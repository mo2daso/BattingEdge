"""
Test single video with detailed output
Place this in ROOT directory and run: python test_single_video.py
"""
import sys
from pathlib import Path
import json

# ================= CONFIGURATION =================
# We assume the video is in the same directory as this script (ROOT)
VIDEO_PATH = Path("test_video.mp4")

# Output directory
OUTPUT_DIR = Path("test_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from inference import StackingEnsembleClassifier
    import report as rpt
except ImportError:
    print("❌ ERROR: Could not import backend modules.")
    print("   Ensure 'backend' folder contains inference.py and report.py")
    sys.exit(1)

# ================= MAIN TEST =================

def main():
    print("=" * 70)
    print("BATTINGEDGE V9.5 - SINGLE VIDEO TEST")
    print("=" * 70)
    
    # Check video exists
    if not VIDEO_PATH.exists():
        print(f"\n❌ ERROR: Video not found at: {VIDEO_PATH}")
        print(f"   Please place a video named 'test_video.mp4' in this folder")
        print(f"   OR update VIDEO_PATH in the script.")
        return
    
    print(f"\n📹 Video: {VIDEO_PATH.name}")
    print(f"   Size: {VIDEO_PATH.stat().st_size / (1024*1024):.2f} MB")
    
    # Load model
    print(f"\n⏳ Loading model...")
    try:
        classifier = StackingEnsembleClassifier()
        mode = "Ensemble (95%)" if classifier.is_ensemble else "BiLSTM Only (~85%)"
        print(f"   ✅ Model loaded: {mode}")
    except Exception as e:
        print(f"   ❌ Model load failed: {e}")
        return
    
    # Run inference
    print(f"\n⏳ Running inference...")
    print("-" * 70)
    
    result = classifier.predict_video(str(VIDEO_PATH))
    
    if 'error' in result:
        print(f"\n❌ INFERENCE FAILED")
        print(f"   Error: {result['error']}")
        return
    
    # ===== DISPLAY RESULTS =====
    
    print(f"\n{'=' * 70}")
    print(f"PREDICTION RESULTS")
    print(f"{'=' * 70}")
    
    print(f"\n🎯 SHOT DETECTED: {result['prediction']}")
    print(f"   Confidence: {result['confidence']:.1f}%")
    
    # All probabilities
    print(f"\n📊 ALL SHOT PROBABILITIES:")
    print(f"   {'Shot':<20s} {'Probability':>12s}")
    print(f"   {'-'*20} {'-'*12}")
    for shot, prob in sorted(
        result['all_probabilities'].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        bar = "█" * int(prob / 5)  # Visual bar
        print(f"   {shot:<20s} {prob:>6.2f}%  {bar}")
    
    # Form analysis
    form = result['form_analysis']
    
    print(f"\n{'=' * 70}")
    print(f"BIOMECHANICAL ANALYSIS")
    print(f"{'=' * 70}")
    
    print(f"\n📈 OVERALL ASSESSMENT:")
    print(f"   Score: {form['overall_score']}/100")
    print(f"   Grade: {form['grade']}")
    print(f"   Summary: {form['summary']}")
    
    # Strengths
    if form.get('strengths'):
        print(f"\n✅ STRENGTHS ({len(form['strengths'])}):")
        for i, strength in enumerate(form['strengths'], 1):
            print(f"   {i}. {strength}")
    else:
        print(f"\n✅ STRENGTHS: None identified")
    
    # Improvements
    if form.get('key_improvements'):
        print(f"\n⚠️  KEY IMPROVEMENTS NEEDED ({len(form['key_improvements'])}):")
        for i, improvement in enumerate(form['key_improvements'], 1):
            print(f"   {i}. {improvement}")
    
    # Detailed metrics
    print(f"\n{'=' * 70}")
    print(f"DETAILED BIOMECHANICAL METRICS")
    print(f"{'=' * 70}")
    
    print(f"\n   {'Metric':<25s} {'Value':>10s} {'Status':>8s}  {'Target Range':>20s}")
    print(f"   {'-'*25} {'-'*10} {'-'*8}  {'-'*20}")
    
    for check in form['checks']:
        status_icon = "✅" if not check['is_error'] else "❌"
        status_text = "Good" if not check['is_error'] else "Fair/Poor"
        
        print(f"   {check['name']:<25s} {check['value']:>10s} {status_icon} {status_text:>6s}  {check['ideal_range']}")
    
    # Save results
    print(f"\n{'=' * 70}")
    print(f"SAVING OUTPUTS")
    print(f"{'=' * 70}")
    
    # Save JSON
    json_path = OUTPUT_DIR / f"{VIDEO_PATH.stem}_result.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 JSON saved: {json_path}")
    
    # Create overlay (optional)
    create_overlay = input("\nCreate overlay video? (y/n): ").lower().strip() == 'y'
    
    if create_overlay:
        print(f"\n⏳ Creating overlay video...")
        overlay_path = OUTPUT_DIR / f"{VIDEO_PATH.stem}_overlay.mp4"
        
        try:
            success = classifier.create_overlay(str(VIDEO_PATH), str(overlay_path), result)
            if success:
                print(f"   ✅ Overlay saved: {overlay_path}")
            else:
                print(f"   ❌ Overlay creation failed")
        except Exception as e:
            print(f"   ❌ Overlay error: {e}")
    
    # Generate PDF (optional)
    create_pdf = input("Generate PDF report? (y/n): ").lower().strip() == 'y'
    
    if create_pdf:
        print(f"\n⏳ Generating PDF report...")
        try:
            result['filename'] = VIDEO_PATH.name # Ensure filename is set for report
            pdf_path = OUTPUT_DIR / f"{VIDEO_PATH.stem}_report.pdf"
            rpt.generate_pdf(result, pdf_path)
            print(f"   ✅ PDF saved: {pdf_path}")
        except Exception as e:
            print(f"   ❌ PDF generation failed: {e}")
    
    print(f"\n{'=' * 70}")
    print(f"TEST COMPLETE")
    print(f"{'=' * 70}")
    print(f"\n✅ All outputs saved to: {OUTPUT_DIR.absolute()}")
    print()

if __name__ == "__main__":
    main()