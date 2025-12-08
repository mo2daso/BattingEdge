import os
import sys
import cv2
import numpy as np
import tensorflow as tf
import joblib
import random
import logging
import math
from pathlib import Path
from ultralytics import YOLO
import mediapipe as mp

# ==========================================
# 1. CONFIGURATION
# ==========================================
SEQUENCE_LENGTH = 50
FEATURES_DIM = 103 

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Inference")

# Initialize Models
yolo_model = YOLO('yolov8n.pt')

mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1, 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ==========================================
# 2. COACHING INTELLIGENCE (Humanized)
# ==========================================
COACHING_ADVICE = {
    "Elbow": {
        "good": "Perfect! Your arms are fully extended, giving you maximum power.",
        "minor": "Good shot, but try to reach out a little more towards the ball.",
        "major": "Your arms are too close to your body ('Chicken Wing'). Try to extend your hands towards the bowler!"
    },
    "Head": {
        "good": "Excellent focus! Your head stayed perfectly still.",
        "minor": "Your head dropped a little bit. Try to keep your chin up.",
        "major": "Your head is falling over. Imagine balancing a glass of water on your helmet—keep it steady!"
    },
    "BackFoot": {
        "good": "Great balance! Your feet stayed planted.",
        "minor": "Your back heel lifted a bit early. Try to keep it grounded longer.",
        "major": "You are jumping at the ball! Keep your back foot stuck to the ground to generate more power."
    },
    "Hips": {
        "good": "Amazing power! You used your hips perfectly.",
        "minor": "Try to twist your hips a little faster to hit the ball harder.",
        "major": "You are using only your arms. Turn your belt buckle towards the bowler to unlock your real power!"
    },
    "Finish": {
        "good": "Beautiful high finish! That's a textbook shot.",
        "minor": "Your hands finished a bit low. Try to swing through the line of the ball.",
        "major": "You stopped your swing too early. Throw your hands high over your shoulder like a pro!"
    }
}

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
        improvements = []
        score = 100
        
        if not landmarks_seq: 
            return {"overall_score": 0, "checks": [], "key_improvements": [], "summary": "No data"}
        
        impact_idx = len(landmarks_seq) // 2 
        start_frame = landmarks_seq[0]
        impact_frame = landmarks_seq[impact_idx]
        final_frame = landmarks_seq[-1]

        # 1. FRONT ELBOW
        s, e, w = impact_frame[12][:2], impact_frame[14][:2], impact_frame[16][:2]
        elbow_angle = self.calculate_angle(s, e, w)
        severity = "good"
        if elbow_angle < 110: severity = "major"; score -= 15
        elif elbow_angle < 120: severity = "minor"; score -= 5
        
        checks.append({
            "name": "Front Elbow Extension", 
            "value": f"{int(elbow_angle)}°", 
            "ideal": "120° - 140°",  # <--- NEW FIELD
            "is_error": severity != "good", 
            "advice": COACHING_ADVICE["Elbow"][severity]
        })
        if severity != "good": improvements.append(COACHING_ADVICE["Elbow"][severity])

        # 2. HEAD STABILITY
        nose_y = [f[0][1] for f in landmarks_seq]
        drift = (max(nose_y) - min(nose_y)) * self.height_scale
        severity = "good"
        if drift > 15: severity = "major"; score -= 20
        elif drift > 10: severity = "minor"; score -= 10
        
        checks.append({
            "name": "Head Stability", 
            "value": f"{int(drift)}cm drift", 
            "ideal": "< 10cm movement", # <--- NEW FIELD
            "is_error": severity != "good", 
            "advice": COACHING_ADVICE["Head"][severity]
        })
        if severity != "good": improvements.append(COACHING_ADVICE["Head"][severity])

        # 3. BACK FOOT
        lift = (start_frame[28][1] - min([f[28][1] for f in landmarks_seq])) * self.height_scale
        severity = "good"
        if lift > 10: severity = "major"; score -= 15
        elif lift > 5: severity = "minor"; score -= 5
        
        checks.append({
            "name": "Back Foot Stability", 
            "value": f"{int(lift)}cm lift", 
            "ideal": "< 5cm lift", # <--- NEW FIELD
            "is_error": severity != "good", 
            "advice": COACHING_ADVICE["BackFoot"][severity]
        })
        if severity != "good": improvements.append(COACHING_ADVICE["BackFoot"][severity])

        # 4. HIP ROTATION
        def hip_ang(f): return np.degrees(np.arctan2(f[24][1]-f[23][1], f[24][0]-f[23][0]))
        rot = abs(hip_ang(start_frame) - hip_ang(impact_frame))
        thresh = 60 if shot_type == 'pull' else 30
        
        severity = "good"
        if rot < (thresh - 15): severity = "major"; score -= 20
        elif rot < thresh: severity = "minor"; score -= 10
        
        checks.append({
            "name": "Hip Rotation", 
            "value": f"{int(rot)}°", 
            "ideal": f"> {thresh}°", # <--- DYNAMIC FIELD
            "is_error": severity != "good", 
            "advice": COACHING_ADVICE["Hips"][severity]
        })
        if severity != "good": improvements.append(COACHING_ADVICE["Hips"][severity])

        # 5. FOLLOW THROUGH
        high_hands = (final_frame[12][1] - final_frame[16][1]) * self.height_scale
        severity = "good"
        if high_hands < -5: severity = "major"; score -= 20
        elif high_hands < 0: severity = "minor"; score -= 5
        
        checks.append({
            "name": "Follow Through", 
            "value": "High" if high_hands > 0 else "Low", 
            "ideal": "Hands > Shoulders", # <--- NEW FIELD
            "is_error": severity != "good", 
            "advice": COACHING_ADVICE["Finish"][severity]
        })
        if severity != "good": improvements.append(COACHING_ADVICE["Finish"][severity])

        final_score = max(0, score)
        if final_score >= 85: summary = "Pro-level form! Minimal adjustments needed."
        elif final_score >= 70: summary = "Good technique. Focus on the key improvements below."
        else: summary = "Needs work on fundamentals to improve stability."

        return {
            "overall_score": final_score, 
            "checks": checks,
            "key_improvements": improvements,
            "summary": summary
        }

