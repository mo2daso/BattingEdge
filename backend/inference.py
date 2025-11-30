import sys
import cv2
import numpy as np
import tensorflow as tf
import joblib
import logging
from pathlib import Path
from ultralytics import YOLO
import mediapipe as mp

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
SEQUENCE_LENGTH = 50
FEATURES_DIM = 103

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Inference")

# Initialize Shared Models
yolo_model = YOLO('yolov8n.pt')

mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Landmark Indices
NOSE = 0
LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
LEFT_ELBOW, RIGHT_ELBOW = 13, 14
LEFT_WRIST, RIGHT_WRIST = 15, 16
LEFT_HIP, RIGHT_HIP = 23, 24
LEFT_KNEE, RIGHT_KNEE = 25, 26
LEFT_ANKLE, RIGHT_ANKLE = 27, 28
LEFT_FOOT_INDEX, RIGHT_FOOT_INDEX = 31, 32

# ==========================================
# 2. BIOMECHANICS & SUMMARY ENGINE
# ==========================================
class BiomechanicsAnalyzer:
    def __init__(self):
        self.height_scale = 175.0

    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0: angle = 360 - angle
        return angle

    def analyze(self, landmarks_seq, shot_type):
        checks = []
        score = 100

        if not landmarks_seq:
            return {"overall_score": 0, "checks": [], "summary": "No pose data detected."}

        impact_idx = len(landmarks_seq) // 2
        start_frame = landmarks_seq[0]
        impact_frame = landmarks_seq[impact_idx]
        final_frame = landmarks_seq[-1]

        # 1. FRONT ELBOW
        s, e, w = impact_frame[12][:2], impact_frame[14][:2], impact_frame[16][:2]
        elbow_angle = self.calculate_angle(s, e, w)
        c1 = {"name": "Elbow", "value": f"{int(elbow_angle)}°", "is_error": False}
        if elbow_angle < 110:
            c1["is_error"] = True; score -= 15
        checks.append(c1)

        # 2. HEAD STABILITY
        nose_y = [f[0][1] for f in landmarks_seq]
        drift = (max(nose_y) - min(nose_y)) * self.height_scale
        c2 = {"name": "Head", "value": f"{int(drift)}cm", "is_error": False}
        if drift > 15:
            c2["is_error"] = True; score -= 20
        checks.append(c2)

        # 3. BACK FOOT
        lift = (start_frame[28][1] - min([f[28][1] for f in landmarks_seq])) * self.height_scale
        c3 = {"name": "BackFoot", "value": f"{int(lift)}cm", "is_error": False}
        if lift > 10:
            c3["is_error"] = True; score -= 15
        checks.append(c3)

        # 4. HIP ROTATION
        def hip_ang(f):
            return np.degrees(np.arctan2(f[24][1]-f[23][1], f[24][0]-f[23][0]))
        rot = abs(hip_ang(start_frame) - hip_ang(impact_frame))
        thresh = 60 if shot_type == 'pull' else 30
        c4 = {"name": "Hips", "value": f"{int(rot)}°", "is_error": False}
        if rot < (thresh - 10):
            c4["is_error"] = True; score -= 20
        checks.append(c4)

        # 5. FOLLOW THROUGH
        high_hands = (final_frame[12][1] - final_frame[16][1]) * self.height_scale
        c5 = {"name": "Finish", "value": "High" if high_hands > 0 else "Low", "is_error": False}
        if high_hands < -5:
            c5["is_error"] = True; score -= 20
        checks.append(c5)

        # --- SUMMARY LOGIC ---
        final_score = max(0, score)
        if final_score >= 85:
            summary_text = "Pro-level form! Excellent mechanics."
        elif final_score >= 60:
            summary_text = "Good form with minor technical adjustments needed."
        else:
            summary_text = "Form needs significant correction on stability and timing."

        return {
            "overall_score": int(final_score),
            "checks": checks,
            "summary": summary_text
        }

