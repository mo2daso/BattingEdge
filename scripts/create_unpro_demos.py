"""
Create Demo Videos from Unprofessional Players
Generates videos, JSONs, and PDFs with human-readable coaching advice
"""

import sys
import json
import cv2
from pathlib import Path
from datetime import datetime
import traceback  # Added for error logging

# Add backend to path
sys.path.insert(0, 'backend')

try:
    from inference import CricketShotClassifier
    print("✅ Successfully imported CricketShotClassifier")
    # Import reportlab for PDF generation
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.units import inch
except ImportError as e:
    print(f"❌ Error importing: {e}")
    print("Ensure you have installed: pip install reportlab")
    sys.exit(1)

# Paths
RAW_CLIPS_DIR = Path(r"D:\Users\Anoshia\BattingEdge_FYP\data\Raw_Testing_Clips_Unsorted")
OUTPUT_DIR = Path("data/defense_demos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Human-readable coaching advice
COACHING_ADVICE = {
    "Elbow": {
        "good": "Your front arm extension is excellent! This positioning allows maximum power transfer through the shot. Keep practicing this form.",
        "minor": "Your elbow is slightly bent at impact. Try extending your front arm more fully as you make contact with the ball. Practice shadow batting with focus on full arm extension.",
        "major": "Your front elbow is too bent ('chicken wing'). This significantly reduces power. Practice the 'wall drill' - stand near a wall and practice your swing ensuring your front arm extends fully without hitting the wall."
    },
    "Head": {
        "good": "Great head stability! Your eyes stayed level throughout the shot, which is crucial for tracking the ball and timing. This is textbook technique.",
        "minor": "Your head moved a bit during the shot. Try to keep your head as still as possible - imagine balancing a book on your head while batting. This helps maintain sight of the ball.",
        "major": "Your head is moving too much (dipping or falling away). This causes you to lose sight of the ball. Practice the 'nose over toes' drill - your nose should stay over your front toe throughout the shot. Try batting with a cap and place a tennis ball on top to train stability."
    },
    "BackFoot": {
        "good": "Excellent back foot stability! Your base is solid, allowing proper weight transfer. This foundation is key to generating power.",
        "minor": "Your back foot lifted slightly early. While not critical, keeping it grounded longer will improve your balance and power transfer. Practice weight distribution drills.",
        "major": "Your back foot is lifting too early, causing you to lose balance and power. Your base becomes unstable. Practice the 'anchor drill' - place a small weight on your back foot during shadow practice, or have someone hold your back foot down initially to feel the correct position."
    },
    "Hips": {
        "good": "Perfect hip rotation! You're generating excellent power through your lower body. This aggressive rotation is exactly what's needed for this shot.",
        "minor": "Your hip rotation is present but could be more aggressive. The power in cricket shots comes from the hips, not just the arms. Practice the 'pivot drill' - stand with bat down and practice rotating your hips forcefully without moving your feet.",
        "major": "You need much more hip rotation. You're mostly using your arms, which limits power significantly. Think 'hips lead, hands follow'. Practice shadow shots focusing ONLY on hip rotation first, then add the arms. Watch videos of professional batters in slow motion to see how early and aggressive their hip turn is."
    },
    "Finish": {
        "good": "Beautiful high finish! Your hands completed the full arc, showing complete commitment to the shot. This maximizes power and control.",
        "minor": "Your follow-through is there but stops a bit short. Try to exaggerate the finish - let your hands go all the way up and over your shoulder. This ensures full power transfer.",
        "major": "Your follow-through is incomplete - hands stopping low. This means you're decelerating through the shot, losing power. Practice 'full swing drills' where you exaggerate the follow-through. Your hands should finish HIGH - near or above your opposite shoulder. Think 'throw the bat over your shoulder' (but controlled!)."
    }
}

def get_human_advice(check_name, is_error, severity="minor"):
    """Get human-readable coaching advice"""
    advice_dict = COACHING_ADVICE.get(check_name, {})
    
    if not is_error:
        return advice_dict.get("good", "Good form on this aspect!")
    elif severity == "minor":
        return advice_dict.get("minor", "Minor improvement needed.")
    else:
        return advice_dict.get("major", "Significant improvement needed.")

def enhance_result_with_advice(result):
    """Add detailed human coaching to the result"""
    if 'form_analysis' not in result:
        return result
    
    form = result['form_analysis']
    enhanced_checks = []
    
    for check in form.get('checks', []):
        # [IMPROVEMENT 1] Better Severity Logic
        # Check if severity is explicitly provided, otherwise infer
        if 'severity' in check:
            severity = check['severity']
        else:
            # Default logic if severity missing: Major if error exists
            severity = "major" if check.get('is_error') else "none"
        
        # Get human advice
        advice = get_human_advice(
            check['name'], 
            check.get('is_error', False),
            severity
        )
        
        enhanced_check = {
            **check,
            'severity': severity,
            'detailed_advice': advice
        }
        enhanced_checks.append(enhanced_check)
    
    result['form_analysis']['checks'] = enhanced_checks
    
    # Enhanced summary
    score = form.get('overall_score', 0)
    errors = [c for c in enhanced_checks if c['is_error']]
    
    if score >= 85:
        summary = "🌟 Excellent form! You're executing this shot at a high level. "
    elif score >= 70:
        summary = "👍 Good form overall with room for fine-tuning. "
    elif score >= 50:
        summary = "⚠️ Decent attempt but several technical issues to address. "
    else:
        summary = "❌ Form needs significant work. Don't worry - everyone starts somewhere! "
    
    if errors:
        error_names = [e['name'] for e in errors]
        summary += f"Focus on improving: {', '.join(error_names)}. "
    
    summary += "Keep practicing and you'll see improvement!"
    result['form_analysis']['enhanced_summary'] = summary
    
    return result

def get_video_info(video_path):
    """Get basic video information"""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {'fps': 0, 'frames': 0, 'duration': 0, 'resolution': "Unknown"}
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    return {
        'fps': fps,
        'frames': frame_count,
        'duration': frame_count / fps if fps > 0 else 0,
        'resolution': f"{width}x{height}"
    }

def generate_pdf_report(result, video_name, pdf_path):
    """Generate detailed PDF report"""
    try:
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(1*inch, height - 1*inch, "BattingEdge Coaching Report")
        
        c.setFont("Helvetica", 10)
        c.drawString(1*inch, height - 1.3*inch, f"Video: {video_name}")
        c.drawString(1*inch, height - 1.5*inch, f"Date: {datetime.now().strftime('%B %d, %Y')}")
        c.drawString(1*inch, height - 1.7*inch, f"Analysis Type: Unprofessional Player Assessment")
        
        # Shot Analysis
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 2.2*inch, "SHOT ANALYSIS")
        
        c.setFont("Helvetica", 12)
        y = height - 2.5*inch
        
        shot = result['prediction'].upper()
        conf = result['confidence']
        c.drawString(1.2*inch, y, f"Predicted Shot: {shot}")
        y -= 0.25*inch
        c.drawString(1.2*inch, y, f"Model Confidence: {conf:.1f}%")
        
        # Form Score
        y -= 0.5*inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1*inch, y, "FORM QUALITY SCORE")
        
        score = result['form_analysis']['overall_score']
        y -= 0.3*inch
        c.setFont("Helvetica-Bold", 24)
        
        # Color based on score
        if score >= 80:
            c.setFillColorRGB(0, 0.7, 0)  # Green
        elif score >= 60:
            c.setFillColorRGB(0.8, 0.8, 0)  # Yellow
        else:
            c.setFillColorRGB(0.8, 0, 0)  # Red
        
        c.drawString(1.2*inch, y, f"{score}/100")
        c.setFillColorRGB(0, 0, 0)  # Reset to black
        
        # Summary
        y -= 0.5*inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1*inch, y, "Overall Assessment:")
        
        y -= 0.25*inch
        c.setFont("Helvetica", 10)
        summary = result['form_analysis'].get('enhanced_summary', result['form_analysis'].get('summary', ''))
        
        # Word wrap summary
        words = summary.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if len(test_line) * 6 > (width - 2*inch):  # Rough character width
                c.drawString(1.2*inch, y, line)
                y -= 0.2*inch
                line = word + " "
            else:
                line = test_line
        if line:
            c.drawString(1.2*inch, y, line)
        
        # Technical Breakdown
        y -= 0.5*inch
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1*inch, y, "TECHNICAL BREAKDOWN")
        
        y -= 0.3*inch
        for i, check in enumerate(result['form_analysis']['checks'], 1):
            if y < 2*inch:  # Start new page if needed
                c.showPage()
                y = height - 1*inch
                c.setFont("Helvetica", 10)
            
            # Check header
            c.setFont("Helvetica-Bold", 11)
            status = "✓" if not check['is_error'] else "✗"
            c.drawString(1*inch, y, f"{i}. {check['name']}: {status}")
            
            y -= 0.2*inch
            c.setFont("Helvetica", 9)
            c.drawString(1.2*inch, y, f"Measured: {check['value']}")
            
            # Detailed advice (word wrap)
            y -= 0.25*inch
            c.setFont("Helvetica", 9)
            advice = check.get('detailed_advice', 'No advice available')
            
            words = advice.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if len(test_line) * 5.5 > (width - 2.4*inch):
                    c.drawString(1.2*inch, y, line)
                    y -= 0.18*inch
                    line = word + " "
                else:
                    line = test_line
            if line:
                c.drawString(1.2*inch, y, line)
            
            y -= 0.3*inch
        
        # Footer
        y = 1*inch
        # [IMPROVEMENT 2] Font Fix: Helvetica-Italic -> Helvetica-Oblique
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(1*inch, y, "Generated by BattingEdge AI Coaching System")
        c.drawString(1*inch, y - 0.15*inch, "For training purposes only. Consult a professional coach for personalized guidance.")
        
        c.save()
        print(f"  ✅ PDF saved: {pdf_path.name}")
        
    except ImportError:
        print("  ⚠️  reportlab not installed. Skipping PDF generation.")
        print("      Install with: pip install reportlab")
    except Exception as e:
        print(f"  ⚠️  PDF generation error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=" * 80)
    print("🎬 CREATING DEMO VIDEOS FROM UNPROFESSIONAL PLAYERS")
    print("=" * 80)
    print()
    
    # Check if directory exists
    if not RAW_CLIPS_DIR.exists():
        print(f"❌ Directory not found: {RAW_CLIPS_DIR}")
        print("   Please check the path and try again.")
        return
    
    # Find all video files
    video_files = []
    for ext in ['*.mp4', '*.avi', '*.mov', '*.MP4', '*.AVI', '*.MOV']:
        video_files.extend(RAW_CLIPS_DIR.glob(ext))
    
    if not video_files:
        print(f"❌ No video files found in {RAW_CLIPS_DIR}")
        return
    
    print(f"📹 Found {len(video_files)} videos to process")
    print()
    
    # Initialize classifier
    print("🧠 Loading model...")
    try:
        classifier = CricketShotClassifier()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    # Process each video
    results_summary = []
    
    for idx, video_path in enumerate(sorted(video_files), 1):
        print(f"\n{'='*80}")
        print(f"Processing Demo {idx}/{len(video_files)}: {video_path.name}")
        print('='*80)
        
        try:
            # Get video info
            video_info = get_video_info(video_path)
            print(f"  📊 Video info: {video_info['duration']:.1f}s, {video_info['resolution']}, {video_info['fps']:.0f} fps")
            
            # Run inference
            print("  🔍 Running analysis...")
            result = classifier.predict_video(str(video_path))
            
            if result and "error" not in result:
                # Enhance with human-readable advice
                result = enhance_result_with_advice(result)
                
                # Add video info to result
                result['video_info'] = video_info
                result['original_filename'] = video_path.name
                result['analysis_date'] = datetime.now().isoformat()
                
                # Extract key info
                shot = result['prediction']
                conf = result['confidence']
                score = result['form_analysis']['overall_score']
                
                print(f"  📊 Shot: {shot.upper()} ({conf:.1f}% confidence)")
                print(f"  📊 Form Score: {score}/100")
                
                # Generate filenames
                demo_name = f"demo{idx}"
                overlay_video = OUTPUT_DIR / f"{demo_name}.mp4"
                json_file = OUTPUT_DIR / f"{demo_name}.json"
                pdf_file = OUTPUT_DIR / f"{demo_name}.pdf"
                
                # 1. Create overlay video
                print("  🎨 Creating overlay video...")
                classifier.create_overlay(str(video_path), str(overlay_video), result)
                print(f"  ✅ Video saved: {overlay_video.name}")
                
                # 2. Save JSON
                print("  💾 Saving JSON...")
                with open(json_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"  ✅ JSON saved: {json_file.name}")
                
                # 3. Generate PDF
                print("  📄 Generating PDF report...")
                generate_pdf_report(result, video_path.name, pdf_file)
                
                # Add to summary
                results_summary.append({
                    'demo_number': idx,
                    'original_file': video_path.name,
                    'shot': shot,
                    'confidence': round(conf, 2),
                    'form_score': score,
                    'output_files': {
                        'video': overlay_video.name,
                        'json': json_file.name,
                        'pdf': pdf_file.name
                    }
                })
                
                print(f"  ✨ Demo {idx} completed successfully!")
                
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'Analysis failed'
                print(f"  ❌ Failed: {error_msg}")
                
        except Exception as e:
            print(f"  ❌ Error processing video: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate master summary JSON
    print(f"\n{'='*80}")
    print("📝 Generating master summary...")
    
    summary_json = {
        'generation_date': datetime.now().isoformat(),
        'total_demos': len(video_files),
        'successful': len(results_summary),
        'failed': len(video_files) - len(results_summary),
        'demos': results_summary,
        'statistics': {
            'avg_confidence': round(sum(r['confidence'] for r in results_summary) / len(results_summary), 2) if results_summary else 0,
            'avg_form_score': round(sum(r['form_score'] for r in results_summary) / len(results_summary), 2) if results_summary else 0,
            'shots_detected': {}
        }
    }
    
    # Count shots
    for r in results_summary:
        shot = r['shot']
        summary_json['statistics']['shots_detected'][shot] = \
            summary_json['statistics']['shots_detected'].get(shot, 0) + 1
    
    summary_path = OUTPUT_DIR / 'demo_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary_json, f, indent=2)
    
    print(f"✅ Summary saved: {summary_path.name}")
    
    # Print final summary
    print(f"\n{'='*80}")
    print("🎉 DEMO GENERATION COMPLETE!")
    print('='*80)
    print(f"\n📊 Summary:")
    print(f"  Total videos processed: {len(video_files)}")
    print(f"  Successful: {len(results_summary)}")
    print(f"  Failed: {len(video_files) - len(results_summary)}")
    print(f"\n  Average confidence: {summary_json['statistics']['avg_confidence']:.1f}%")
    print(f"  Average form score: {summary_json['statistics']['avg_form_score']:.1f}/100")
    print(f"\n  Shots detected:")
    for shot, count in summary_json['statistics']['shots_detected'].items():
        print(f"    - {shot.capitalize()}: {count}")
    
    print(f"\n📁 All outputs saved to: {OUTPUT_DIR}")
    print(f"   - {len(results_summary)} overlay videos (demo1.mp4, demo2.mp4, ...)")
    print(f"   - {len(results_summary)} JSON files (demo1.json, demo2.json, ...)")
    print(f"   - {len(results_summary)} PDF reports (demo1.pdf, demo2.pdf, ...)")
    print(f"   - 1 master summary (demo_summary.json)")
    
    print("\n✨ Ready for defense presentation!")
    print("="*80)

if __name__ == "__main__":
    main()