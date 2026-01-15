"""
Script 2: Extract Best Quality Shots
Processes 'correct_dataset' folder, analyzes biomechanics, 
and copies only videos scoring >70% to 'best_dataset'.

Usage: python 2_extract_best_shots.py
"""
import sys
import json
import shutil
from pathlib import Path
from tqdm import tqdm

# ==========================================
# SETUP PATHS
# ==========================================
# Add backend directory to system path so we can import the model
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir / "backend"))

try:
    from inference import StackingEnsembleClassifier
except ImportError:
    print("❌ ERROR: Could not import 'backend.inference'.")
    print("   Make sure you are running this script from the project root")
    print("   and that the 'backend' folder exists.")
    sys.exit(1)

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_DIR = Path("dataset")      # Source folder
OUTPUT_DIR = Path("best_dataset")        # Destination folder
MIN_SCORE = 70                           # Threshold (70%)
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

def get_unique_filename(destination_dir, filename):
    """
    Ensures we don't overwrite files if names are duplicates.
    If 'video.mp4' exists, returns 'video_1.mp4', 'video_2.mp4', etc.
    """
    file_path = destination_dir / filename
    if not file_path.exists():
        return file_path
    
    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1
    
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = destination_dir / new_filename
        if not new_path.exists():
            return new_path
        counter += 1

def main():
    print("=" * 80)
    print(f"STEP 2: EXTRACT HIGH-QUALITY SHOTS (Score >= {MIN_SCORE}%)")
    print("=" * 80)
    
    # 1. Validation
    if not INPUT_DIR.exists():
        print(f"\n❌ ERROR: Input directory not found: {INPUT_DIR.absolute()}")
        return
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n📂 Input:  {INPUT_DIR}")
    print(f"📂 Output: {OUTPUT_DIR}")

    # 2. Load Model
    print(f"\n⏳ Loading AI Model...")
    try:
        classifier = StackingEnsembleClassifier()
        print(f"   ✅ Model loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load model: {e}")
        return

    # 3. Find Videos
    print(f"\n⏳ Scanning for videos...")
    all_videos = []
    for ext in VIDEO_EXTENSIONS:
        # Using rglob to find videos even inside subfolders
        all_videos.extend(list(INPUT_DIR.rglob(f'*{ext}')))
    
    if not all_videos:
        print(f"❌ No videos found in {INPUT_DIR}")
        return

    print(f"   ✅ Found {len(all_videos)} videos to analyze")

    # 4. Process Videos
    print(f"\n⏳ Starting Analysis...")
    print("-" * 80)

    stats = {
        'high_quality': 0,
        'low_quality': 0,
        'errors': 0,
        'processed': 0
    }
    
    results_log = []

    # Progress bar loop
    for video_path in tqdm(all_videos, desc="Analyzing Biomechanics"):
        try:
            # --- PREDICTION ---
            result = classifier.predict_video(str(video_path))
            
            # Check for prediction errors
            if 'error' in result:
                stats['errors'] += 1
                results_log.append({
                    'file': video_path.name,
                    'status': 'ERROR',
                    'error_msg': result['error']
                })
                continue

            # --- PARSE RESULTS ---
            # Handle cases where form_analysis might be a JSON string or dict
            form_analysis = result.get('form_analysis', {})
            if isinstance(form_analysis, str):
                try:
                    form_analysis = json.loads(form_analysis)
                except:
                    form_analysis = {}

            # Extract Score
            score = form_analysis.get('overall_score', 0)
            shot_type = result.get('prediction', 'Unknown')
            level = form_analysis.get('performance_level', 'Unknown')

            # --- DECISION LOGIC ---
            if score >= MIN_SCORE:
                stats['high_quality'] += 1
                kept = True
                
                # Copy file
                dest_path = get_unique_filename(OUTPUT_DIR, video_path.name)
                shutil.copy2(video_path, dest_path)
            else:
                stats['low_quality'] += 1
                kept = False

            # Log data
            results_log.append({
                'file': video_path.name,
                'status': 'KEPT' if kept else 'DROPPED',
                'score': score,
                'shot_type': shot_type,
                'level': level
            })
            
            stats['processed'] += 1

        except Exception as e:
            stats['errors'] += 1
            results_log.append({
                'file': video_path.name,
                'status': 'CRITICAL_ERROR',
                'error_msg': str(e)
            })

    # ==========================================
    # FINAL SUMMARY
    # ==========================================
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    total = len(all_videos)
    print(f"Total Videos:      {total}")
    print(f"✅ High Quality:   {stats['high_quality']} (Copied to {OUTPUT_DIR.name}/)")
    print(f"❌ Low Quality:    {stats['low_quality']}")
    print(f"⚠️  Errors:         {stats['errors']}")
    
    # Save Log
    log_file = Path("analysis_log.json")
    with open(log_file, 'w') as f:
        json.dump(results_log, f, indent=2)
    
    print(f"\n📄 Detailed log saved to: {log_file.absolute()}")
    
    if stats['high_quality'] > 0:
        # Show Top 3
        print("\n🏆 Top 3 Highest Scoring Shots:")
        valid_shots = [r for r in results_log if r.get('score')]
        valid_shots.sort(key=lambda x: x['score'], reverse=True)
        
        for i, shot in enumerate(valid_shots[:3], 1):
            print(f"   {i}. {shot['file']} - {shot['shot_type']} ({shot['score']}%)")
    else:
        print("\n⚠️  No videos met the 70% threshold.")

if __name__ == "__main__":
    main()