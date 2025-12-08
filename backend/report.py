from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import logging

logger = logging.getLogger("PDF_Report")

# Static Reference Data for the "Textbook Criteria" Section
TEXTBOOK_CRITERIA = [
    ("Front Elbow", "120° - 140°", "Ensures maximum leverage and bat speed."),
    ("Head Stability", "< 10cm drift", "Maintains balance and eye-line on the ball."),
    ("Back Foot", "< 5cm lift", "Anchors the base for power transfer."),
    ("Hip Rotation", "> 30° (Drive) / > 60° (Pull)", "Generates explosive power from the core."),
    ("Follow Through", "Hands > Shoulders", "Guarantees acceleration through impact.")
]

def draw_wrapped_text(canvas_obj, text, x, y, max_width, line_height=14):
    if not text: return y
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if canvas_obj.stringWidth(test_line) < max_width:
            line = test_line
        else:
            canvas_obj.drawString(x, y, line)
            y -= line_height
            line = word + " "
    if line:
        canvas_obj.drawString(x, y, line)
        y -= line_height
    return y

def generate_pdf(result, output_path):
    try:
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        
        # --- COLORS ---
        DARK_BLUE = colors.Color(0.04, 0.05, 0.1) 
        LIGHT_GRAY = colors.Color(0.95, 0.95, 0.95)
        
        # --- HEADER ---
        c.setFillColor(DARK_BLUE)
        c.rect(0, height - 1.2*inch, width, 1.2*inch, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(0.5*inch, height - 0.7*inch, "BattingEdge Performance Report")
        
        c.setFont("Helvetica", 10)
        date_str = datetime.now().strftime('%B %d, %Y')
        c.drawRightString(width - 0.5*inch, height - 0.7*inch, f"Generated: {date_str}")
        
        y_pos = height - 1.8*inch

        # --- SCORE & GRADE ---
        form = result.get('form_analysis', {})
        score = form.get('overall_score', 0)
        
        if score >= 80: 
            grade = "A"; grade_color = colors.green; grade_txt = "PRO LEVEL"
        elif score >= 60: 
            grade = "B"; grade_color = colors.orange; grade_txt = "INTERMEDIATE"
        else: 
            grade = "C"; grade_color = colors.red; grade_txt = "NEEDS WORK"

        # Score Card Box
        c.setStrokeColor(colors.lightgrey)
        c.roundRect(0.5*inch, y_pos - 1*inch, width - 1*inch, 1*inch, 8, fill=0, stroke=1)
        
        # Shot Info (Left)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.7*inch, y_pos - 0.3*inch, "SHOT CLASSIFICATION")
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(DARK_BLUE)
        c.drawString(0.7*inch, y_pos - 0.6*inch, result.get('prediction', 'Unknown').upper())
        
        # Grade (Right)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawRightString(width - 0.7*inch, y_pos - 0.3*inch, "TECHNIQUE SCORE")
        c.setFont("Helvetica-Bold", 30)
        c.setFillColor(grade_color)
        c.drawRightString(width - 0.7*inch, y_pos - 0.7*inch, f"{score} / 100")
        
        y_pos -= 1.4*inch

        # --- COACHING SUMMARY ---
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(0.5*inch, y_pos, "COACH'S SUMMARY")
        y_pos -= 0.3*inch
        
        c.setFont("Helvetica", 11)
        summary = form.get('summary', "No summary.")
        y_pos = draw_wrapped_text(c, summary, 0.5*inch, y_pos, width - 1*inch)
        y_pos -= 0.4*inch

        # --- ANALYSIS BREAKDOWN ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.5*inch, y_pos, "DETAILED BIOMECHANICS")
        y_pos -= 0.2*inch
        
        checks = form.get('checks', [])
        for i, check in enumerate(checks):
            # Page Break Check
            if y_pos < 3.5*inch: # Leave space for footer table
                c.showPage()
                y_pos = height - 1*inch
            
            # Row Background
            if i % 2 == 0:
                c.setFillColor(LIGHT_GRAY)
                c.rect(0.5*inch, y_pos - 0.5*inch, width - 1*inch, 0.6*inch, fill=1, stroke=0)
            
            is_error = check.get('is_error', False)
            icon = "X" if is_error else "OK"
            color = colors.red if is_error else colors.green
            
            # Icon & Name
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(color)
            c.drawString(0.6*inch, y_pos, f"[{icon}] {check.get('name', '')}")
            
            # Measured Value (Technical Data)
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawRightString(width - 0.6*inch, y_pos, f"Value: {check.get('value', '')}")
            
            # Advice (Human Readable)
            y_pos -= 0.2*inch
            c.setFont("Helvetica-Oblique", 10)
            c.setFillColor(colors.darkgrey)
            advice = check.get('advice', 'Good form.')
            c.drawString(0.8*inch, y_pos, f"Feedback: {advice}")
            
            y_pos -= 0.4*inch

        # --- TEXTBOOK CRITERIA REFERENCE (The "Cheat Sheet") ---
        # Draw this at the bottom of the page
        y_bottom = 2.5*inch 
        if y_pos < y_bottom: 
            c.showPage()
            y_bottom = height - 3*inch

        c.setStrokeColor(DARK_BLUE)
        c.setLineWidth(1.5)
        c.line(0.5*inch, y_bottom + 0.2*inch, width - 0.5*inch, y_bottom + 0.2*inch)
        
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(DARK_BLUE)
        c.drawString(0.5*inch, y_bottom, "REFERENCE: TEXTBOOK CRICKET CRITERIA")
        
        y_ref = y_bottom - 0.3*inch
        c.setFont("Helvetica", 9)
        
        # Table Header
        c.drawString(0.5*inch, y_ref, "METRIC")
        c.drawString(2.5*inch, y_ref, "IDEAL RANGE")
        c.drawString(4.5*inch, y_ref, "WHY IT MATTERS")
        y_ref -= 0.1*inch
        c.setLineWidth(0.5)
        c.line(0.5*inch, y_ref, width - 0.5*inch, y_ref)
        y_ref -= 0.2*inch

        for item in TEXTBOOK_CRITERIA:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(0.5*inch, y_ref, item[0])
            c.setFont("Helvetica", 9)
            c.drawString(2.5*inch, y_ref, item[1])
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(4.5*inch, y_ref, item[2])
            y_ref -= 0.2*inch

        c.save()
        logger.info(f"PDF Generated: {output_path.name}")
        return True
    except Exception as e:
        logger.error(f"PDF Error: {e}")
        return False