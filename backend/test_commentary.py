"""
Quick smoke-test: run 3 videos through the full inference + coaching commentary pipeline.
Run from the backend/ directory:  python test_commentary.py
"""
import sys, os, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")   # load GROQ_API_KEY before importing groq_router
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

TEST_VIDEOS = [
    r"C:\Users\hp\Desktop\test_videos\1.mp4",
    r"C:\Users\hp\Desktop\test_videos\5.mp4",
    r"C:\Users\hp\Desktop\test_videos\10.mp4",
]

CONTEXT = {"bowling_type": "medium", "ball_pitch": "good_length"}

print("=" * 65)
print("BattingEdge — Commentary Pipeline Test")
print("=" * 65)

# ── Load models once ──────────────────────────────────────────────
print("\n[1/2] Loading models...")
t0 = time.time()
try:
    from inference_v9_5 import StackingEnsembleClassifier
    classifier = StackingEnsembleClassifier()
    mode = "Ensemble" if classifier.is_ensemble else "BiLSTM-only"
    print(f"      ✅ Classifier ready ({mode}) in {time.time()-t0:.1f}s")
except Exception as e:
    print(f"      ❌ Classifier load FAILED: {e}")
    sys.exit(1)

try:
    from groq_router import generate_coaching_commentary
    print("      ✅ generate_coaching_commentary imported")
except Exception as e:
    print(f"      ❌ Import FAILED: {e}")
    sys.exit(1)

# ── Run each video ────────────────────────────────────────────────
print("\n[2/2] Running videos...\n")
passed = failed = 0

for i, video_path in enumerate(TEST_VIDEOS, 1):
    vname = Path(video_path).name
    print(f"  [{i}/{len(TEST_VIDEOS)}] {vname}")

    if not Path(video_path).exists():
        print(f"         ⚠️  File not found — skipping")
        failed += 1
        continue

    # Inference
    t1 = time.time()
    result = classifier.predict_video(video_path)
    inf_time = time.time() - t1

    if "error" in result:
        print(f"         ❌ Inference error: {result['error']}")
        failed += 1
        continue

    fa = result.get("form_analysis", {})
    print(f"         Shot      : {result['prediction']}")
    print(f"         Confidence: {result['confidence']:.1f}%")
    print(f"         Score     : {fa.get('overall_score', '?')}/100  Grade: {fa.get('grade', '?')}")
    print(f"         Inference : {inf_time:.1f}s")

    # Commentary
    t2 = time.time()
    commentary = generate_coaching_commentary(result, context=CONTEXT)
    com_time = time.time() - t2

    if commentary:
        preview = commentary[:180].replace("\n", " ")
        print(f"         Commentary: ✅ {com_time:.1f}s | {len(commentary)} chars")
        print(f"         Preview   : \"{preview}...\"")
    else:
        print(f"         Commentary: ⚠️  empty (Groq skipped or key missing)")

    passed += 1
    print()

# ── Summary ───────────────────────────────────────────────────────
print("=" * 65)
print(f"Results: {passed} passed, {failed} failed out of {len(TEST_VIDEOS)} videos")
print("=" * 65)
