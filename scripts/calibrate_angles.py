"""
BattingEdge Calibration Tool
Measures 'Ground Truth' angles from the dataset to calibrate grading rules.
"""
import sys
import random
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import mediapipe as mp
import cv2  # <--- Moved import to top level to fix NameError

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

try:
    from inference import calculate_dot_product_angle, calculate_planar_angle
except ImportError:
    print("❌ Critical Error: Could not import backend.inference")
    sys.exit(1)

# CONFIG
DATASET_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP\dataset")
SAMPLES_PER_CLASS = 10  # 50 total videos
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
    
    # Analyze the IMPACT frame (middle of sequence)
    # We take the middle 20% of frames and average them to be robust
    mid = len(frames) // 2
    # Ensure window indices are valid
    start_idx = max(0, mid - 2)
    end_idx = min(len(frames), mid + 3)
    window = frames[start_idx:end_idx] 
    
    metrics = {
        'elbow_angle': [], 'front_knee': [], 'bat_angle': [], 
        'hip_rotation': [], 'back_lift': [], 'head_drift': []
    }
    
    # Calculate Movement (Full Sequence)
    nose_y = [p[0].y for p in frames]
    metrics['head_drift'] = (max(nose_y) - min(nose_y)) * HEIGHT_SCALE
    metrics['back_lift'] = abs(frames[0][28].y - min([p[28].y for p in frames])) * HEIGHT_SCALE
    
    # Calculate Angles (Impact Window)
    for lm in window:
        try:
            # 1. Elbow
            l_elb = calculate_dot_product_angle(lm[11], lm[13], lm[15])
            metrics['elbow_angle'].append(l_elb)
            
            # 2. Knee
            l_knee = calculate_dot_product_angle(lm[23], lm[25], lm[27])
            metrics['front_knee'].append(l_knee)
            
            # 3. Bat
            bat = abs(calculate_planar_angle(lm[16], lm[12]))
            metrics['bat_angle'].append(bat)
            
            # 4. Hip
            hip = abs(calculate_planar_angle(lm[24], lm[23]))
            metrics['hip_rotation'].append(hip)
            
        except: pass
        
    # Return averages
    return {
        'elbow_angle': np.mean(metrics['elbow_angle']) if metrics['elbow_angle'] else 0,
        'front_knee': np.mean(metrics['front_knee']) if metrics['front_knee'] else 0,
        'bat_angle': np.mean(metrics['bat_angle']) if metrics['bat_angle'] else 0,
        'hip_rotation': np.mean(metrics['hip_rotation']) if metrics['hip_rotation'] else 0,
        'head_drift': metrics['head_drift'],
        'back_lift': metrics['back_lift']
    }

def main():
    print("="*60)
    print("📏 BATTINGEDGE CALIBRATION RUN")
    print("="*60)
    
    # 1. Collect Data
    data = []
    classes = ['Cover Drive', 'Pull Shot', 'Cut Shot', 'Sweep Shot', 'Defense']
    
    search_paths = [DATASET_DIR]
    for sub in ['train', 'test', 'val']:
        if (DATASET_DIR / sub).exists(): search_paths.append(DATASET_DIR / sub)

    for cls in classes:
        videos = []
        for d in search_paths:
            target = d / cls
            if not target.exists():
                # Try finding case-insensitive
                for child in d.iterdir():
                    if child.is_dir() and child.name.lower() == cls.lower():
                        target = child
                        break
            if target and target.exists():
                videos.extend(list(target.glob("*.mp4")))
        
        if not videos:
            print(f"⚠️ No videos for {cls}")
            continue
            
        # Select random samples
        samples = random.sample(videos, min(len(videos), SAMPLES_PER_CLASS))
        
        print(f"\nProcessing {len(samples)} videos for {cls}...")
        for vid in tqdm(samples):
            res = get_metrics_from_video(vid)
            if res:
                res['class'] = cls
                res['video'] = vid.name
                data.append(res)

    if not data:
        print("❌ No data collected.")
        return

    # 2. Analyze & Print Report
    df = pd.DataFrame(data)
    try:
        df.to_csv("calibration_data.csv", index=False)
    except:
        print("⚠️ Could not save CSV (file might be open), continuing...")
    
    print("\n" + "="*80)
    print(f"{'SHOT TYPE':<15} | {'METRIC':<15} | {'MIN':<6} | {'AVG':<6} | {'MAX':<6} | {'STD':<6}")
    print("="*80)
    
    for cls in classes:
        subset = df[df['class'] == cls]
        if subset.empty: continue
        
        print(f"\n--- {cls.upper()} ({len(subset)} samples) ---")
        
        for metric in ['elbow_angle', 'front_knee', 'bat_angle', 'hip_rotation', 'head_drift']:
            vals = subset[metric]
            print(f"{'':<15} | {metric:<15} | {vals.min():.1f}   | {vals.mean():.1f}   | {vals.max():.1f}   | {vals.std():.1f}")

    print("\n" + "="*80)
    print("✅ Calibration complete. Paste this output into the chat.")
    print("="*80)

if __name__ == "__main__":
    main()