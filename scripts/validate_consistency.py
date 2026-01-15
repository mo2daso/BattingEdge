"""
Validate consistency between overlay video, PDF report, and JSON output
Place this in ROOT directory and run: python validate_consistency.py
"""
import sys
from pathlib import Path
import json

# ================= CONFIGURATION =================
# UPDATE THIS PATH to your test video
VIDEO_PATH = Path("test_video.mp4")

# Output directory
VALIDATION_DIR = Path("validation_output")
VALIDATION_DIR.mkdir(exist_ok=True)

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from inference import StackingEnsembleClassifier
    import report as rpt
except ImportError:
    print("❌ ERROR: Could not import backend modules.")
    sys.exit(1)

# ================= MAIN TEST =================

def main():
    print("=" * 80)
    print("BATTINGEDGE V9.5 - CONSISTENCY VALIDATION TEST")
    print("=" * 80)
    print("\nThis test verifies that all outputs (JSON, Overlay, PDF) contain the same data")
    
    # Check video exists
    if not VIDEO_PATH.exists():
        print(f"\n❌ ERROR: Video not found at: {VIDEO_PATH}")
        print(f"   Please place a video named 'test_video.mp4' in this folder")
        return
    
    print(f"\n📹 Test Video: {VIDEO_PATH.name}")
    
    # Load model
    print(f"\n⏳ Step 1/5: Loading model...")
    try:
        classifier = StackingEnsembleClassifier()
        mode = "Ensemble (95%)" if classifier.is_ensemble else "BiLSTM Only (~85%)"
        print(f"   ✅ Model loaded: {mode}")
    except Exception as e:
        print(f"   ❌ Model load failed: {e}")
        return
    
    # Run inference
    print(f"\n⏳ Step 2/5: Running inference...")
    result = classifier.predict_video(str(VIDEO_PATH))
    
    if 'error' in result:
        print(f"   ❌ Inference failed: {result['error']}")
        return
    
    result['filename'] = VIDEO_PATH.name
    print(f"   ✅ Inference complete")
    
    # Save JSON
    print(f"\n⏳ Step 3/5: Saving JSON...")
    json_path = VALIDATION_DIR / "result.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"   ✅ JSON saved: {json_path}")
    
    # Create overlay
    print(f"\n⏳ Step 4/5: Creating overlay video...")
    overlay_path = VALIDATION_DIR / "overlay.mp4"
    try:
        success = classifier.create_overlay(str(VIDEO_PATH), str(overlay_path), result)
        if success:
            print(f"   ✅ Overlay saved: {overlay_path}")
        else:
            print(f"   ❌ Overlay creation failed")
            overlay_path = None
    except Exception as e:
        print(f"   ❌ Overlay error: {e}")
        overlay_path = None
    
    # Generate PDF
    print(f"\n⏳ Step 5/5: Generating PDF report...")
    pdf_path = VALIDATION_DIR / "report.pdf"
    try:
        rpt.generate_pdf(result, pdf_path)
        print(f"   ✅ PDF saved: {pdf_path}")
    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        pdf_path = None
    
    # ===== VALIDATION RESULTS =====
    
    print(f"\n{'=' * 80}")
    print(f"VALIDATION RESULTS")
    print(f"{'=' * 80}")
    
    form = result['form_analysis']
    
    # Extract key values to verify
    key_values = {
        "Shot Prediction": result['prediction'],
        "Confidence": f"{result['confidence']:.1f}%",
        "Overall Score": f"{form['overall_score']}/100",
        "Grade": form['grade'],
        "Strengths": len(form.get('strengths', [])),
        "Improvements": len(form.get('key_improvements', [])),
        "Metrics Checked": len(form['checks'])
    }
    
    print(f"\n📋 KEY VALUES (verify these match across all outputs):")
    print(f"   {'-' * 76}")
    for label, value in key_values.items():
        print(f"   {label:<20s}: {value}")
    print(f"   {'-' * 76}")
    
    # Manual verification checklist
    print(f"\n{'=' * 80}")
    print(f"MANUAL VERIFICATION CHECKLIST")
    print(f"{'=' * 80}")
    
    print(f"\n✅ Files Generated:")
    print(f"   1. JSON:     {json_path.absolute()}")
    if overlay_path:
        print(f"   2. Overlay: {overlay_path.absolute()}")
    if pdf_path:
        print(f"   3. PDF:      {pdf_path.absolute()}")
    
    print(f"\n📝 Verification Steps:")
    print(f"   1. Open JSON file - this is your baseline truth")
    print(f"   2. Play overlay video - verify HUD shows:")
    print(f"      • Shot: {result['prediction'].upper()}")
    print(f"      • Score: {form['overall_score']}/100")
    print(f"      • Grade: {form['grade']}")
    print(f"   3. Open PDF report - verify:")
    print(f"      • Header shows correct shot/score/grade")
    print(f"      • All metric values match JSON")
    print(f"      • No text overflow in tables")
    
    # Check for common issues
    print(f"\n🔎 Automated Checks:")
    
    issues = []
    
    # Check 1: Score vs Grade consistency
    score = form['overall_score']
    grade = form['grade']
    
    # Simple check - actual logic is in ShotRules
    if score >= 90 and grade != 'A': issues.append(f"Possible grade mismatch: Score {score} but Grade {grade}")
    elif score < 40 and grade != 'F': issues.append(f"Possible grade mismatch: Score {score} but Grade {grade}")
    else: print(f"   ✅ Grade-Score consistency check passed")
    
    # Check 2: Probabilities sum to ~100%
    total_prob = sum(result['all_probabilities'].values())
    if abs(total_prob - 100.0) > 0.1:
        issues.append(f"Probabilities don't sum to 100%: {total_prob:.2f}%")
    else:
        print(f"   ✅ Probability sum: {total_prob:.2f}%")
    
    # Check 3: Check for nested form_analysis
    if 'form_analysis' in form:
        issues.append("Double-nested form_analysis detected! (form_analysis.form_analysis)")
    else:
        print(f"   ✅ No double-nesting in form_analysis")
    
    # Report issues
    if issues:
        print(f"\n❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print(f"\n✅ All automated checks passed!")
    
    print(f"\n📁 All outputs saved to: {VALIDATION_DIR.absolute()}\n")

if __name__ == "__main__":
    main()