import sys
import os
import json
import numpy as np
from pathlib import Path
import random

# ================= CONFIGURATION =================
BASE_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP")
BACKEND_DIR = BASE_DIR / "backend"
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_DIR = BASE_DIR / "diagnostic_output"

# Ensure output dir exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Add backend to Python path so we can import inference/report
sys.path.insert(0, str(BACKEND_DIR))

try:
    from inference import StackingEnsembleClassifier
    import report as rpt
except ImportError as e:
    print(f"❌ CRITICAL ERROR: Could not import backend modules.")
    print(f"   Make sure 'inference.py' and 'report.py' are in {BACKEND_DIR}")
    print(f"   Error details: {e}")
    sys.exit(1)

def find_pull_shot_video():
    """Finds a random Pull Shot video to test the specific error case"""
    possible_folders = ["Pull Shot", "Pull", "pull shot", "pull"]
    
    # Check dataset subfolders (train/test/val)
    search_paths = [DATASET_DIR]
    for sub in ['train', 'test', 'val']:
        if (DATASET_DIR / sub).exists():
            search_paths.append(DATASET_DIR / sub)
            
    for base in search_paths:
        for folder_name in possible_folders:
            target = base / folder_name
            if target.exists():
                videos = list(target.glob("*.mp4"))
                if videos:
                    return videos[0] # Return the first one found
    return None

def main():
    print("="*60)
    print(" 🕵️‍♂️ BATTINGEDGE DIAGNOSTIC - PULL SHOT TEST")
    print("="*60)

    # 1. Locate a Pull Shot Video
    print("\n[1] Finding a Pull Shot video for testing...")
    video_path = find_pull_shot_video()
    
    if not video_path:
        print("❌ Could not find a 'Pull Shot' folder in your dataset!")
        print(f"   Checked in: {DATASET_DIR}")
        # Fallback: ask user
        print("   Please edit this script and manually set 'video_path' if you have one.")
        return
    else:
        print(f"   ✅ Found video: {video_path.name}")
        print(f"   📍 Path: {video_path}")

    # 2. Load Model
    print("\n[2] Loading Ensemble Model...")
    try:
        classifier = StackingEnsembleClassifier()
        if classifier.is_ensemble:
            print("   ✅ Ensemble Loaded: BiLSTM + XGBoost + RF")
        else:
            print("   ⚠️ WARNING: Only BiLSTM loaded (Ensemble files missing?)")
    except Exception as e:
        print(f"   ❌ Model Load Failed: {e}")
        return

    # 3. Run Prediction
    print("\n[3] Running Prediction...")
    result = classifier.predict_video(str(video_path))
    
    if 'error' in result:
        print(f"   ❌ Prediction Error: {result['error']}")
        return

    # 4. Analyze Results
    pred = result['prediction']
    conf = result['confidence']
    
    print("\n" + "-"*30)
    print(f"🎯 PREDICTION: {pred.upper()}")
    print(f"📊 CONFIDENCE: {conf:.2f}%")
    print("-"*30)
    
    print("\n📉 Class Probabilities (What the model 'thought'):")
    probs = result.get('all_probabilities', {})
    for shot, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
        marker = " <--- WRONG?" if shot == "Cover Drive" and pred == "Cover Drive" else ""
        marker = " <--- CORRECT" if shot == "Pull Shot" else marker
        print(f"   {shot:<15}: {prob:>6.2f}% {marker}")

    # 5. Check Feature Extraction Internals (Mock check)
    print("\n[4] Sanity Check on Features:")
    # We will try to extract features manually to check shape
    try:
        feats, _ = classifier.extract_features(video_path)
        if feats is not None:
            print(f"   ✅ Feature Shape: {feats.shape}")
            if feats.shape == (50, 107):
                print("   ✅ Shape matches training requirement (50 frames, 107 features)")
            else:
                print(f"   ❌ SHAPE MISMATCH! Expected (50, 107), Got {feats.shape}")
                print("      This is why the model is failing!")
    except Exception as e:
        print(f"   ⚠️ Feature extraction check failed: {e}")

    # 6. PDF Generation Test (To check text overlap)
    print("\n[5] Generating Diagnostic PDF...")
    pdf_out = OUTPUT_DIR / "diagnostic_report.pdf"
    
    try:
        # Force a filename for the report header
        result['filename'] = video_path.name
        
        # Inject long text to test wrapping
        result['form_analysis']['summary'] += " (DIAGNOSTIC TEST: This is a very long sentence added to verify that the text wrapping logic in the report generator is working correctly and does not overlap with other elements on the page.)"
        
        rpt.generate_pdf(result, pdf_out)
        print(f"   ✅ PDF Saved: {pdf_out}")
        print("   👉 Open this PDF now. If text overlaps, report.py is still broken.")
    except Exception as e:
        print(f"   ❌ PDF Generation Failed: {e}")

if __name__ == "__main__":
    main()