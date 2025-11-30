import cv2
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
import logging

# Configuration
SEQUENCE_LENGTH = 50
FEATURES_DIM = 103 

logger = logging.getLogger("FeatureExtractor")

# Initialize Models
mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1, 
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# YOLO for Initial Detection
yolo_model = YOLO('yolov8n.pt')

# Landmark Indices
LW, RW = 15, 16
LS, RS = 11, 12
LK, RK = 25, 26
LA, RA = 27, 28
LF, RF = 31, 32

def get_initial_batsman_box(frame):
    """
    Scans the FIRST frame to find the batsman (Tallest + Central).
    Returns the coordinates (x1, y1, x2, y2) to LOCK onto.
    """
    height, width, _ = frame.shape
    center_x = width // 2
    
    results = yolo_model(frame, verbose=False, classes=[0, 34]) # Person + Bat
    
    best_box = None
    max_score = -1

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            box_h = y2 - y1
            box_w = x2 - x1
            
            # 1. Aspect Ratio (Tall is better)
            aspect_ratio = box_h / (box_w + 1e-6)
            
            # 2. Centrality
            box_center = (x1 + x2) // 2
            dist_score = 1.0 - (abs(center_x - box_center) / width)
            
            # 3. Class (Bat bonus)
            cls_bonus = 20 if int(box.cls[0]) == 34 else 0
            
            score = (aspect_ratio * 2.0) + dist_score + cls_bonus
            
            if score > max_score:
                max_score = score
                best_box = (x1, y1, x2, y2)

    return best_box

def extract_pose_features(video_path):
    cap = cv2.VideoCapture(str(video_path))
    skeleton_seq = []
    biomech_seq = []
    
    # --- STEP 1: LOCK ONTO BATSMAN ---
    # We read the first few frames to find the best lock
    locked_box = None
    frames_checked = 0
    
    while frames_checked < 10: # Check first 10 frames
        ret, frame = cap.read()
        if not ret: break
        frames_checked += 1
        
        found_box = get_initial_batsman_box(frame)
        if found_box:
            locked_box = found_box
            break
    
    # Reset video to start
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # If no batsman found, use full frame
    if not locked_box:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        locked_box = (0, 0, width, height)

    # Add generous padding to the lock (so they don't move out of it)
    lx1, ly1, lx2, ly2 = locked_box
    frame_h, frame_w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    pad_w = int((lx2 - lx1) * 0.4) # 40% width padding
    pad_h = int((ly2 - ly1) * 0.3) # 30% height padding
    
    # Final Fixed Crop Coordinates
    crop_x1 = max(0, lx1 - pad_w)
    crop_y1 = max(0, ly1 - pad_h)
    crop_x2 = min(frame_w, lx2 + pad_w)
    crop_y2 = min(frame_h, ly2 + pad_h)

    # --- STEP 2: PROCESS VIDEO WITH LOCKED CROP ---
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # CROP TO THE LOCKED REGION
        if crop_x2 > crop_x1 and crop_y2 > crop_y1:
            frame_roi = frame[crop_y1:crop_y2, crop_x1:crop_x2]
        else:
            frame_roi = frame
        
        # Pose Estimation
        rgb = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2RGB)
        res = pose_model.process(rgb)
        
        if not res.pose_landmarks: continue
        
        lms = res.pose_landmarks.landmark
        
        # Extract 99 Skeleton Features
        pose_vec = []
        for lm in lms:
            pose_vec.extend([lm.x, lm.y, lm.z])
        skeleton_seq.append(pose_vec)

        # Extract 4 Biomechanical Features
        lw = np.array([lms[LW].x, lms[LW].y])
        rw = np.array([lms[RW].x, lms[RW].y])
        ls = np.array([lms[LS].x, lms[LS].y])
        rs = np.array([lms[RS].x, lms[RS].y])
        lk = np.array([lms[LK].x, lms[LK].y])
        lf, rf = np.array([lms[LF].x, lms[LF].y]), np.array([lms[RF].x, lms[RF].y])

        wrist_vel = 0.0
        if len(biomech_seq) > 0:
            prev_lw, prev_rw = biomech_seq[-1][:2]
            wrist_vel = max(np.linalg.norm(lw - prev_lw), np.linalg.norm(rw - prev_rw))

        knee_angle = 180.0 
        shoulder_vec = rs - ls
        wrist_vec = rw - lw
        bat_angle = np.dot(shoulder_vec, wrist_vec) 
        stance = np.linalg.norm(lf - rf)

        biomech_seq.append([lw, rw, wrist_vel, knee_angle, bat_angle, stance])

    cap.release()

    if len(skeleton_seq) == 0:
        return None, 0

    X = np.array(skeleton_seq, dtype=np.float32)
    B = np.array([[b[2], b[3], b[4], b[5]] for b in biomech_seq], dtype=np.float32)
    
    X_plus = np.concatenate([X, B], axis=1)
    return X_plus, len(skeleton_seq)

def resample_sequence(X, target_len=SEQUENCE_LENGTH):
    if X is None: return None
    T, D = X.shape
    if T == target_len: return X
    src_idx = np.arange(T)
    dst_idx = np.linspace(0, T-1, target_len)
    out = np.zeros((target_len, D), dtype=np.float32)
    for d in range(D):
        out[:, d] = np.interp(dst_idx, src_idx, X[:, d])
    return out