import sys
import os
from pathlib import Path

# Setup paths
current_dir = Path(__file__).resolve().parent
output_dir = current_dir / "outputs"
output_dir.mkdir(exist_ok=True)

# Import your report module
try:
    import report as rpt
    print("✅ Successfully imported report.py")
except ImportError as e:
    print(f"❌ Could not import report.py: {e}")
    sys.exit(1)

# Dummy Data (Matches your AI output format)
dummy_result = {
    "prediction": "cover drive",
    "confidence": 98.5,
    "form_analysis": {
        "overall_score": 78,
        "performance_level": "Advanced",
        "grade": "B",
        "summary": "Good shot with solid mechanics. Work on head stability.",
        "strengths": [
            "Great elbow extension (160°)",
            "Good bat angle (vertical)",
            "Strong hip rotation"
        ],
        "key_improvements": [
            "Head falling over slightly",
            "Front foot could plant firmer"
        ],
        "checks": [
            {
                "name": "Elbow Angle",
                "value": "160.5°",
                "ideal_range": "120-180°",
                "status": "Excellent",
                "advice": "Perfect extension!"
            },
            {
                "name": "Head Drift",
                "value": "95cm",
                "ideal_range": "<90cm",
                "status": "Acceptable",
                "advice": "Keep head stiller."
            }
        ],
        "recommended_drills": [
            {"name": "Wall Drill", "description": "Lean against wall for balance."},
            {"name": "Tee Work", "description": "Hit stationary balls."}
        ]
    }
}

def run_test():
    print("="*50)
    print("🚀 STARTING PDF DIAGNOSTIC TEST")
    print("="*50)
    
    output_path = output_dir / "test_report.pdf"
    
    try:
        print(f"📂 Output Path: {output_path}")
        print("⏳ Generating PDF...")
        
        # CALL THE FUNCTION
        success = rpt.generate_pdf(dummy_result, output_path)
        
        if success:
            print("\n✅ SUCCESS! PDF Generated.")
            print(f"📄 Check file at: {output_path}")
        else:
            print("\n❌ FAILURE. Function returned False.")
            
    except Exception as e:
        print("\n❌ CRASH DETECTED!")
        print("-" * 30)
        import traceback
        traceback.print_exc()
        print("-" * 30)

if __name__ == "__main__":
    run_test()