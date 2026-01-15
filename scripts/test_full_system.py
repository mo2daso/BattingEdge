"""
BattingEdge V9.5 - Complete System Test
Tests model accuracy, consistency, and generates detailed report
"""

import os
import sys
import cv2
import numpy as np
import shutil
import json
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import pandas as pd

# Add backend to path
SCRIPT_DIR = Path(__file__).parent
if 'backend' in SCRIPT_DIR.parts:
    BASE_DIR = SCRIPT_DIR.parent
else:
    BASE_DIR = SCRIPT_DIR

sys.path.insert(0, str(BASE_DIR / "backend"))

from inference import StackingEnsembleClassifier

# ==========================================
# CONFIGURATION
# ==========================================
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = BASE_DIR / "test_results"
REPORT_FILE = OUTPUT_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# Create output dirs
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "correct").mkdir(exist_ok=True)
(OUTPUT_DIR / "incorrect").mkdir(exist_ok=True)

# ==========================================
# INITIALIZE MODEL
# ==========================================
print("="*60)
print("BATTINGEDGE V9.5 - COMPLETE SYSTEM TEST")
print("="*60)
print(f"\nDataset: {DATASET_DIR}")
print(f"Output: {OUTPUT_DIR}\n")

try:
    classifier = StackingEnsembleClassifier()
    print(f"✅ Model loaded successfully")
    print(f"   Mode: {'Ensemble (95%)' if classifier.is_ensemble else 'BiLSTM Only'}")
    print(f"   Classes: {classifier.classes}\n")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

# ==========================================
# TEST FUNCTIONS
# ==========================================
def test_single_video(video_path, true_label):
    """Test single video and return results"""
    result = classifier.predict_video(str(video_path))
    
    if 'error' in result:
        return {
            'video': video_path.name,
            'true_label': true_label,
            'predicted': None,
            'confidence': 0,
            'correct': False,
            'error': result['error']
        }
    
    predicted = result['prediction']
    confidence = result['confidence']
    correct = (predicted == true_label)
    
    form = result.get('form_analysis', {})
    
    return {
        'video': video_path.name,
        'true_label': true_label,
        'predicted': predicted,
        'confidence': confidence,
        'correct': correct,
        'score': form.get('overall_score', 0),
        'grade': form.get('grade', 'N/A'),
        'error': None
    }

def save_video_copy(video_path, true_label, predicted, correct):
    """Copy video to organized output folder"""
    if correct:
        dest_folder = OUTPUT_DIR / "correct" / true_label
    else:
        dest_folder = OUTPUT_DIR / "incorrect" / f"true_{true_label}" / f"pred_{predicted}"
    
    dest_folder.mkdir(parents=True, exist_ok=True)
    dest_path = dest_folder / video_path.name
    
    try:
        shutil.copy2(video_path, dest_path)
    except Exception as e:
        print(f"⚠️ Failed to copy {video_path.name}: {e}")

# ==========================================
# RUN TESTS
# ==========================================
stats = {
    'total': 0,
    'correct': 0,
    'incorrect': 0,
    'errors': 0,
    'by_class': {}
}

results_list = []
confusion_matrix = {}

# Initialize confusion matrix
for class_name in classifier.classes:
    stats['by_class'][class_name] = {'correct': 0, 'total': 0}
    confusion_matrix[class_name] = {c: 0 for c in classifier.classes}

# Test all subsets
subsets = ['train', 'test', 'val']

for subset in subsets:
    subset_path = DATASET_DIR / subset
    
    if not subset_path.exists():
        print(f"⚠️ Subset '{subset}' not found, skipping...")
        continue
    
    print(f"\n{'='*60}")
    print(f"Testing subset: {subset.upper()}")
    print(f"{'='*60}\n")
    
    for class_name in classifier.classes:
        class_dir = subset_path / class_name
        
        if not class_dir.exists():
            print(f"⚠️ Class '{class_name}' not found in {subset}")
            continue
        
        videos = list(class_dir.glob("*.mp4"))
        
        if not videos:
            print(f"⚠️ No videos found for {class_name} in {subset}")
            continue
        
        print(f"Testing {class_name}: {len(videos)} videos")
        
        for video_path in tqdm(videos, desc=f"{class_name}", leave=False):
            stats['total'] += 1
            stats['by_class'][class_name]['total'] += 1
            
            # Test video
            result = test_single_video(video_path, class_name)
            results_list.append(result)
            
            if result['error']:
                stats['errors'] += 1
                continue
            
            # Update stats
            if result['correct']:
                stats['correct'] += 1
                stats['by_class'][class_name]['correct'] += 1
            else:
                stats['incorrect'] += 1
            
            # Update confusion matrix
            if result['predicted']:
                confusion_matrix[class_name][result['predicted']] += 1
            
            # Save video copy
            save_video_copy(
                video_path,
                class_name,
                result['predicted'],
                result['correct']
            )

