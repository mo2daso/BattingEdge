"""
Script 3: Automated Overlay Validator & MOVER (Queue System)
Checks if overlay videos have:
1. Green YOLO box around batsman
2. MediaPipe skeleton detected
3. Proper alignment (skeleton inside box)

- Uses Early Exit: Stops checking if 5 consecutive frames are perfect.
- MOVES valid videos to 'BE_VIDEOS' (Removing them from source).
- This allows you to run the script repeatedly on new batches.

Usage:
    python 3_validate_and_move.py --input_dir "D:/Users/Anoshia/BattingEdge_FYP/best_dataset"
"""

import cv2
import numpy as np
from pathlib import Path
import argparse
import csv
import shutil
import time
from tqdm import tqdm
import mediapipe as mp

# Try importing YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ YOLO not available. Box detection will be skipped.")

mp_pose = mp.solutions.pose

class OverlayValidator:
    def __init__(self, use_yolo=True):
        self.use_yolo = use_yolo and YOLO_AVAILABLE
        if self.use_yolo:
            try:
                self.yolo = YOLO('yolov8n.pt')
                # Suppress YOLO logging
                self.yolo.predictor = None 
                print("✅ YOLO loaded for validation")
            except:
                self.yolo = None
                self.use_yolo = False
                print("⚠️ YOLO load failed")
        
    def validate_video(self, video_path):
        """
        Validates a single video with Early Exit optimization.
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            return {
                'filename': video_path.name,
                'path': video_path,
                'status': 'FAIL',
                'issues': ['Cannot open video file']
            }
        
        w = int(cap.get(3))
        h = int(cap.get(4))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames_with_box = 0
        frames_with_pose = 0
        frames_with_aligned_pose = 0
        issues = []
        
        # Optimization: Check roughly every 5% of the video (max 20 checks total)
        frame_sample_rate = max(1, total_frames // 20) 
        
        consecutive_good_frames = 0
        early_exit_triggered = False
        
        with mp_pose.Pose(min_detection_confidence=0.5) as pose:
            frame_idx = 0
            checked_frames = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip frames
                if frame_idx % frame_sample_rate != 0:
                    frame_idx += 1
                    continue
                
                checked_frames += 1
                
                # 1. YOLO Check
                person_box = None
                box_found = False
                
                if self.use_yolo and self.yolo is not None:
                    try:
                        results = self.yolo(frame, verbose=False)
                        boxes = results[0].boxes.data.cpu().numpy()
                        # Filter for person (class 0) with conf > 0.4
                        person_boxes = [b for b in boxes if int(b[5]) == 0 and b[4] > 0.4]
                        
                        if len(person_boxes) > 0:
                            frames_with_box += 1
                            box_found = True
                            # Get largest box
                            best_box = max(person_boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
                            x1, y1, x2, y2 = map(int, best_box[:4])
                            person_box = (x1, y1, x2, y2)
                    except Exception:
                        pass
                else:
                    box_found = True

                # 2. MediaPipe Check
                res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                pose_found = False
                aligned = False
                
                if res.pose_landmarks:
                    frames_with_pose += 1
                    pose_found = True
                    
                    # 3. Alignment Check
                    if person_box is not None:
                        x1, y1, x2, y2 = person_box
                        nose = res.pose_landmarks.landmark[0]
                        nose_x = int(nose.x * w)
                        nose_y = int(nose.y * h)
                        
                        # Relaxed boundary check
                        if (x1 - 50) <= nose_x <= (x2 + 50) and (y1 - 50) <= nose_y <= (y2 + 200):
                            frames_with_aligned_pose += 1
                            aligned = True
                    elif not self.use_yolo:
                        aligned = True 
                
                # Logic for Good Frame
                if pose_found and (not self.use_yolo or (box_found and aligned)):
                    consecutive_good_frames += 1
                else:
                    consecutive_good_frames = 0 
                
                # === EARLY EXIT ===
                if consecutive_good_frames >= 5:
                    early_exit_triggered = True
                    break
                
                frame_idx += 1
        
        cap.release()
        
        # Results Logic
        if early_exit_triggered:
            return {
                'filename': video_path.name,
                'status': 'PASS',
                'issues': 'None'
            }
        else:
            denom = checked_frames if checked_frames > 0 else 1
            pose_rate = (frames_with_pose / denom) * 100
            box_rate = (frames_with_box / denom) * 100
            align_rate = (frames_with_aligned_pose / denom) * 100
            
            status = 'PASS'
            if pose_rate < 50:
                status = 'FAIL'
                issues.append(f'Low pose ({pose_rate:.0f}%)')
            
            if self.use_yolo:
                if box_rate < 50:
                    status = 'WARNING' if status == 'PASS' else 'FAIL'
                    issues.append(f'Low box ({box_rate:.0f}%)')
                
                if align_rate < 40 and box_rate > 50:
                    status = 'FAIL'
                    issues.append(f'Misaligned ({align_rate:.0f}%)')
        
            return {
                'filename': video_path.name,
                'status': status,
                'issues': '; '.join(issues) if issues else 'None'
            }

def validate_and_move(input_dir, output_folder_name="BE_VIDEOS"):
    """
    Validates videos. 
    - If VALID: MOVES to output folder (deletes from source).
    - If FAIL: Leaves in source folder (so you can inspect/retry).
    """
    input_path = Path(input_dir)
    output_dir = input_path.parent / output_folder_name
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_path}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 Output Queue: {output_dir}")
    
    video_exts = {'.mp4', '.avi', '.mov', '.webm', '.mkv'}
    video_files = [p for p in input_path.glob('*') if p.suffix.lower() in video_exts]
    
    if not video_files:
        print(f"❌ No videos found in {input_dir}")
        return
    
    print(f"🔍 Processing Queue: {len(video_files)} videos...")
    print("=" * 70)
    
    validator = OverlayValidator(use_yolo=True)
    results = []
    moved_count = 0
    
    for video_file in tqdm(video_files, desc="Validating & Moving"):
        try:
            res = validator.validate_video(video_file)
            results.append(res)
            
            # --- MOVE LOGIC ---
            if res['status'] in ['PASS', 'WARNING']:
                dest_path = output_dir / video_file.name
                
                # Handle name collision
                if dest_path.exists():
                    timestamp = int(time.time())
                    dest_path = output_dir / f"{video_file.stem}_{timestamp}{video_file.suffix}"
                
                # MOVE (Copy + Delete)
                shutil.move(str(video_file), str(dest_path))
                moved_count += 1
                
        except Exception as e:
            print(f"❌ Error on {video_file.name}: {e}")
            
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    warnings = sum(1 for r in results if r['status'] == 'WARNING')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    print(f"Total Processed: {len(results)}")
    print(f"✅ Passed:       {passed}")
    print(f"⚠️  Warnings:     {warnings} (Moved)")
    print(f"❌ Failed:       {failed} (Left in Source)")
    print("-" * 30)
    print(f"🚀 Total Moved to '{output_folder_name}': {moved_count}")
    print(f"📉 Remaining in Source: {len(video_files) - moved_count}")
    
    # Save Report
    report_file = output_dir / "validation_report.csv"
    with open(report_file, 'a', newline='') as f:  # Append mode 'a'
        writer = csv.DictWriter(f, fieldnames=['filename', 'status', 'issues'])
        if f.tell() == 0: writer.writeheader()
        writer.writerows([{k: v for k, v in r.items() if k in ['filename', 'status', 'issues']} for r in results])
    
    print(f"📄 Log updated: {report_file.name}")

if __name__ == '__main__':
    DEFAULT_INPUT = r"D:\Users\Anoshia\BattingEdge_FYP\best_dataset"
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default=DEFAULT_INPUT)
    args = parser.parse_args()
    
    validate_and_move(args.input_dir)