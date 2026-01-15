"""
BattingEdge Model Comparison Tool
Compares Stacking Ensemble vs. BiLSTM on the exact same 10 videos.

Usage:
python compare_models.py
"""

import sys
import os
import random
import logging
from pathlib import Path
import pandas as pd

# ================= CONFIGURATION =================
DATASET_DIR = Path("dataset") # Directory containing class folders
SAMPLES_TOTAL = 10            # Total videos to test

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

# Suppress Logs for clean output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger("Inference").setLevel(logging.WARNING)
logging.getLogger("EnsembleInference").setLevel(logging.WARNING)
logging.getLogger("tensorflow").setLevel(logging.ERROR)

try:
    from inference import StackingEnsembleClassifier
except ImportError:
    print("❌ Critical Error: Could not import backend.inference")
    sys.exit(1)

def get_test_videos(dataset_dir, total_samples):
    """
    Picks 'total_samples' videos, evenly distributed across classes if possible.
    """
    if not dataset_dir.exists():
        print(f"❌ Dataset not found at {dataset_dir}")
        return []

    # Find all videos
    all_videos = []
    classes = ['Cover Drive', 'Pull Shot', 'Cut Shot', 'Sweep Shot', 'Defense']
    
    # Check subfolders (train/test/val)
    search_dirs = [dataset_dir]
    for sub in ['test', 'val', 'train']:
        if (dataset_dir / sub).exists():
            search_dirs.append(dataset_dir / sub)

    for cls in classes:
        cls_videos = []
        for d in search_dirs:
            # Case insensitive search
            target = d / cls
            if not target.exists():
                for child in d.iterdir():
                    if child.is_dir() and child.name.lower() == cls.lower():
                        target = child
                        break
            
            if target.exists():
                cls_videos.extend(list(target.glob("*.mp4")))
        
        if cls_videos:
            # Pick 2 per class to reach 10 total
            samples = random.sample(cls_videos, min(len(cls_videos), 2))
            all_videos.extend([(cls, v) for v in samples])

    # If we don't have enough, fill with randoms
    if len(all_videos) < total_samples:
        remaining = total_samples - len(all_videos)
        # Add logic to fill remainder if needed, but usually dataset is large enough
    
    # Shuffle
    random.shuffle(all_videos)
    return all_videos[:total_samples]

def main():
    print("="*100)
    print("🥊 MODEL SHOWDOWN: ENSEMBLE vs BILSTM")
    print("="*100)

    # 1. Select Videos
    print("\n🎥 Selecting 10 random videos (2 from each class)...")
    test_set = get_test_videos(DATASET_DIR, SAMPLES_TOTAL)
    
    if not test_set:
        print("❌ No videos found! Check 'dataset' folder path.")
        return

    print(f"   Selected {len(test_set)} videos for testing.\n")

    # 2. Load Models
    print("⏳ Loading Models...")
    
    # Model A: Ensemble
    model_ensemble = StackingEnsembleClassifier()
    if not model_ensemble.is_ensemble:
        print("❌ Error: Ensemble model files missing! Cannot run comparison.")
        return

    # Model B: BiLSTM (We force the ensemble flag to False)
    model_bilstm = StackingEnsembleClassifier()
    model_bilstm.is_ensemble = False 

    print("   ✅ Corner Red:  Stacking Ensemble (BiLSTM + XGBoost + RF)")
    print("   ✅ Corner Blue: BiLSTM Single Model")
    print("\n" + "-"*100)

    # 3. Run Comparison
    results = []
    scores = {"Ensemble": 0, "BiLSTM": 0}

    print(f"{'VIDEO':<25} | {'TRUE CLASS':<15} | {'ENSEMBLE PRED':<15} | {'BILSTM PRED':<15} | {'VERDICT'}")
    print("-" * 100)

    for true_label, video_path in test_set:
        # Run predictions
        try:
            # Ensemble
            res_ens = model_ensemble.predict_video(str(video_path))
            pred_ens = res_ens['prediction']
            conf_ens = res_ens['confidence']

            # BiLSTM
            res_bi = model_bilstm.predict_video(str(video_path))
            pred_bi = res_bi['prediction']
            conf_bi = res_bi['confidence']

            # Scoring
            ens_correct = (pred_ens == true_label)
            bi_correct = (pred_bi == true_label)

            if ens_correct: scores["Ensemble"] += 1
            if bi_correct: scores["BiLSTM"] += 1

            # Verdict Icon
            if ens_correct and not bi_correct:
                verdict = "🏆 Ens Wins"
            elif not ens_correct and bi_correct:
                verdict = "📉 BiLSTM Wins"
            elif ens_correct and bi_correct:
                verdict = "✅ Both Correct"
            else:
                verdict = "❌ Both Wrong"

            # Format Output
            vid_name = video_path.name
            if len(vid_name) > 22: vid_name = vid_name[:20] + ".."

            print(f"{vid_name:<25} | {true_label:<15} | {pred_ens:<12} {int(conf_ens)}% | {pred_bi:<12} {int(conf_bi)}% | {verdict}")
            
            results.append({
                "Video": video_path.name,
                "True": true_label,
                "Ensemble": f"{pred_ens} ({int(conf_ens)}%)",
                "BiLSTM": f"{pred_bi} ({int(conf_bi)}%)",
                "Correct?": verdict
            })

        except Exception as e:
            print(f"{video_path.name:<25} | ERROR: {str(e)}")

    # 4. Final Scoreboard
    print("-" * 100)
    print("\n🏆 FINAL SCOREBOARD")
    print("=" * 30)
    print(f"Stacking Ensemble: {scores['Ensemble']}/{len(test_set)}  ({(scores['Ensemble']/len(test_set))*100:.0f}%)")
    print(f"BiLSTM Only:       {scores['BiLSTM']}/{len(test_set)}  ({(scores['BiLSTM']/len(test_set))*100:.0f}%)")
    
    if scores['Ensemble'] > scores['BiLSTM']:
        print("\n🎉 CONCLUSION: Ensemble improves accuracy!")
    elif scores['Ensemble'] == scores['BiLSTM']:
        print("\n🤝 CONCLUSION: Models performing equally on this small sample.")
    else:
        print("\n🤔 CONCLUSION: BiLSTM performed better (check for overfitting in ensemble).")
    
    print("=" * 30)

if __name__ == "__main__":
    main()