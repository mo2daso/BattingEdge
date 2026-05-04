"""
BattingEdge V9.5 — PDF Report Validation (Task 2)
Runs REAL inference on a best_videos/ file, then generates the PDF from that result.
Run from backend/ directory:
    python test_pdf.py [optional: /path/to/video.mp4]
"""
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# ── Pick video from best_videos/ (never use mock data) ───────────────────────
DEFAULT_VIDEO = current_dir.parent / "best_videos" / "1.mp4"
video_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VIDEO

print("=" * 60)
print("  BattingEdge PDF Report Validation (real inference)")
print("=" * 60)
print(f"  Video : {video_path}")

if not video_path.exists():
    print(f"\n  [FAIL] Video not found: {video_path}")
    print("  Provide a path as argument: python test_pdf.py <video>")
    sys.exit(1)

# ── Step 1: Run real inference ────────────────────────────────────────────────
print("\n  [1/2] Running inference...")
try:
    from inference_v9_5 import StackingEnsembleClassifier
    clf = StackingEnsembleClassifier()
    result = clf.predict_video(str(video_path))
    result['filename'] = video_path.name
except Exception as e:
    print(f"\n  [FAIL] Inference failed: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

if 'error' in result:
    print(f"\n  [FAIL] Inference returned error: {result['error']}")
    sys.exit(1)

shot     = result.get('prediction', '?')
conf     = result.get('confidence', 0)
score    = result.get('form_analysis', {}).get('overall_score', 0)
grade    = result.get('form_analysis', {}).get('grade', '?')
print(f"  Shot     : {shot}")
print(f"  Confidence: {conf:.1f}%")
print(f"  Score    : {score}/100  Grade: {grade}")

# ── Step 2: Generate PDF from real result ─────────────────────────────────────
print("\n  [2/2] Generating PDF report...")
output_path = current_dir.parent / "backend" / "outputs" / "test_report.pdf"
output_path.parent.mkdir(parents=True, exist_ok=True)

from report import generate_pdf
success = generate_pdf(result, output_path)

if success and output_path.exists():
    size_kb = output_path.stat().st_size / 1024
    print(f"\n  [PASS] PDF generated ({size_kb:.1f} KB)")
    print(f"  Shot in PDF : {shot}  (matches inference above)")
    print(f"  Open: {output_path}")
    sys.exit(0)
else:
    print("\n  [FAIL] PDF generation failed — check log above")
    sys.exit(1)
