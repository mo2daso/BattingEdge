"""
Groq Vision analysis for cricket batting shot validation and enhanced grading.
Uses the official `groq` Python SDK (sync client) — called directly from the
sync background task in main.py without any asyncio wrapper.
"""
import os
import cv2
import base64
import json
import copy
import logging

from groq import Groq

logger = logging.getLogger("GroqVision")

GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = (
    "You are an expert cricket batting coach with 20 years of experience. "
    "Analyze the provided sequential frames from a cricket batting video "
    "and respond ONLY with valid JSON, no markdown, no explanation."
)

USER_PROMPT = (
    "Analyze these 5 sequential frames from a cricket batting video.\n"
    "Return ONLY this JSON structure with no other text:\n"
    "{\n"
    '  "cricket_shot_detected": true or false,\n'
    '  "predicted_shot": one of exactly: "cover drive", "pull shot", '
    '"straight drive", "cut shot", "defensive shot", or "none",\n'
    '  "bat_visible": true or false,\n'
    '  "full_body_visible": true or false,\n'
    '  "technique_quality": one of exactly: "poor", "average", "good", "excellent",\n'
    '  "technique_score": number between 0 and 100,\n'
    '  "coaching_observation": "one specific sentence about the most important technical aspect visible",\n'
    '  "key_strength": "one specific strength visible in the shot",\n'
    '  "key_improvement": "one specific thing to improve",\n'
    '  "groq_confidence": one of exactly: "low", "medium", "high"\n'
    "}"
)


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Frame extraction
# ──────────────────────────────────────────────────────────────────────────────

