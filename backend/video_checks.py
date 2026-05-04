"""
Pre-inference video quality checks for BattingEdge.
All functions are fast (frame-sampling only) and non-blocking —
failures return a warning string, never raise.
"""
import cv2
import logging

logger = logging.getLogger("VideoChecks")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _open_window(video_path, start_time, end_time):
    """Return (cap, start_frame, window_size) or None on failure."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None, 0, 0
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    sf    = int(start_time * fps) if (start_time and start_time > 0) else 0
    ef    = min(int(end_time * fps) if end_time else total, total)
    return cap, sf, ef - sf


# ─────────────────────────────────────────────────────────────────────────────
# Feature 3 — Motion detection
# ─────────────────────────────────────────────────────────────────────────────

def check_motion(video_path, start_time=None, end_time=None):
    """
    Sample 6 frames across the active window and measure inter-frame pixel diff.
    Returns (has_motion: bool, warning: str | None).
    Mean diff < 4.0 → person is standing still.
    """
    cap, start_frame, window = _open_window(video_path, start_time, end_time)
    if cap is None or window < 5:
        if cap:
            cap.release()
        return True, None  # can't check → don't block

    prev_gray = None
    diffs = []
    for pos in [0.15, 0.30, 0.45, 0.60, 0.75, 0.90]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame + int(window * pos))
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(cv2.resize(frame, (160, 120)), cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            diffs.append(float(cv2.absdiff(gray, prev_gray).mean()))
        prev_gray = gray
    cap.release()

    if not diffs:
        return True, None

    avg = sum(diffs) / len(diffs)
    logger.info(f"Motion check: avg_diff={avg:.2f}")

    if avg < 4.0:
        return False, (
            "No significant movement detected — please record an actual "
            "batting shot with your full body in motion."
        )
    return True, None


# ─────────────────────────────────────────────────────────────────────────────
# Feature 2 — Pose completeness
# ─────────────────────────────────────────────────────────────────────────────

def check_pose_completeness(video_path, start_time=None, end_time=None):
    """
    Run MediaPipe Pose on 3 frames from the active window and take the best
    landmark visibility ratio.  ratio < 0.5 → body not fully visible warning.
    Returns (ratio: float, warning: str | None).
    """
    try:
        import mediapipe as mp
    except ImportError:
        return 1.0, None

    cap, start_frame, window = _open_window(video_path, start_time, end_time)
    if cap is None or window < 5:
        if cap:
            cap.release()
        return 1.0, None

    frames = []
    for pos in [0.35, 0.50, 0.65]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame + int(window * pos))
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()

    if not frames:
        return 1.0, None

    best = 0.0
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.3) as pose:
        for frame in frames:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)
            if res.pose_landmarks:
                lms = res.pose_landmarks.landmark
                visible = sum(1 for lm in lms if lm.visibility > 0.5)
                best = max(best, visible / len(lms))

    logger.info(f"Pose completeness: best_ratio={best:.2f}")

    if best < 0.5:
        return best, (
            "Full body not clearly visible — ensure the camera captures your "
            "whole body from head to feet for most accurate results."
        )
    return best, None


# ─────────────────────────────────────────────────────────────────────────────
# Feature 5 — Auto-trim: detect active shot window
# ─────────────────────────────────────────────────────────────────────────────

def auto_detect_trim(video_path):
    """
    Called only when the user did NOT manually trim.
    Samples 24 frames, computes inter-frame motion, finds the active window
    where motion exceeds 30 % of peak, pads by 0.5 s on each side.
    Returns (start_sec, end_sec) or (None, None) if no clear window found.
    Only applied when the detected window is < 80 % of total duration
    (i.e. would actually trim something meaningful).
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None, None

    fps   = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < 30:
        cap.release()
        return None, None

    duration  = total / fps
    SAMPLES   = 24
    prev_gray = None
    motion    = []  # (time_sec, score)

    for i in range(SAMPLES):
        pos = i / (SAMPLES - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * pos))
        ret, frame = cap.read()
        t = total * pos / fps
        if not ret:
            motion.append((t, 0.0))
            prev_gray = None
            continue
        gray = cv2.cvtColor(cv2.resize(frame, (160, 120)), cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            motion.append((t, float(cv2.absdiff(gray, prev_gray).mean())))
        else:
            motion.append((t, 0.0))
        prev_gray = gray

    cap.release()

    scores = [s for _, s in motion]
    peak   = max(scores)
    if peak < 3.0:
        return None, None  # video has no meaningful motion at all

    threshold = peak * 0.30
    active    = [(t, s) for t, s in motion if s >= threshold]
    if not active:
        return None, None

    t_start = max(0.0,      active[0][0]  - 0.5)
    t_end   = min(duration, active[-1][0] + 0.5)

    if (t_end - t_start) >= duration * 0.80:
        return None, None  # shot spans most of the video — no useful trim

    logger.info(f"Auto-trim detected: {t_start:.1f}s → {t_end:.1f}s (of {duration:.1f}s total)")
    return t_start, t_end
