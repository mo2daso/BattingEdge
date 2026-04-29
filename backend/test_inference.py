"""
BattingEdge V9.5 — Inference Validation Script (Task 0.4)
Run from backend/ directory:
    python test_inference.py [optional: path/to/video.mp4]
"""
import sys
import os
import json
from pathlib import Path

# Add backend dir to path so imports resolve the same way as main.py
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Default video: first file from best_videos/
DEFAULT_VIDEO = str(Path(__file__).resolve().parent.parent / "best_videos" / "1.mp4")
video_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VIDEO

print("=" * 60)
print("  BattingEdge V9.5 — Inference Validation")
print("=" * 60)
print(f"  Video: {video_path}")

if not Path(video_path).exists():
    print(f"\n❌ ERROR: Video file not found: {video_path}")
    print("   Provide a path as argument: python test_inference.py <video>")
    sys.exit(1)

# --- Load model ---
print("\n[1/4] Loading StackingEnsembleClassifier...")
try:
    from inference_v9_5 import StackingEnsembleClassifier
    clf = StackingEnsembleClassifier()
    print(f"      ✅ Loaded. Ensemble: {clf.is_ensemble}")
except Exception as e:
    print(f"      ❌ FAILED: {e}")
    sys.exit(1)

# --- Run inference ---
print(f"\n[2/4] Running predict_video()...")
try:
    result = clf.predict_video(video_path)
except Exception as e:
    print(f"      ❌ FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# --- Full result dump ---
print("\n[3/4] Full result:\n")
print(json.dumps(result, indent=2, default=str))

# --- Validation ---
print("\n[4/4] Validation checks:")
passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"      ✅ {label}{' — ' + detail if detail else ''}")
        passed += 1
    else:
        print(f"      ❌ {label}{' — ' + detail if detail else ''}")
        failed += 1

# Top-level fields
prediction = result.get("prediction", "")
confidence = result.get("confidence", 0)
check("prediction present and non-empty", bool(prediction), prediction)
check("confidence non-zero", confidence > 0, f"{confidence:.2f}%")

# form_analysis
fa = result.get("form_analysis", {})
overall_score = fa.get("overall_score", 0)
check("overall_score present and non-zero", overall_score > 0, str(overall_score))
check("performance_level present", bool(fa.get("performance_level")), fa.get("performance_level", ""))
check("grade present", bool(fa.get("grade")), fa.get("grade", ""))
check("summary present", bool(fa.get("summary")))
check("strengths list present", isinstance(fa.get("strengths"), list))
check("key_improvements list present", isinstance(fa.get("key_improvements"), list))
check("recommended_drills list present", isinstance(fa.get("recommended_drills"), list))

# checks[] validation
checks = fa.get("checks", [])
check("checks[] non-empty", len(checks) > 0, f"{len(checks)} checks found")

for i, c in enumerate(checks):
    for field in ("name", "value", "ideal_range", "advice"):
        if field not in c:
            check(f"checks[{i}].{field} present", False, f"MISSING in check: {c.get('name', '?')}")

# Mandatory metrics: head_drift, hip_rotation
check_names = [c.get("name", "").lower() for c in checks]

head_drift_check = next((c for c in checks if "head" in c.get("name","").lower()), None)
hip_rotation_check = next((c for c in checks if "hip" in c.get("name","").lower()), None)

check("head_drift check present", head_drift_check is not None,
      f"value={head_drift_check.get('value') if head_drift_check else 'MISSING'}")
check("hip_rotation check present", hip_rotation_check is not None,
      f"value={hip_rotation_check.get('value') if hip_rotation_check else 'MISSING'}")

# back_lift — computed internally, not surfaced in checks[] by shot_rules.py
# This is expected behaviour — back_lift is used for feature extraction, not displayed
print(f"\n      ℹ️  back_lift: computed in BiomechanicsAnalyzer as a raw metric "
      f"but is NOT in checks[] (shot_rules.py doesn't surface it as a display metric). "
      f"This is expected V9.5 behaviour.")

# Overlay
print(f"\n[OPTIONAL] Testing overlay generation...")
overlay_path = str(Path(__file__).parent.parent / "backend" / "outputs" / "test_overlay.webm")
try:
    success = clf.create_overlay(video_path, overlay_path, result)
    check("overlay created successfully", success, overlay_path if success else "returned False")
except Exception as e:
    check("overlay created successfully", False, str(e))

# --- Summary ---
print(f"\n{'=' * 60}")
print(f"  RESULT: {passed} passed / {failed} failed")
if failed == 0:
    print("  ✅ ALL CHECKS PASSED — V9.5 inference validated")
else:
    print(f"  ❌ {failed} CHECK(S) FAILED — review output above")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