# ==========================================
# GENERATE REPORT
# ==========================================
print(f"\n{'='*60}")
print("GENERATING REPORT")
print(f"{'='*60}\n")

with open(REPORT_FILE, 'w') as f:
    f.write("="*60 + "\n")
    f.write("BATTINGEDGE V9.5 - TEST REPORT\n")
    f.write("="*60 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Model Mode: {'Ensemble' if classifier.is_ensemble else 'BiLSTM Only'}\n")
    f.write(f"Dataset: {DATASET_DIR}\n")
    f.write("\n")
    
    # Overall Statistics
    f.write("OVERALL STATISTICS\n")
    f.write("-"*60 + "\n")
    f.write(f"Total Videos Tested: {stats['total']}\n")
    f.write(f"Correct Predictions: {stats['correct']} ({stats['correct']/stats['total']*100:.2f}%)\n")
    f.write(f"Incorrect Predictions: {stats['incorrect']} ({stats['incorrect']/stats['total']*100:.2f}%)\n")
    f.write(f"Errors (No Pose): {stats['errors']}\n")
    f.write("\n")
    
    # Per-Class Accuracy
    f.write("PER-CLASS ACCURACY\n")
    f.write("-"*60 + "\n")
    for class_name in classifier.classes:
        total = stats['by_class'][class_name]['total']
        correct = stats['by_class'][class_name]['correct']
        
        if total > 0:
            acc = (correct / total) * 100
            f.write(f"{class_name:20s}: {correct:3d}/{total:3d} ({acc:5.2f}%)\n")
        else:
            f.write(f"{class_name:20s}: No videos tested\n")
    f.write("\n")
    
    # Confusion Matrix
    f.write("CONFUSION MATRIX\n")
    f.write("-"*60 + "\n")
    f.write(f"{'True \\ Pred':20s}")
    for c in classifier.classes:
        f.write(f"{c:12s}")
    f.write("\n")
    f.write("-"*60 + "\n")
    
    for true_class in classifier.classes:
        f.write(f"{true_class:20s}")
        for pred_class in classifier.classes:
            count = confusion_matrix[true_class][pred_class]
            f.write(f"{count:12d}")
        f.write("\n")
    f.write("\n")
    
    # Common Misclassifications
    f.write("COMMON MISCLASSIFICATIONS\n")
    f.write("-"*60 + "\n")
    misclass = []
    for true_class in classifier.classes:
        for pred_class in classifier.classes:
            if true_class != pred_class:
                count = confusion_matrix[true_class][pred_class]
                if count > 0:
                    misclass.append((count, true_class, pred_class))
    
    misclass.sort(reverse=True)
    for count, true_class, pred_class in misclass[:10]:
        f.write(f"{true_class:20s} → {pred_class:20s}: {count:3d} times\n")
    f.write("\n")
    
    # Score Distribution
    f.write("SCORE DISTRIBUTION\n")
    f.write("-"*60 + "\n")
    scores = [r['score'] for r in results_list if not r['error']]
    if scores:
        f.write(f"Average Score: {np.mean(scores):.1f}/100\n")
        f.write(f"Median Score:  {np.median(scores):.1f}/100\n")
        f.write(f"Min Score:     {np.min(scores):.1f}/100\n")
        f.write(f"Max Score:     {np.max(scores):.1f}/100\n")
    f.write("\n")
    
    # Grade Distribution
    f.write("GRADE DISTRIBUTION\n")
    f.write("-"*60 + "\n")
    grades = [r['grade'] for r in results_list if not r['error']]
    from collections import Counter
    grade_counts = Counter(grades)
    
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = grade_counts.get(grade, 0)
        pct = (count / len(grades) * 100) if grades else 0
        f.write(f"Grade {grade}: {count:4d} ({pct:5.2f}%)\n")
    f.write("\n")
    
    # Failures
    errors = [r for r in results_list if r['error']]
    if errors:
        f.write("FAILED VIDEOS (NO POSE DETECTED)\n")
        f.write("-"*60 + "\n")
        for err in errors[:20]:
            f.write(f"{err['video']:40s} - {err['error']}\n")
        f.write(f"\n... and {len(errors)-20} more\n" if len(errors) > 20 else "")

# Save CSV
df = pd.DataFrame(results_list)
csv_path = OUTPUT_DIR / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(csv_path, index=False)

print(f"\n{'='*60}")
print("TEST COMPLETE")
print(f"{'='*60}")
print(f"\nResults saved to:")
print(f"  Report: {REPORT_FILE}")
print(f"  CSV:    {csv_path}")
print(f"  Videos: {OUTPUT_DIR}")
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Total Videos: {stats['total']}")
print(f"Accuracy:     {stats['correct']}/{stats['total']} ({stats['correct']/stats['total']*100:.2f}%)")
print(f"Errors:       {stats['errors']}")
print(f"{'='*60}\n")