# ==========================================
# 3. FEATURE EXTRACTION (FULL FRAME)
# ==========================================
def extract_features_full_frame(video_path):
    """
    Extracts features using FULL FRAME (No Crop).
    This ensures coordinates match the training data exactly.
    """
    cap = cv2.VideoCapture(str(video_path))
    skeleton, biomech, raw_lms = [], [], []

    while True:
        ret, frame = cap.read()
        if not ret: break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose_model.process(rgb)

        if not res.pose_landmarks: continue
        lms = res.pose_landmarks.landmark

        raw_lms.append([(float(lm.x), float(lm.y), float(lm.z)) for lm in lms])

        pose_vec = []
        for lm in lms: pose_vec.extend([float(lm.x), float(lm.y), float(lm.z)])
        skeleton.append(pose_vec)

        # Biomech calc
        lw, rw = np.array([lms[15].x, lms[15].y], dtype=np.float32), np.array([lms[16].x, lms[16].y], dtype=np.float32)
        ls, rs = np.array([lms[11].x, lms[11].y], dtype=np.float32), np.array([lms[12].x, lms[12].y], dtype=np.float32)
        lf, rf = np.array([lms[31].x, lms[31].y], dtype=np.float32), np.array([lms[32].x, lms[32].y], dtype=np.float32)

        wrist_vel = 0.0
        if len(biomech) > 0:
            p_lw, p_rw = biomech[-1][0], biomech[-1][1]
            wrist_vel = float(max(np.linalg.norm(lw - p_lw), np.linalg.norm(rw - p_rw)))

        shoulder_vec = rs - ls
        wrist_vec = rw - lw
        bat_angle = float(np.dot(shoulder_vec, wrist_vec))
        stance = float(np.linalg.norm(lf - rf))

        biomech.append([lw, rw, wrist_vel, 180.0, bat_angle, stance])

    cap.release()
    if not skeleton: return None, 0, None

    X = np.array(skeleton, dtype=np.float32)
    B = np.array([[b[2], b[3], b[4], b[5]] for b in biomech], dtype=np.float32)
    return np.concatenate([X, B], axis=1), len(skeleton), raw_lms

def resample(X, target=SEQUENCE_LENGTH):
    if X is None: return None
    T, D = X.shape
    if T == target: return X
    out = np.zeros((target, D), dtype=np.float32)
    src = np.arange(T)
    dst = np.linspace(0, T-1, target)
    for d in range(D): out[:, d] = np.interp(dst, src, X[:, d])
    return out

def resample_raw(raw, target=SEQUENCE_LENGTH):
    if not raw: return []
    indices = np.linspace(0, len(raw)-1, target).astype(int)
    return [raw[i] for i in indices]

