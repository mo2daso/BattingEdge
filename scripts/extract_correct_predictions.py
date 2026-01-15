"""
Script 1 (Flat Folder Version): Extract Predictions from Test Folder
Processes a flat 'test' folder (no subfolders), runs prediction, and extracts valid results.

Usage: python 1_extract_correct_predictions_flat.py
"""
import sys
import shutil
from pathlib import Path
from tqdm import tqdm

# Add backend to path
sys.path.insert(0, str(Path.cwd() / "backend"))

try:
    from inference import StackingEnsembleClassifier
except ImportError:
    print("❌ Error: Could not import 'inference'. Make sure you are in the root directory.")
    sys.exit(1)

# ==========================================
# CONFIGURATION
# ==========================================
# Update this to your actual flat video folder
TEST_FOLDER = Path("test")  
OUTPUT_DIR = Path("dataset")

# Video extensions to process
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

# List of known classes to check against filenames (Optional)
KNOWN_CLASSES = ['cover', 'pull', 'cut', 'sweep', 'defense', 'drive', 'flick', 'hook', 'lofted', 'square', 'straight']

# ==========================================
# MAIN SCRIPT
# ==========================================

def main():
    print("=" * 80)
    print("STEP 1: PREDICT VIDEOS IN FLAT FOLDER")
    print("=" * 80)
    
    # Check test folder exists
    if not TEST_FOLDER.exists():
        print(f"\n❌ ERROR: Test folder not found at {TEST_FOLDER.absolute()}")
        print(f"   Please create the folder or update TEST_FOLDER in the script.")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n✅ Output directory: {OUTPUT_DIR.absolute()}")
    
    # Load model
    print(f"\n⏳ Loading model...")
    try:
        classifier = StackingEnsembleClassifier()
        mode = "Ensemble" if classifier.is_ensemble else "BiLSTM"
        print(f"   ✅ Model loaded: {mode}")
    except Exception as e:
        print(f"   ❌ Model load failed: {e}")
        return
    
    # Collect all videos
    print(f"\n⏳ Scanning '{TEST_FOLDER.name}'...")
    all_videos = [f for f in TEST_FOLDER.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS]
    
    print(f"   ✅ Found {len(all_videos)} videos")
    
    if len(all_videos) == 0:
        print(f"\n❌ No videos found! Add .mp4/.avi files to the '{TEST_FOLDER}' folder.")
        return
    
    # Process videos
    print(f"\n⏳ Processing videos...")
    print("-" * 80)
    
    results = []
    processed_count = 0
    error_count = 0
    
    for video_path in tqdm(all_videos, desc="Analyzing"):
        try:
            # Run prediction
            result = classifier.predict_video(str(video_path))
            
            if 'error' in result:
                error_count += 1
                results.append({
                    'video': video_path.name,
                    'prediction': 'ERROR',
                    'confidence': 0,
                    'error': result['error']
                })
                continue
            
            predicted_class = result['prediction']
            confidence = result['confidence']
            
            # --- VERIFICATION LOGIC ---
            # Since we don't have labeled folders, we check if the filename contains the predicted class.
            # Example: "cover_drive_01.mp4" contains "cover", so prediction "cover drive" is likely correct.
            filename_lower = video_path.stem.lower()
            prediction_lower = predicted_class.lower()
            
            # Simple check: Is the prediction roughly in the filename?
            # Splits prediction "cover drive" -> ["cover", "drive"] and checks if any part matches.
            pred_parts = prediction_lower.split()
            is_match = any(part in filename_lower for part in pred_parts if len(part) > 2)
            
            # If filename is generic (e.g. "video1.mp4"), we can't verify, so we default to True or mark as Unknown.
            # Here we assume if it's not a match, we still keep it but flag it.
            status = "MATCH" if is_match else "UNKNOWN/MISMATCH"
            
            processed_count += 1
            
            # Copy to output directory
            # We rename it to include the prediction for clarity: "pred_cover_drive_video1.mp4"
            clean_pred_name = predicted_class.replace(" ", "_")
            new_filename = f"pred_{clean_pred_name}_{video_path.name}"
            output_path = OUTPUT_DIR / new_filename
            
            shutil.copy2(video_path, output_path)
            
            results.append({
                'video': video_path.name,
                'prediction': predicted_class,
                'confidence': confidence,
                'status': status
            })
            
        except Exception as e:
            error_count += 1
            results.append({
                'video': video_path.name,
                'prediction': 'EXCEPTION',
                'confidence': 0,
                'error': str(e)
            })
    
    # ==========================================
    # SUMMARY
    # ==========================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total = len(all_videos)
    print(f"\nTotal Videos: {total}")
    print(f"   ✅ Successfully Processed: {processed_count}")
    print(f"   ⚠️  Errors:                 {error_count}")
    
    print(f"\n📁 Videos copied to: {OUTPUT_DIR.absolute()}")
    print("-" * 80)
    print(f"{'Video Name':<30s} {'Prediction':<20s} {'Conf':<8s} {'Filename Match?'}")
    print("-" * 80)
    
    for r in results:
        if 'error' not in r:
            match_icon = "✅" if r['status'] == "MATCH" else "❓"
            print(f"{r['video'][:28]:<30s} {r['prediction']:<20s} {r['confidence']:<6.1f}%   {match_icon} {r['status']}")
        else:
            print(f"{r['video'][:28]:<30s} ❌ ERROR: {r['error']}")
            
    print("-" * 80)
    
    # Save log
    import json
    log_file = Path("test_folder_predictions.json")
    with open(log_file, 'w') as f:
        json.dump({'summary': {'total': total, 'processed': processed_count}, 'details': results}, f, indent=2)
    
    print(f"\n💾 Log saved to: {log_file.absolute()}")
    print("\n" + "=" * 80)
    print(f"✅ STEP 1 COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()