import os
import cv2
import numpy as np
import mediapipe as mp
import joblib
import tensorflow as tf
from xgboost import XGBClassifier
import shutil
from pathlib import Path
from tqdm import tqdm

# ================= CONFIGURATION =================
BASE_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP")
DATASET_DIR = BASE_DIR / "dataset"  # Root dataset folder
OUTPUT_DIR  = BASE_DIR / "v9_5_test_results"  # Output folder

MODEL_DIR = BASE_DIR / "backend" / "models"

# Paths
SCALER_PATH = MODEL_DIR / "scaler_V9_5.pkl"
CLASSES_PATH = MODEL_DIR / "classes_V9_5.pkl"
LSTM_PATH = MODEL_DIR / "battingedge_V9_5_best.keras"
XGB_PATH  = MODEL_DIR / "battingedge_V9_5_xgboost_best.json"
RF_PATH   = MODEL_DIR / "battingedge_V9_5_random_forest_best.pkl"
META_PATH = MODEL_DIR / "battingedge_V9_5_meta_model.pkl"

SEQUENCE_LENGTH = 50
mp_pose = mp.solutions.pose

# ================= 1. LOAD MODELS =================
print("Loading Ensemble Models...")

try:
    scaler = joblib.load(SCALER_PATH)
    classes = joblib.load(CLASSES_PATH)
    lstm_model = tf.keras.models.load_model(LSTM_PATH)
    
    xgb_model = XGBClassifier()
    xgb_model.load_model(XGB_PATH)
    
    rf_model = joblib.load(RF_PATH)
    meta_model = joblib.load(META_PATH)
    
    print("✅ All models loaded successfully.")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    exit()

# ================= 2. FEATURE EXTRACTION =================
def get_angle(landmarks, a, b, c):
    """Calculates angle between three landmarks a, b, c"""
    try:
        p1 = np.array([landmarks[a].x, landmarks[a].y])
        p2 = np.array([landmarks[b].x, landmarks[b].y])
        p3 = np.array([landmarks[c].x, landmarks[c].y])
        
        radians = np.arctan2(p3[1]-p2[1], p3[0]-p2[0]) - np.arctan2(p1[1]-p2[1], p1[0]-p2[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle
    except:
        return 0.0

def extract_features_from_video(video_path):
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    
    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # 1. Raw Coordinates (33*3 = 99 features)
                pose_row = []
                for lm in landmarks:
                    pose_row.extend([lm.x, lm.y, lm.z])
                
                # 2. Angles (8 features)
                angles = [
                    get_angle(landmarks, 11, 13, 15), # Left Elbow
                    get_angle(landmarks, 12, 14, 16), # Right Elbow
                    get_angle(landmarks, 11, 23, 25), # Left Hip
                    get_angle(landmarks, 12, 24, 26), # Right Hip
                    get_angle(landmarks, 23, 25, 27), # Left Knee
                    get_angle(landmarks, 24, 26, 28), # Right Knee
                    get_angle(landmarks, 11, 12, 23), # Shoulder-Hip
                    get_angle(landmarks, 23, 24, 25)  # Stance
                ]
                
                # Combine
                feature_vector = np.array(pose_row + angles)
                frames.append(feature_vector)
            
            if len(frames) >= SEQUENCE_LENGTH:
                break
                
    cap.release()
    
    # Handle lengths
    if len(frames) == 0:
        return None
    
    # Pad if too short
    while len(frames) < SEQUENCE_LENGTH:
        frames.append(frames[-1])
            
    return np.array(frames)

# ================= 3. PREDICTION LOGIC =================
def predict_video(features):
    # Prepare Inputs
    N, F = features.shape
    
    # Scale (Using the single scaler for everything)
    features_scaled = scaler.transform(features)
    
    # Input 1: 3D for LSTM (1, 50, 107)
    X_3d = features_scaled.reshape(1, 50, 107)
    
    # Input 2: 2D Flat for RF/XGB (1, 5350)
    X_2d = features_scaled.reshape(1, 5350)
    
    # Get Individual Predictions
    p_lstm = lstm_model.predict(X_3d, verbose=0)
    p_xgb  = xgb_model.predict_proba(X_2d)
    p_rf   = rf_model.predict_proba(X_2d)
    
    # Stack for Meta-Model
    meta_input = np.hstack([p_lstm, p_xgb, p_rf]) 
    
    # Final Decision
    final_prob = meta_model.predict_proba(meta_input)[0]
    pred_idx = np.argmax(final_prob)
    
    return classes[pred_idx], final_prob[pred_idx]

# ================= 4. MAIN LOOP (Updated for Train/Test/Val) =================
print("\n🚀 STARTING FULL DATASET TEST")
print(f"Source: {DATASET_DIR}")
print(f"Output: {OUTPUT_DIR}\n")

stats = {"Total": 0, "Correct": 0, "Incorrect": 0}
subsets = ['train', 'test', 'val']  # <--- CHECK ALL SUBFOLDERS

for subset in subsets:
    subset_path = DATASET_DIR / subset
    if not subset_path.exists():
        continue
        
    print(f"📂 Scanning subset: {subset.upper()}")
    
    for class_name in classes:
        class_dir = subset_path / class_name
        if not class_dir.exists():
            continue
            
        videos = list(class_dir.glob("*.mp4"))
        print(f"   Processing {class_name} ({len(videos)} videos)...")
        
        for video_file in tqdm(videos, leave=False):
            stats["Total"] += 1
            
            # Extract
            features = extract_features_from_video(video_file)
            if features is None:
                continue
                
            # Predict
            pred_class, conf = predict_video(features)
            
            # Verify
            is_correct = (pred_class == class_name)
            
            # Sort Files
            if is_correct:
                stats["Correct"] += 1
                # Output/Correct/Cover Drive/video.mp4
                dest_folder = OUTPUT_DIR / "Correct" / class_name
            else:
                stats["Incorrect"] += 1
                # Output/Incorrect/True_CoverDrive/Pred_CutShot/video.mp4
                dest_folder = OUTPUT_DIR / "Incorrect" / f"True_{class_name}" / f"Pred_{pred_class}"
                
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy file with prefix to avoid duplicates from different subsets
            new_name = f"{subset}_{video_file.name}"
            shutil.copy(str(video_file), str(dest_folder / new_name))

# ================= 5. REPORT =================
print("\n" + "="*50)
print("TEST COMPLETED")
print("="*50)

if stats['Total'] > 0:
    acc = (stats['Correct'] / stats['Total']) * 100
    err = (stats['Incorrect'] / stats['Total']) * 100
    
    print(f"Total Videos: {stats['Total']}")
    print(f"Correct:      {stats['Correct']} ({acc:.2f}%)")
    print(f"Incorrect:    {stats['Incorrect']} ({err:.2f}%)")
    print(f"\n✅ Results saved to: {OUTPUT_DIR}")
else:
    print("❌ No videos found! Check your dataset path.")