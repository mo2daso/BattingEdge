"""
BattingEdge V9.5 - Report Generation & Coaching Logic Test
Verifies the new 'Calibrated' scoring and 'Platypus' PDF generation.
"""
import sys
import os
import random
import logging
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

try:
    from inference import StackingEnsembleClassifier
    import report as rpt
except ImportError as e:
    print(f"❌ Error: Could not import backend modules: {e}")
    sys.exit(1)

# CONFIG
DATASET_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP\dataset")
OUTPUT_DIR = Path("test_reports")
OUTPUT_DIR.mkdir(exist_ok=True)

def get_one_video_per_class(dataset_dir):
    """Finds one valid video for each shot type"""
    classes = ['Cover Drive', 'Pull Shot', 'Cut Shot', 'Sweep Shot', 'Defense']
    selection = []
    
    search_paths = [dataset_dir]
    for sub in ['train', 'test', 'val']:
        if (dataset_dir / sub).exists(): search_paths.append(dataset_dir / sub)

    for cls in classes:
        found = False
        for d in search_paths:
            # Try exact match
            target = d / cls
            if not target.exists():
                # Try case-insensitive
                for child in d.iterdir():
                    if child.is_dir() and child.name.lower() == cls.lower():
                        target = child
                        break
            
            if target and target.exists():
                videos = list(target.glob("*.mp4"))
                if videos:
                    # Pick a random one
                    vid = random.choice(videos)
                    selection.append((cls, vid))
                    found = True
                    break
        if not found:
            print(f"⚠️ Could not find video for {cls}")
            
    return selection

def main():
    print("="*80)
    print("📝 REPORT GENERATION TEST (5 VIDEOS)")
    print("="*80)

    # 1. Load Model
    print("\n⏳ Loading System...")
    try:
        model = StackingEnsembleClassifier()
        print("✅ Model Loaded")
    except Exception as e:
        print(f"❌ Init Failed: {e}")
        return

    # 2. Get Data
    test_videos = get_one_video_per_class(DATASET_DIR)
    if not test_videos:
        print("❌ No videos found. Check DATASET_DIR.")
        return

    print(f"✅ Selected {len(test_videos)} videos for reporting test.\n")

    # 3. Process Each
    for actual_type, video_path in test_videos:
        print("-" * 80)
        print(f"🎬 Processing: {video_path.name} (Expected: {actual_type})")
        
        try:
            # A. PREDICT
            result = model.predict_video(str(video_path))
            
            if 'error' in result:
                print(f"❌ Inference Error: {result['error']}")
                continue
                
            pred_shot = result['prediction']
            form = result['form_analysis']
            score = form.get('overall_score', 0)
            
            # B. PRINT ANALYSIS TO CONSOLE
            print(f"   🎯 Prediction: {pred_shot} | Score: {score}%")
            print(f"   📝 Summary:    {form.get('summary', 'No summary')}")
            
            print("\n   🔍 CHECKLIST (What the user sees):")
            for check in form.get('checks', []):
                # Using 'value' which is the Translated Display Value
                print(f"      - {check['name']:<15}: {check['value']:<8} (Target: {check['ideal_range']}) -> {check['status']}")
            
            print("\n   💡 ADVICE:")
            for imp in form.get('key_improvements', [])[:2]:
                print(f"      • {imp}")

            # C. GENERATE PDF
            pdf_filename = f"TEST_{pred_shot}_{video_path.stem[:10]}.pdf"
            pdf_path = OUTPUT_DIR / pdf_filename
            
            success = rpt.generate_pdf(result, pdf_path)
            
            if success:
                print(f"\n   ✅ PDF Created: {pdf_path}")
            else:
                print(f"\n   ❌ PDF Failed to build")

        except Exception as e:
            print(f"❌ CRASH: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print(f"✅ Test Complete. Check the '{OUTPUT_DIR}' folder to see the PDFs.")
    print("="*80)

if __name__ == "__main__":
    main()