# ==========================================
# 4. CLASSIFIER CLASS
# ==========================================
class CricketShotClassifier:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.model_dir = self.base_dir / "models"
        self.model_path = self.model_dir / "shot_model_V8p_best.keras"
        self.scaler_path = self.model_dir / "shot_scaler_V8p.pkl"
        self.encoder_path = self.model_dir / "shot_encoder_V8p.pkl"

        self.biomech = BiomechanicsAnalyzer()
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose_drawer = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1)

        self._load()

    def _load(self):
        if not self.model_path.exists():
            logger.error(f"Missing: {self.model_path}"); sys.exit(1)
        try:
            self.model = tf.keras.models.load_model(str(self.model_path))
            self.scaler = joblib.load(self.scaler_path)
            self.encoder = joblib.load(self.encoder_path)
            self.classes = self.encoder.classes_
            logger.info("✅ Model Loaded")
        except Exception as e:
            logger.error(f"Load Error: {e}"); sys.exit(1)

    def predict_video(self, video_path):
        video_path = Path(video_path)
        if not video_path.exists():
            return {
                "error": "File not found",
                "form_analysis": {"overall_score": 0, "checks": [], "summary": "Error: file missing"}
            }

        # 1. Extract (Full Frame)
        feat, frames, raw_lms = extract_features_full_frame(video_path)
        if feat is None:
            return {
                "error": "No pose detected",
                "form_analysis": {"overall_score": 0, "checks": [], "summary": "No pose detected"}
            }

        # 2. Predict
        feat_50 = resample(feat)
        feat_flat = feat_50.reshape(-1, FEATURES_DIM)
        feat_scaled = self.scaler.transform(feat_flat)
        feat_final = feat_scaled.reshape(1, SEQUENCE_LENGTH, FEATURES_DIM)

        preds = self.model.predict(feat_final, verbose=0)[0]
        top_idx = int(np.argmax(preds))
        pred_class = str(self.classes[top_idx])
        conf = float(preds[top_idx] * 100.0)

        all_probs = {str(self.classes[i]): float(preds[i] * 100.0) for i in range(len(self.classes))}

        # 3. Analyze
        raw_50 = resample_raw(raw_lms)
        form = self.biomech.analyze(raw_50, pred_class)
        if "summary" not in form:
            form["summary"] = "No summary available"

        # Cast frames to int
        frames = int(frames)

        return {
            "prediction": pred_class,
            "confidence": conf,
            "all_probabilities": all_probs,
            "frames": frames,
            "form_analysis": form
        }

    def create_overlay(self, input_path, output_path, result_data):
        cap = cv2.VideoCapture(str(input_path))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        out = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

        GREEN = (0, 255, 0); RED = (0, 0, 255); YELLOW = (0, 255, 255); BLACK = (0, 0, 0); WHITE = (255, 255, 255)

        # Optional focus box (visual aid)
        lock_box = None
        for _ in range(10):
            ret, frame = cap.read()
            if not ret: break
            # Keep UI simple: skip YOLO box if noisy. Uncomment to enable:
            # lock_box = get_batsman_box(frame)
            # if lock_box: break
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        frame_num = 0
        impact_range = range(int(total_frames/2) - 2, int(total_frames/2) + 3)

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_num += 1

            # 1. Full-frame skeleton
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.pose_drawer.process(rgb)
            if res.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=RED, thickness=3, circle_radius=3),
                    self.mp_drawing.DrawingSpec(color=GREEN, thickness=2)
                )

            # 2. Impact flash
            if frame_num in impact_range:
                cv2.rectangle(frame, (0, 0), (width, height), YELLOW, 10)
                cv2.putText(frame, "IMPACT", (width//2 - 100, height//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, YELLOW, 5)

            # 3. HUD
            overlay = frame.copy()

            # Classification
            conf = float(result_data['confidence'])
            bg = GREEN if conf > 70 else (YELLOW if conf > 50 else RED)
            cv2.rectangle(overlay, (20, 20), (350, 110), bg, -1)
            cv2.putText(overlay, result_data['prediction'].upper(), (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, BLACK, 3)
            cv2.putText(overlay, f"{conf:.1f}% Confidence", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 1)

            # Form score
            score = int(result_data['form_analysis']['overall_score'])
            s_col = GREEN if score > 80 else (YELLOW if score > 60 else RED)
            center = (width - 80, 70)
            cv2.circle(overlay, center, 50, (50, 50, 50), -1)
            cv2.putText(overlay, str(score), (center[0]-25, center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 1.2, WHITE, 3)
            cv2.putText(overlay, "FORM", (center[0]-25, center[1]+40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1)

            # Checks
            bar_y = height - 70
            cv2.rectangle(overlay, (0, height-100), (width, height), BLACK, -1)
            checks = result_data['form_analysis']['checks']
            spacing = max(1, width // max(1, len(checks)+1))
            for i, c in enumerate(checks):
                x = 20 + (i * spacing)
                col = RED if c['is_error'] else GREEN
                icon = "X" if c['is_error'] else "OK"
                cv2.putText(overlay, f"{icon} {c['name']}", (x, bar_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
                cv2.putText(overlay, str(c['value']), (x, bar_y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)

            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            out.write(frame)

        cap.release()
        out.release()
        return True

if __name__ == "__main__":
    pass
