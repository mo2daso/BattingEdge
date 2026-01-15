"""
BattingEdge V9.5 - Ensemble Accuracy Test
Validates model accuracy on 20 random videos from dataset.

Usage: python test_ensemble_accuracy.py
"""
import sys
import random
import logging
from pathlib import Path
from collections import defaultdict

# ================= CONFIGURATION =================
DATASET_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP\dataset") # Update if needed
SAMPLES_PER_CLASS = 4  # Total = 5 classes * 4 = 20 videos

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

try:
    from inference import StackingEnsembleClassifier
except ImportError:
    print("❌ Error: Could not import backend.inference")
    sys.exit(1)

def get_test_batch(dataset_dir, count_per_class):
    """Selects random videos from each class"""
    if not dataset_dir.exists():
        print(f"❌ Dataset not found at {dataset_dir}")
        return []

    classes = ['Cover Drive', 'Pull Shot', 'Cut Shot', 'Sweep Shot', 'Defense']
    batch = []
    
    # Search recursively for class folders
    search_paths = [dataset_dir]
    for sub in ['train', 'test', 'val']:
        if (dataset_dir / sub).exists(): search_paths.append(dataset_dir / sub)

    for cls in classes:
        videos = []
        for d in search_paths:
            # Case insensitive folder match
            target = None
            if (d / cls).exists(): target = d / cls
            else:
                for child in d.iterdir():
                    if child.is_dir() and child.name.lower() == cls.lower():
                        target = child
                        break
            
            if target:
                videos.extend(list(target.glob("*.mp4")))
        
        if videos:
            # Random sample
            selected = random.sample(videos, min(len(videos), count_per_class))
            batch.extend([(cls, v) for v in selected])
        else:
            print(f"⚠️  No videos found for class: {cls}")

    random.shuffle(batch)
    return batch

def main():
    print("="*80)
    print("🧪 ENSEMBLE ACCURACY CHECK (20 VIDEOS)")
    print("="*80)

    # 1. Load Model
    print("\n⏳ Loading Stacking Ensemble...")
    try:
        model = StackingEnsembleClassifier()
        if not model.is_ensemble:
            print("❌ Error: Ensemble failed to load (fallback active). Check model files.")
            return
        print("✅ Ensemble Loaded Successfully")
    except Exception as e:
        print(f"❌ Init Failed: {e}")
        return

    # 2. Get Data
    test_data = get_test_batch(DATASET_DIR, SAMPLES_PER_CLASS)
    print(f"✅ Loaded {len(test_data)} videos for testing.\n")

    # 3. Run Inference
    correct = 0
    results = defaultdict(lambda: {"correct": 0, "total": 0})

    print(f"{'VIDEO':<30} | {'ACTUAL':<15} | {'PREDICTED':<15} | {'CONF'}")
    print("-" * 80)

    for actual, video_path in test_data:
        try:
            res = model.predict_video(str(video_path))
            
            if 'error' in res:
                print(f"{video_path.name[:28]:<30} | {actual:<15} | ❌ ERROR")
                continue

            pred = res['prediction']
            conf = res['confidence']
            
            is_correct = (pred == actual)
            if is_correct: correct += 1
            
            results[actual]["total"] += 1
            if is_correct: results[actual]["correct"] += 1

            icon = "✅" if is_correct else "❌"
            print(f"{video_path.name[:28]:<30} | {actual:<15} | {pred:<15} | {int(conf)}% {icon}")

        except Exception as e:
            print(f"❌ Crash on {video_path.name}: {e}")

    # 4. Results
    print("\n" + "="*80)
    print("📊 CLASS PERFORMANCE")
    print("-" * 80)
    for cls, stats in sorted(results.items()):
        acc = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"{cls:<15}: {stats['correct']}/{stats['total']} ({acc:.0f}%)")

    total_acc = (correct / len(test_data)) * 100 if test_data else 0
    print("="*80)
    print(f"🏆 OVERALL ACCURACY: {total_acc:.1f}%")
    
    if total_acc >= 90:
        print("✅ PASS: System is ready for deployment.")
    elif total_acc >= 80:
        print("⚠️  WARNING: Accuracy is acceptable but lower than expected.")
    else:
        print("❌ FAIL: Something is wrong with feature extraction or model files.")
    print("="*80)

if __name__ == "__main__":
    main()