def extract_key_frames(video_path, start_time=None, end_time=None):
    """
    Extract 5 frames at 20/35/50/65/80% of the active window.
    Respects start_time/end_time (seconds) so trimmed videos sample
    within the trim window, not across the full original file.
    Returns list of base64-encoded JPEG strings.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return []

    fps          = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    start_frame = int(start_time * fps) if (start_time and start_time > 0) else 0
    end_frame   = int(end_time   * fps) if end_time else total_frames
    end_frame   = min(end_frame, total_frames)
    window      = end_frame - start_frame

    if window < 10:
        cap.release()
        return []

    frames_b64 = []
    for pos in [0.20, 0.35, 0.50, 0.65, 0.80]:
        frame_idx = start_frame + int(window * pos)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue

        # Resize to max width 512 px (maintains aspect ratio)
        h, w = frame.shape[:2]
        if w > 512:
            frame = cv2.resize(frame, (512, int(h * 512 / w)))

        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frames_b64.append(base64.b64encode(buf.tobytes()).decode('utf-8'))

    cap.release()
    return frames_b64


# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — Groq Vision API call (sync, 14-second timeout)
# ──────────────────────────────────────────────────────────────────────────────

def _extract_first_json_object(text):
    """
    Return the substring spanning the first complete {...} block.
    Handles extra text / commentary that the model appends after the JSON.
    Falls back to the original string if no braces found.
    """
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == '{':
            if start is None:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i + 1]
    return text  # let json.loads produce the real error if still malformed


def analyze_with_groq_vision(video_path, ml_prediction, ml_confidence,
                             start_time=None, end_time=None):
    """
    Send 5 key frames to Groq Vision and return parsed JSON dict.
    start_time/end_time (seconds) are forwarded to extract_key_frames so
    trimmed videos sample within the trim window only.
    Returns None on any failure — caller always falls back to ML-only result.
    """
    try:
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — skipping vision analysis")
            return None

        frames = extract_key_frames(video_path, start_time=start_time, end_time=end_time)
        if not frames:
            logger.warning("No frames extracted — skipping vision analysis")
            return None

        # Build multimodal content: text prompt first, then one image block per frame
        content = [{"type": "text", "text": USER_PROMPT}]
        for b64 in frames:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        # Groq SDK sync client — timeout applies to the whole HTTP round-trip
        client = Groq(api_key=GROQ_API_KEY, timeout=14.0)

        completion = client.chat.completions.create(
            model=GROQ_VISION_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": content},
            ],
            temperature=0.1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        raw = completion.choices[0].message.content.strip()

        # Strip markdown fences if model wraps in ```json ... ```
        if raw.startswith("```"):
            lines = raw.split('\n')
            inner = lines[1:] if len(lines) > 1 else lines
            if inner and inner[-1].strip().startswith('```'):
                inner = inner[:-1]
            raw = '\n'.join(inner).strip()

        # Extract the first complete JSON object (handles trailing text / extra data)
        raw = _extract_first_json_object(raw)

        parsed = json.loads(raw)
        # Model sometimes wraps response in a JSON array — unwrap it
        if isinstance(parsed, list) and parsed:
            parsed = parsed[0]
        return parsed if isinstance(parsed, dict) else None

    except Exception as exc:
        logger.warning(f"Groq Vision failed (non-fatal): {exc}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 — Result merging
# ──────────────────────────────────────────────────────────────────────────────

def _normalize_shot(label):
    """Lower-case, strip underscores/hyphens for loose shot-name matching."""
    return (label or '').lower().replace('_', ' ').replace('-', ' ').strip()


def merge_results(ml_result, groq_result):
    """
    Merge ML inference result with Groq Vision result.

    All Groq fields are stored *inside* form_analysis so they persist
    automatically via the existing form_checks DB column — no schema change.

    groq_result = None  →  return ML result unchanged (groq_available=False)
    cricket_shot_detected = False  →  return error dict (triggers failed status)
    """
    # ── Groq unavailable / timed out ──────────────────────────────────────
    if groq_result is None:
        result = copy.deepcopy(ml_result)
        fa = result.get('form_analysis', {})
        fa['groq_available'] = False
        result['form_analysis'] = fa
        return result

    # ── No cricket shot visible ────────────────────────────────────────────
    # Groq's rejection is only trusted when groq_confidence is "high".
    # If ML is >= 25% confident, trust ML over Groq's rejection regardless.
    # The ML model always classifies into one of 5 shots with no "none" class.
    groq_confidence = groq_result.get('groq_confidence', '').lower()
    if not groq_result.get('cricket_shot_detected', True):
        ml_conf = ml_result.get('confidence', 0)
        if isinstance(ml_conf, str):
            ml_conf = float(ml_conf.replace('%', '')) / 100
        elif ml_conf > 1:          # already a percentage like 64.8
            ml_conf = ml_conf / 100

        if ml_conf >= 0.25:
            # ML has enough confidence — use ML result, flag Groq disagreement
            result = copy.deepcopy(ml_result)
            fa = result.get('form_analysis', {})
            fa['groq_available']      = True
            fa['ai_verified']         = False
            fa['ai_validation_label'] = 'AI Assisted'
            fa['note']     = 'AI Vision uncertain — ML model prediction used'
            fa['bat_warning'] = (
                'AI Vision could not confirm shot in frames — result based on pose analysis'
            )
            result['form_analysis'] = fa
            return result
        else:
            return {
                'error': (
                    'No cricket shot detected. Please record yourself playing a '
                    'batting shot with full body visible.'
                ),
                'groq_available':        True,
                'cricket_shot_detected': False,
            }

    result = copy.deepcopy(ml_result)

    # ── Score blending (ML 60 % + Groq 40 %) ──────────────────────────────
    ml_score   = result.get('form_analysis', {}).get('overall_score', 0)
    groq_score = groq_result.get('technique_score', ml_score)
    enhanced   = round(ml_score * 0.6 + groq_score * 0.4)

    # ── Shot agreement ─────────────────────────────────────────────────────
    # Groq only overrides ML verification when groq_confidence is "high" —
    # prevents low-movement shots (e.g. defensive) from being incorrectly rejected.
    ml_shot   = _normalize_shot(result.get('prediction', ''))
    groq_shot = (
        _normalize_shot(groq_result.get('predicted_shot', ''))
        .replace('defensive shot', 'defense')
        .replace('defensive',      'defense')
    )
    ml_norm = ml_shot.replace('_', ' ')
    shots_agree = ml_norm == groq_shot or ml_norm in groq_shot or groq_shot in ml_norm
    # Only mark as AI-verified when Groq is high-confidence AND shots agree.
    # If Groq confidence is not "high", treat as AI Assisted regardless of shot match.
    ai_verified = shots_agree and groq_confidence == 'high'
    # Note: ML prediction is never overridden — Groq shot names don't match ML class labels
    # (e.g. Groq returns "defensive shot" / "straight drive" which aren't ML classes).
    # Disagreement is flagged via ai_verified=False; ML label is always the one shown.

    # ── Update form_analysis ───────────────────────────────────────────────
    fa = result.get('form_analysis', {})
    fa['overall_score'] = enhanced

    if   enhanced >= 90: fa['performance_level'] = 'Elite'
    elif enhanced >= 80: fa['performance_level'] = 'Advanced'
    elif enhanced >= 70: fa['performance_level'] = 'Proficient'
    elif enhanced >= 60: fa['performance_level'] = 'Developing'
    elif enhanced >= 50: fa['performance_level'] = 'Beginner'
    else:                fa['performance_level'] = 'Needs Work'

    if   enhanced >= 90: fa['grade'] = 'A+'
    elif enhanced >= 85: fa['grade'] = 'A'
    elif enhanced >= 80: fa['grade'] = 'A-'
    elif enhanced >= 75: fa['grade'] = 'B+'
    elif enhanced >= 70: fa['grade'] = 'B'
    elif enhanced >= 65: fa['grade'] = 'B-'
    elif enhanced >= 60: fa['grade'] = 'C+'
    elif enhanced >= 55: fa['grade'] = 'C'
    else:                fa['grade'] = 'D'

    # ── Embed all Groq fields in form_analysis (persisted in DB) ──────────
    fa['groq_available']       = True
    fa['ai_verified']          = ai_verified
    fa['ai_validation_label']  = 'AI Vision Verified' if ai_verified else 'AI Assisted'
    fa['coaching_observation'] = groq_result.get('coaching_observation', '')
    fa['key_strength']         = groq_result.get('key_strength', '')
    fa['key_improvement']      = groq_result.get('key_improvement', '')
    fa['technique_quality']    = groq_result.get('technique_quality', '')
    fa['bat_warning'] = (
        'Bat not clearly visible — results based on body movement only'
        if not groq_result.get('bat_visible', True) else None
    )
    fa['body_warning'] = (
        'Full body not visible — for best results ensure whole body is in frame'
        if not groq_result.get('full_body_visible', True) else None
    )

    result['form_analysis'] = fa
    return result
