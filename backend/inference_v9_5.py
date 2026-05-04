import os
import sys
import cv2
import numpy as np
import tensorflow as tf
import joblib
import logging
from pathlib import Path
from xgboost import XGBClassifier
import mediapipe as mp
from shot_rules import ShotRules

# ==========================================
# CONFIGURATION
# ==========================================
SEQUENCE_LENGTH = 50
FEATURES_DIM = 107
HEIGHT_SCALE = 175.0 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EnsembleInference")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# ==========================================
# YOLO IMPORT (OPTIONAL - ONLY FOR OVERLAY)
# ==========================================
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("⚠️ ultralytics not installed. YOLO box will be disabled.")

# ==========================================
# GEOMETRY FUNCTIONS (UNCHANGED - YOUR LOGIC)
# ==========================================
def calculate_dot_product_angle(a, b, c):
    """3D Dot Product Angle (0-180) - Matches Training Logic for Limbs"""
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    
    ba = a - b
    bc = c - b
    
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return angle

def calculate_planar_angle(a, b):
    """2D Orientation Angle (Arctan2) - Matches Training Logic for Body"""
    return np.degrees(np.arctan2(a.y - b.y, a.x - b.x))

# ==========================================
# BIOMECHANICS ANALYZER (UNCHANGED)
# ==========================================
class BiomechanicsAnalyzer:
    def __init__(self):
        self.height_scale = HEIGHT_SCALE

    def analyze(self, landmarks_seq, shot_type):
        if not landmarks_seq or len(landmarks_seq) < 3:
            return self._get_empty_analysis("Insufficient data")
        
        # Key Frames (YOUR LOGIC - UNCHANGED)
        start = landmarks_seq[0]
        impact = landmarks_seq[len(landmarks_seq) // 2]
        
        metrics = {}
        try:
            # 1. ANGLES (YOUR LOGIC - UNCHANGED)
            metrics['elbow_angle'] = calculate_dot_product_angle(impact[12], impact[14], impact[16])
            metrics['front_knee'] = calculate_dot_product_angle(impact[23], impact[25], impact[27])
            
            # 2. ORIENTATION (YOUR LOGIC - UNCHANGED)
            metrics['bat_angle'] = abs(calculate_planar_angle(impact[16], impact[12]))
            
            # 3. MOVEMENT (YOUR LOGIC - UNCHANGED)
            nose_y = [p.y for p in landmarks_seq]
            metrics['head_drift'] = (max(nose_y) - min(nose_y)) * self.height_scale
            metrics['back_lift'] = abs(start[28].y - min([p.y for p in landmarks_seq])) * self.height_scale
            
            # 4. ROTATION (YOUR LOGIC - UNCHANGED)
            hip_start = calculate_planar_angle(start[24], start[23])
            hip_end = calculate_planar_angle(impact[24], impact[23])
            metrics['hip_rotation'] = abs(hip_end - hip_start)
            
            # 5. BOOLEANS (YOUR LOGIC - UNCHANGED)
            metrics['wrist_above_elbow'] = impact[16].y < impact[14].y
            metrics['head_over_ball'] = abs(impact[0].x - impact[25].x) < 0.1
            metrics['weight_forward'] = abs(impact[0].x - impact[27].x) < abs(impact[0].x - impact[28].x)
            metrics['front_foot_forward'] = abs(impact[27].x - start[27].x) > 0.05
            metrics['backlift'] = metrics['back_lift']

        except:
            pass

        # Call new analyze_shot
        grading = ShotRules.analyze_shot(metrics, shot_type)
        
        # Handle new ShotRules output format
        checks = []
        for check_item in grading.get('checks', []):
            checks.append({
                "name": check_item.get('name', 'Metric'),
                "value": check_item.get('value', 'N/A'),
                "ideal_range": check_item.get('ideal_range', 'N/A'),
                "status": check_item.get('status', 'Unknown'),
                "is_error": check_item.get('is_error', False),
                "advice": check_item.get('advice', 'Keep practicing.')
            })

        return {
            "overall_score": grading.get('overall_score', 70),
            "performance_level": grading.get('performance_level', 'Good'),
            "grade": grading.get('grade', 'B'),
            "checks": checks,
            "key_improvements": grading.get('key_improvements', []),
            "strengths": grading.get('strengths', []),
            "summary": grading.get('summary', f"Analysis for {shot_type}"),
            "recommended_drills": grading.get('recommended_drills', []),
            "detailed_metrics": metrics
        }

    def _get_empty_analysis(self, reason):
        return {
            "overall_score": 0,
            "performance_level": "N/A",
            "grade": "F",
            "checks": [],
            "summary": reason,
            "key_improvements": [],
            "strengths": [],
            "recommended_drills": []
        }

# ==========================================
# ENSEMBLE CLASSIFIER (UNCHANGED)
# ==========================================
class StackingEnsembleClassifier:
    def __init__(self):
        self.base = Path(__file__).parent
        self.models = self.base / "models"
        
        try:
            self.scaler = joblib.load(self.models / "scaler_V9_5.pkl")
            self.classes = joblib.load(self.models / "classes_V9_5.pkl")
            if hasattr(self.classes, 'classes_'):
                self.classes = self.classes.classes_
            
            self.lstm_model = tf.keras.models.load_model(str(self.models / "battingedge_V9_5_best.keras"))
            
            try:
                self.xgb_model = XGBClassifier()
                self.xgb_model.load_model(self.models / "battingedge_V9_5_xgboost_best.json")
                self.rf_model = joblib.load(self.models / "battingedge_V9_5_random_forest_best.pkl")
                self.meta_model = joblib.load(self.models / "battingedge_V9_5_meta_model.pkl")
                if hasattr(self.meta_model, 'multi_class'):
                    delattr(self.meta_model, 'multi_class')
                self.is_ensemble = True
                logger.info("✅ Ensemble Loaded")
            except:
                self.is_ensemble = False
                logger.warning("⚠️ Ensemble missing. Using BiLSTM.")
                
            self.analyzer = BiomechanicsAnalyzer()
            
            # Load YOLO only if available (for overlay visualization only)
            if YOLO_AVAILABLE:
                try:
                    self.yolo = YOLO('yolov8n.pt')
                    logger.info("✅ YOLO loaded for overlay tracking")
                except:
                    self.yolo = None
                    logger.warning("⚠️ YOLO load failed")
            else:
                self.yolo = None
            
        except Exception as e:
            logger.error(f"Init Error: {e}")
            sys.exit(1)

    def extract_features(self, video_path, start_time=None, end_time=None):
        """
        YOUR INTERPOLATION LOGIC - UNCHANGED
        CRITICAL: Uses FULL FRAME (no YOLO cropping) to match training
        Optional start_time / end_time (seconds) to analyse only a clip segment.
        """
        cap = cv2.VideoCapture(str(video_path))

        # Seek to start of trim window if provided
        if start_time is not None and start_time > 0:
            cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

        frames, lms = [], []

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                # Stop at end of trim window if provided
                if end_time is not None and cap.get(cv2.CAP_PROP_POS_MSEC) > end_time * 1000:
                    break

                ret, frame = cap.read()
                if not ret:
                    break
                
                res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if res.pose_landmarks:
                    lm = res.pose_landmarks.landmark
                    lms.append(lm)
                    
                    row = [c for p in lm for c in (p.x, p.y, p.z)]
                    try:
                        # YOUR ANGLE CALCULATIONS - UNCHANGED
                        l_elb = calculate_dot_product_angle(lm[11], lm[13], lm[15])
                        r_elb = calculate_dot_product_angle(lm[12], lm[14], lm[16])
                        l_knee = calculate_dot_product_angle(lm[23], lm[25], lm[27])
                        r_knee = calculate_dot_product_angle(lm[24], lm[26], lm[28])
                        
                        shoulder = np.degrees(np.arctan2(lm[12].y - lm[11].y, lm[12].x - lm[11].x))
                        hip = np.degrees(np.arctan2(lm[24].y - lm[23].y, lm[24].x - lm[23].x))
                        bat = np.degrees(np.arctan2(lm[15].y - lm[11].y, lm[15].x - lm[11].x))
                        stance = abs(lm[27].x - lm[28].x)
                        
                        row.extend([l_elb, r_elb, l_knee, r_knee, shoulder, hip, bat, stance])
                        frames.append(np.array(row))
                    except:
                        frames.append(np.array(row + [0]*8))
        
        cap.release()
        if len(frames) < 10:
            return None, None
        
        # YOUR TEMPORAL INTERPOLATION LOGIC - UNCHANGED
        frames = np.array(frames)
        current_len = len(frames)
        target_len = SEQUENCE_LENGTH
        
        if current_len == target_len:
            resampled = frames
        else:
            resampled = np.zeros((target_len, frames.shape[1]))
            x_old = np.linspace(0, current_len - 1, current_len)
            x_new = np.linspace(0, current_len - 1, target_len)
            
            for i in range(frames.shape[1]):
                resampled[:, i] = np.interp(x_new, x_old, frames[:, i])
                
        step = max(1, len(lms) // target_len)
        sampled_lms = lms[::step][:target_len]
        
        return resampled, sampled_lms

    def predict_video(self, video_path, start_time=None, end_time=None):
        """YOUR PREDICTION LOGIC - UNCHANGED"""
        if not Path(video_path).exists():
            return {"error": "File not found"}

        features, lms = self.extract_features(video_path, start_time=start_time, end_time=end_time)
        if features is None:
            return {"error": "No pose detected"}
        
        try:
            X = self.scaler.transform(features)
            
            p_lstm = self.lstm_model.predict(X.reshape(1, 50, 107), verbose=0)[0]
            
            if self.is_ensemble:
                p_xgb = self.xgb_model.predict_proba(X.reshape(1, 5350))[0]
                p_rf = self.rf_model.predict_proba(X.reshape(1, 5350))[0]
                final = self.meta_model.predict_proba(np.hstack([p_lstm, p_xgb, p_rf]).reshape(1, -1))[0]
            else:
                final = p_lstm
                
            idx = np.argmax(final)
            shot = self.classes[idx]
            conf = float(final[idx] * 100)
            
            form = self.analyzer.analyze(lms, shot)
            
            return {
                "prediction": shot,
                "confidence": conf,
                "all_probabilities": {self.classes[i]: float(final[i]*100) for i in range(len(final))},
                "form_analysis": form,
                "filename": Path(video_path).name
            }
        except Exception as e:
            logger.error(f"Predict Error: {e}")
            return {"error": str(e)}

    def create_overlay(self, input_path, output_path, data):
        """
        ===== UPDATED: GREEN BOX + FILTERED SKELETON =====
        Uses YOLO ONLY for visualization (green box around batsman)
        MediaPipe runs on FULL FRAME (no cropping - matches training)
        """
        cap = cv2.VideoCapture(str(input_path))
        w = int(cap.get(3))
        h = int(cap.get(4))
        fps = cap.get(5)
        
        try:
            if str(output_path).endswith('.webm'):
                fourcc = cv2.VideoWriter_fourcc(*'vp80')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
        except: 
            out = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
        
        shot = data['prediction'].upper()
        form = data.get('form_analysis', {})
        score = form.get('overall_score', 0)
        perf_level = form.get('performance_level', 'N/A')
        checks = form.get('checks', [])
        
        # Custom MediaPipe drawing specs (GREEN theme)
        landmark_spec = mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
        connection_spec = mp_drawing.DrawingSpec(color=(0, 220, 0), thickness=2)
        
        with mp_pose.Pose(min_detection_confidence=0.5) as pose:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # ===== STEP 1: YOLO DETECTION (VISUAL BOX ONLY) =====
                best_person_box = None
                if self.yolo is not None:
                    try:
                        results = self.yolo(frame, verbose=False)
                        boxes = results[0].boxes.data.cpu().numpy()
                        person_boxes = [b for b in boxes if int(b[5]) == 0 and b[4] > 0.5]  # class=0 (person), conf>0.5
                        
                        if len(person_boxes) > 0:
                            # Find largest person (likely the batsman, not umpire)
                            best_box = max(person_boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
                            x1, y1, x2, y2 = map(int, best_box[:4])
                            best_person_box = (x1, y1, x2, y2)
                    except Exception as e:
                        logger.warning(f"YOLO detection failed: {e}")
                
                # ===== STEP 2: MEDIAPIPE ON FULL FRAME (NO CROPPING!) =====
                res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # ===== STEP 3: FILTER SKELETON TO ONLY SHOW PERSON IN BOX =====
                if res.pose_landmarks:
                    if best_person_box is not None:
                        # Check if nose (landmark 0) is inside the YOLO box
                        x1, y1, x2, y2 = best_person_box
                        nose = res.pose_landmarks.landmark[0]
                        nose_x = int(nose.x * w)
                        nose_y = int(nose.y * h)
                        
                        # Only draw skeleton if nose is inside the box
                        if x1 <= nose_x <= x2 and y1 <= nose_y <= y2:
                            mp_drawing.draw_landmarks(
                                frame, 
                                res.pose_landmarks, 
                                mp_pose.POSE_CONNECTIONS,
                                landmark_spec,
                                connection_spec
                            )
                            
                            # Draw green box around batsman
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            cv2.putText(frame, "BATSMAN", (x1, y1-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        # Fallback: draw skeleton anyway if YOLO failed
                        mp_drawing.draw_landmarks(
                            frame, 
                            res.pose_landmarks, 
                            mp_pose.POSE_CONNECTIONS,
                            landmark_spec,
                            connection_spec
                        )
                
                # ===== TOP HUD (UNCHANGED) =====
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 140), (10, 14, 26), -1)
                cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
                cv2.rectangle(frame, (0, 0), (w, 140), (255, 229, 0), 3)
                
                cv2.putText(frame, shot, (20, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
                
                if score >= 85:
                    score_color = (16, 185, 129)  # Green
                elif score >= 70:
                    score_color = (255, 229, 0)    # Neon Blue
                elif score >= 55:
                    score_color = (11, 158, 245)   # Orange
                else:
                    score_color = (68, 68, 239)    # Red
                
                cv2.putText(frame, f"SCORE: {score}%", (20, 95), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, score_color, 3)
                cv2.putText(frame, f"Level: {perf_level}", (20, 125), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (148, 163, 184), 2)
                
                # ===== SIDE PANEL (UNCHANGED) =====
                panel_x = w - 350
                panel_y = 20
                panel_w = 330
                panel_h = min(len(checks) * 35 + 70, h - 40)
                
                overlay2 = frame.copy()
                cv2.rectangle(overlay2, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), 
                             (10, 14, 26), -1)
                cv2.addWeighted(overlay2, 0.85, frame, 0.15, 0, frame)
                cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), 
                             (255, 229, 0), 2)
                
                cv2.putText(frame, "BIOMECHANICS", (panel_x + 10, panel_y + 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 229, 0), 2)
                
                y_offset = panel_y + 60
                line_height = 35
                
                for i, check in enumerate(checks[:8]):
                    if y_offset + line_height > panel_y + panel_h - 10:
                        break
                    
                    name = check.get('name', 'Metric')
                    value = check.get('value', 'N/A')
                    status = check.get('status', 'Unknown')
                    
                    if status == 'Excellent':
                        status_color = (16, 185, 129)  # Green
                    elif status == 'Good':
                        status_color = (255, 229, 0)    # Blue
                    elif status == 'Acceptable':
                        status_color = (11, 158, 245)   # Orange
                    else:
                        status_color = (68, 68, 239)    # Red
                    
                    cv2.putText(frame, name[:18], (panel_x + 10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                    
                    value_text = f"{value}"
                    (text_w, text_h), _ = cv2.getTextSize(value_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.putText(frame, value_text, (panel_x + panel_w - text_w - 15, y_offset + 18), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
                    
                    y_offset += line_height
                
                out.write(frame)
        
        cap.release()
        out.release()
        return True