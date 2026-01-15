"""
BattingEdge Percentile Calibration
Finds the 'Elite' standards by looking at the top 20% of shots, not the average.
"""
import sys
import random
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import mediapipe as mp
import cv2

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

try:
    from inference import calculate_dot_product_angle, calculate_planar_angle
except ImportError:
    print("❌ Critical Error: Could not import backend.inference")
    sys.exit(1)

# CONFIG
DATASET_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP\dataset")
SAMPLES_PER_CLASS = 15  # Increased sample size
HEIGHT_SCALE = 175.0

mp_pose = mp.solutions.pose

def get_metrics_from_video(video_path):
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if res.pose_landmarks:
                frames.append(res.pose_landmarks.landmark)
    cap.release()
    
    if len(frames) < 10: return None
    
    # Impact Window (Middle 10 frames)
    mid = len(frames) // 2
    window = frames[mid-5:mid+5]
    
    metrics = {'elbow': [], 'knee': [], 'bat': [], 'hip': []}
    
    # Movement
    nose_y = [p[0].y for p in frames]
    head_drift = (max(nose_y) - min(nose_y)) * HEIGHT_SCALE
    
    for lm in window:
        try:
            # Elbow (Maximize for Drive/Cut, Minimize for Pull?)
            metrics['elbow'].append(calculate_dot_product_angle(lm[11], lm[13], lm[15]))
            # Knee (Maximize = Straight, Minimize = Bent)
            metrics['knee'].append(calculate_dot_product_angle(lm[23], lm[25], lm[27]))
            # Bat (90 is vertical/horizontal depending on view)
            metrics['bat'].append(abs(calculate_planar_angle(lm[16], lm[12])))
            # Hip Rotation
            metrics['hip'].append(abs(calculate_planar_angle(lm[24], lm[23])))
        except: pass
        
    return {
        'elbow': np.mean(metrics['elbow']) if metrics['elbow'] else 0,
        'knee': np.mean(metrics['knee']) if metrics['knee'] else 0,
        'bat': np.mean(metrics['bat']) if metrics['bat'] else 0,
        'hip': np.mean(metrics['hip']) if metrics['hip'] else 0,
        'head_drift': head_drift
    }

def main():
    print("="*60)
    print("📊 PERCENTILE CALIBRATION (Finding the Top 20%)")
    print("="*60)
    
    classes = ['Cover Drive', 'Pull Shot', 'Cut Shot', 'Sweep Shot', 'Defense']
    search_paths = [DATASET_DIR]
    for sub in ['train', 'test', 'val']:
        if (DATASET_DIR / sub).exists(): search_paths.append(DATASET_DIR / sub)

    for cls in classes:
        videos = []
        for d in search_paths:
            target = d / cls
            if not target.exists():
                for child in d.iterdir():
                    if child.is_dir() and child.name.lower() == cls.lower():
                        target = child
                        break
            if target and target.exists():
                videos.extend(list(target.glob("*.mp4")))
        
        if not videos: continue
        
        samples = random.sample(videos, min(len(videos), SAMPLES_PER_CLASS))
        data = []
        
        print(f"\nScanning {cls}...")
        for vid in tqdm(samples):
            res = get_metrics_from_video(vid)
            if res: data.append(res)
            
        if not data: continue
        
        df = pd.DataFrame(data)
        
        print(f"\n--- {cls.upper()} STANDARDS ---")
        
        # 1. ELBOW (Higher is usually better for extension)
        elbow_good = np.percentile(df['elbow'], 75) # Top 25%
        print(f"Elbow Target (>): {elbow_good:.1f}° (Avg was {df['elbow'].mean():.1f})")
        
        # 2. HEAD DRIFT (Lower is better)
        head_good = np.percentile(df['head_drift'], 35) # Bottom 35%
        print(f"Head Drift (<): {head_good:.1f}cm")
        
        # 3. KNEE (Context dependent)
        knee_avg = df['knee'].mean()
        print(f"Front Knee Avg: {knee_avg:.1f}°")
        
        # 4. BAT ANGLE
        bat_avg = df['bat'].mean()
        print(f"Bat Angle Avg:  {bat_avg:.1f}°")

if __name__ == "__main__":
    main()