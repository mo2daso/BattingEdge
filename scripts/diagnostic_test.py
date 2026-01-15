# Quick diagnostic script
import json
from pathlib import Path
from backend.inference import StackingEnsembleClassifier

classifier = StackingEnsembleClassifier()

# Test video path - use your pull shot video
video_path = "D:\\Users\\Anoshia\\BattingEdge_FYP\\test_video.mp4"

result = classifier.predict_video(video_path)
print(json.dumps(result, indent=2))

# Also check probabilities
print("\n=== PROBABILITIES ===")
for shot, prob in result.get('all_probabilities', {}).items():
    print(f"{shot}: {prob:.2f}%")