# ==========================================
# 3. EXTRACTION & OVERLAY
# ==========================================
def get_initial_batsman_box(frame):
    height, width, _ = frame.shape
    center_x = width // 2
    results = yolo_model(frame, verbose=False, classes=[0, 34])
    best_box, max_score = None, -1
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            aspect_ratio = (y2 - y1) / ((x2 - x1) + 1e-6)
            dist_score = 1.0 - (abs(center_x - ((x1+x2)//2)) / width)
            cls_bonus = 20 if int(box.cls[0]) == 34 else 0
            score = (aspect_ratio * 2.0) + dist_score + cls_bonus
            if score > max_score:
                max_score = score
                best_box = (x1, y1, x2, y2)
    return best_box

def extract_features_full_frame(video_path):
    cap = cv2.VideoCapture(str(video_path))
    skeleton, biomech, raw_lms = [], [], []
    while True:
        ret, frame = cap.read()
        if not ret: break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose_model.process(rgb)
        if not res.pose_landmarks: continue
        lms = res.pose_landmarks.landmark
        raw_lms.append([(lm.x, lm.y, lm.z) for lm in lms])
        pose_vec = []
        for lm in lms: pose_vec.extend([lm.x, lm.y, lm.z])
        skeleton.append(pose_vec)
        # Biomech
        lw, rw = np.array([lms[15].x, lms[15].y]), np.array([lms[16].x, lms[16].y])
        ls, rs = np.array([lms[11].x, lms[11].y]), np.array([lms[12].x, lms[12].y])
        lf, rf = np.array([lms[31].x, lms[31].y]), np.array([lms[32].x, lms[32].y])
        wrist_vel = 0.0
        if len(biomech) > 0:
            p_lw, p_rw = biomech[-1][:2]
            wrist_vel = max(np.linalg.norm(lw-p_lw), np.linalg.norm(rw-p_rw))
        shoulder_vec = rs - ls
        wrist_vec = rw - lw
        bat_angle = np.dot(shoulder_vec, wrist_vec) 
        stance = np.linalg.norm(lf - rf)
        biomech.append([lw, rw, wrist_vel, 180.0, bat_angle, stance])
    cap.release()
    if not skeleton: return None, 0, None
    X = np.array(skeleton, dtype=np.float32)
    B = np.array([[b[2], b[3], b[4], b[5]] for b in biomech], dtype=np.float32)
    return np.concatenate([X, B], axis=1), len(skeleton), raw_lms

def resample_sequence(X, target_len=SEQUENCE_LENGTH):
    if X is None: return None
    T, D = X.shape
    if T == target_len: return X
    out = np.zeros((target_len, D), dtype=np.float32)
    src, dst = np.arange(T), np.linspace(0, T-1, target_len)
    for d in range(D): out[:, d] = np.interp(dst, src, X[:, d])
    return out

def resample_raw(raw, target=50):
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
            logger.info("✅ V8p Model Loaded Successfully")
        except Exception as e:
            logger.error(f"Load Error: {e}"); sys.exit(1)

    def predict_video(self, video_path):
        video_path = Path(video_path)
        if not video_path.exists(): return {"error": "File not found"}

        feat, frames, raw_lms = extract_features_full_frame(video_path)
        if feat is None: return {"error": "No pose detected"}

        feat_50 = resample_sequence(feat)
        feat_flat = feat_50.reshape(-1, FEATURES_DIM)
        feat_scaled = self.scaler.transform(feat_flat)
        feat_final = feat_scaled.reshape(1, SEQUENCE_LENGTH, FEATURES_DIM)

        preds = self.model.predict(feat_final, verbose=0)[0]
        top_idx = np.argmax(preds)
        pred_class = self.classes[top_idx]
        conf = preds[top_idx] * 100
        all_probs = {self.classes[i]: float(preds[i])*100 for i in range(len(self.classes))}
        raw_50 = resample_raw(raw_lms)
        form = self.biomech.analyze(raw_50, pred_class)

        return {
            "prediction": pred_class,
            "confidence": conf,
            "all_probabilities": all_probs,
            "frames": frames,
            "form_analysis": form
        }

    def create_overlay(self, input_path, output_path, result_data):
        cap = cv2.VideoCapture(str(input_path))
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps, total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            if not out.isOpened(): raise Exception
        except:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        GREEN, RED, YELLOW, BLACK, WHITE = (0, 255, 0), (0, 0, 255), (0, 255, 255), (0, 0, 0), (255, 255, 255)
        
        locked_box = None
        for _ in range(10):
            ret, frame = cap.read()
            if not ret: break
            locked_box = get_initial_batsman_box(frame)
            if locked_box: break
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        frame_num = 0
        impact_window = range(int(total/2)-2, int(total/2)+3)

        while True:
            ret, frame = cap.read()
            if not ret: break
            frame_num += 1

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.pose_drawer.process(rgb)
            if res.pose_landmarks:
                self.mp_drawing.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=RED, thickness=3, circle_radius=3),
                    self.mp_drawing.DrawingSpec(color=GREEN, thickness=2))
            
            if frame_num in impact_window:
                cv2.rectangle(frame, (0,0), (width, height), YELLOW, 10)
                cv2.putText(frame, "IMPACT", (width//2 - 100, height//2), cv2.FONT_HERSHEY_SIMPLEX, 2, YELLOW, 5)

            overlay = frame.copy()
            cv2.rectangle(overlay, (20, 20), (350, 100), BLACK, -1)
            cv2.putText(overlay, result_data['prediction'].upper(), (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 2)
            cv2.putText(overlay, f"Score: {result_data['form_analysis']['overall_score']}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 1)

            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            out.write(frame)

        cap.release()
        out.release()
        return True

if __name__ == "__main__":
    pass