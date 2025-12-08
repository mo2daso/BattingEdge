import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm
import time

# Add backend directory to path to import inference
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

try:
    from inference import CricketShotClassifier
except ImportError:
    print("❌ ERROR: Could not import 'inference.py'. Make sure it's in the 'backend' folder.")
    sys.exit(1)

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = current_dir.parent
DATA_DIR = PROJECT_ROOT / "data" / "dataset_v7_clean" / "test"
REPORT_DIR = PROJECT_ROOT / "data" / "reports"
OUTPUT_CSV = REPORT_DIR / "inference_test_results_full.csv"
CONF_MATRIX_IMG = REPORT_DIR / "inference_confusion_matrix.png"

# Create report directory if missing
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def run_comprehensive_test():
    print("=" * 70)
    print("🏏 BATTINGEDGE - COMPREHENSIVE INFERENCE TEST SUITE")
    print(f"📂 Scanning: {DATA_DIR}")
    print("=" * 70)

    # 1. Initialize Classifier
    try:
        classifier = CricketShotClassifier()
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return

    # 2. Collect All Test Videos
    test_videos = []
    classes = ['drive', 'pull', 'cut', 'sweep']
    
    for shot_class in classes:
        class_dir = DATA_DIR / shot_class
        if class_dir.exists():
            videos = list(class_dir.rglob("*.mp4")) + list(class_dir.rglob("*.avi"))
            for v in videos:
                test_videos.append({
                    "path": v,
                    "true_class": shot_class,
                    "filename": v.name
                })
        else:
            print(f"⚠️ Warning: Class folder not found: {shot_class}")

    total_videos = len(test_videos)
    print(f"\n📊 Found {total_videos} videos across {len(classes)} classes.")
    
    if total_videos == 0:
        print("❌ No videos found. Check your data paths.")
        return

    # 3. Run Inference Loop
    results = []
    print("\n🚀 Starting Inference...")
    
    start_time = time.time()
    
    # Progress bar using tqdm
    for item in tqdm(test_videos, desc="Processing", unit="video"):
        try:
            # Run Prediction
            res = classifier.predict_video(item['path'])
            
            if res and "error" not in res:
                # Success
                is_correct = (res['prediction'].lower() == item['true_class'].lower())
                results.append({
                    "filename": item['filename'],
                    "true_class": item['true_class'],
                    "predicted_class": res['prediction'],
                    "confidence": round(res['confidence'], 2),
                    "frames_used": res['frames'],
                    "correct": is_correct,
                    "error": None
                })
            else:
                # Failure (No pose detected, etc.)
                error_msg = res.get('error', 'Unknown Error') if res else 'Return None'
                results.append({
                    "filename": item['filename'],
                    "true_class": item['true_class'],
                    "predicted_class": "FAILED",
                    "confidence": 0.0,
                    "frames_used": 0,
                    "correct": False,
                    "error": error_msg
                })
                
        except Exception as e:
            results.append({
                "filename": item['filename'],
                "true_class": item['true_class'],
                "predicted_class": "ERROR",
                "confidence": 0.0,
                "frames_used": 0,
                "correct": False,
                "error": str(e)
            })

    elapsed = time.time() - start_time
    print(f"\n✅ Testing Complete in {elapsed:.2f} seconds ({elapsed/total_videos:.2f}s/video)")

    # 4. Process Results
    df = pd.DataFrame(results)
    
    # Filter out failures for metrics calculation
    valid_df = df[df['predicted_class'].isin(classes)]
    failed_count = len(df) - len(valid_df)
    
    accuracy = len(valid_df[valid_df['correct'] == True]) / len(valid_df) if len(valid_df) > 0 else 0
    
    # Save CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n💾 Results saved to: {OUTPUT_CSV}")

    # 5. Generate Report
    print("\n" + "="*70)
    print(f"📊 TEST SUMMARY (N={total_videos})")
    print("="*70)
    print(f"Overall Accuracy:  {accuracy*100:.2f}% (on valid inferences)")
    print(f"Successful Runs:   {len(valid_df)}/{total_videos}")
    print(f"Failures (No Pose): {failed_count}")
    print("-" * 70)
    
    if len(valid_df) > 0:
        # Per-Class Accuracy Table
        print("\n📈 PER-CLASS PERFORMANCE:")
        class_metrics = valid_df.groupby('true_class').apply(
            lambda x: pd.Series({
                'Total': len(x),
                'Correct': len(x[x['correct'] == True]),
                'Accuracy': (len(x[x['correct'] == True]) / len(x) * 100)
            })
        )
        print(class_metrics)

        # Classification Report
        print("\n📋 DETAILED METRICS:")
        print(classification_report(
            valid_df['true_class'], 
            valid_df['predicted_class'], 
            target_names=sorted(classes),
            digits=4
        ))

        # 6. Confusion Matrix
        plt.figure(figsize=(10, 8))
        cm = confusion_matrix(valid_df['true_class'], valid_df['predicted_class'], labels=classes)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=classes, yticklabels=classes)
        plt.title(f'Inference Confusion Matrix\nAccuracy: {accuracy*100:.2f}%')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig(CONF_MATRIX_IMG)
        print(f"\n🖼️ Confusion Matrix saved to: {CONF_MATRIX_IMG}")
        plt.close()

    else:
        print("⚠️ Not enough valid predictions to generate metrics.")

if __name__ == "__main__":
    run_comprehensive_test()