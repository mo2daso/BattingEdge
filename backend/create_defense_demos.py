import sys
import json
import pandas as pd
from pathlib import Path
from fpdf import FPDF

# Add path to import inference
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

try:
    from inference import CricketShotClassifier
except ImportError:
    print("❌ ERROR: Could not import 'inference.py'.")
    sys.exit(1)

PROJECT_ROOT = current_dir.parent
RESULTS_CSV = PROJECT_ROOT / "data" / "reports" / "inference_test_results_full.csv"
DATASET_DIR = PROJECT_ROOT / "data" / "dataset_v7_clean" / "test"
OUTPUT_DIR = PROJECT_ROOT / "data" / "defense_demos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Utility: make dict JSON-safe by converting numpy types to native ---
def json_safe(obj):
    import numpy as np
    if isinstance(obj, dict):
        return {json_safe(k): json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [json_safe(x) for x in obj]
    elif isinstance(obj, np.generic):  # catches np.float32, np.float64, np.int32, np.bool_, etc.
        return obj.item()
    elif hasattr(obj, "tolist"):       # catches numpy arrays
        return obj.tolist()
    else:
        return obj

def main():
    print("=" * 60)
    print("🎬 CREATING DEFENSE DEMOS (PER-VIDEO JSON & PDF)")
    print("=" * 60)

    if not RESULTS_CSV.exists():
        print(f"❌ Missing Results CSV: {RESULTS_CSV}")
        return

    df = pd.read_csv(RESULTS_CSV)
    classifier = CricketShotClassifier()
    summary_list = []

    # Strategy: Top 1 for Drive/Cut/Sweep, Top 2 for Pull
    targets = {'drive': 1, 'cut': 1, 'sweep': 1, 'pull': 2}

    processed_count = 0

    for shot, count in targets.items():
        candidates = df[
            (df['true_class'] == shot) & (df['correct'] == True)
        ].sort_values(by='confidence', ascending=False)

        for i in range(min(len(candidates), count)):
            row = candidates.iloc[i]
            video_path = DATASET_DIR / shot / row['filename']

            print(f"\nProcessing: {row['filename']} ({shot.upper()})")

            result = classifier.predict_video(video_path)

            if result and "error" not in result:
                # 1. Generate Overlay Video
                conf = float(result['confidence'])
                score = int(result['form_analysis']['overall_score'])
                out_vid = f"{shot}_{int(conf):d}pct_{score}form.mp4"
                classifier.create_overlay(video_path, OUTPUT_DIR / out_vid, result)

                # 2. SAVE PER-VIDEO JSON (JSON-safe)
                json_name = f"{shot}_{int(conf):d}pct_{score}form.json"
                result_clean = json_safe(result)
                with open(OUTPUT_DIR / json_name, 'w') as f:
                    json.dump(result_clean, f, indent=4)

                print(f"   ✅ Saved Video: {out_vid}")
                print(f"   ✅ Saved JSON:  {json_name}")

                # 3. Collect for global PDF
                summary_text = result['form_analysis'].get('summary', 'No summary available')
                summary_list.append({
                    "filename": str(row['filename']),
                    "shot": shot,
                    "confidence": conf,
                    "form_score": score,
                    "summary_text": summary_text
                })
                processed_count += 1
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

    # 4. Generate Global PDF
    if processed_count > 0:
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="BattingEdge Defense Demos", ln=True, align='C')
            pdf.ln(10)

            for item in summary_list:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt=f"Shot: {item['shot'].upper()}", ln=True)
                pdf.set_font("Arial", size=11)
                pdf.cell(0, 8, txt=f"File: {item['filename']}", ln=True)
                pdf.cell(0, 8, txt=f"Confidence: {item['confidence']:.2f}% | Form Score: {item['form_score']}", ln=True)
                pdf.multi_cell(0, 8, txt=f"Analysis: {item['summary_text']}")
                pdf.ln(4)

            pdf.output(str(OUTPUT_DIR / "demo_report.pdf"))
            print(f"\n📄 Saved Global PDF: demo_report.pdf")
        except Exception as e:
            print(f"\n⚠️ PDF generation skipped: {e}")

    print("\nDONE.")

if __name__ == "__main__":
    main()
