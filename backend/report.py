from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger("PDF_Report")

# ──────────────────────────────────────────────────────────────────────────────
# 1. COLOR DEFINITIONS
# ──────────────────────────────────────────────────────────────────────────────
NEON_BLUE_HEX    = '#00E5FF'
JET_BLACK_HEX    = '#0A0E1A'
DARK_SLATE_HEX   = '#1E293B'
SILVER_GRAY_HEX  = '#94A3B8'
SUCCESS_GREEN_HEX = '#10B981'
WARNING_ORANGE_HEX = '#F59E0B'
ERROR_RED_HEX    = '#EF4444'
LIGHT_BG_HEX     = '#F8FAFC'
WHITE_HEX        = '#FFFFFF'
FOOTER_GRAY_HEX  = '#A0A0A0'

C_NEON_BLUE  = colors.HexColor(NEON_BLUE_HEX)
C_JET_BLACK  = colors.HexColor(JET_BLACK_HEX)
C_DARK_SLATE = colors.HexColor(DARK_SLATE_HEX)
C_SILVER     = colors.HexColor(SILVER_GRAY_HEX)
C_LIGHT_BG   = colors.HexColor(LIGHT_BG_HEX)
C_WHITE      = colors.HexColor(WHITE_HEX)

# ──────────────────────────────────────────────────────────────────────────────
# 2. SHOT-SPECIFIC COACHING KNOWLEDGE
# ──────────────────────────────────────────────────────────────────────────────

SHOT_COACHING = {
    "COVER DRIVE": {
        "tagline": "The King of Elegant Shots",
        "key_cue": "Let the ball come to you. Drive through the line — not at it.",
        "players": "Babar Azam (textbook timing), Zaheer Abbas (Asian Bradman), Mohammad Yousuf (off-side mastery)",
        "common_mistakes": [
            ("Playing too early", "Wait until the ball is beneath your eyes before swinging. Rushing causes inside edges."),
            ("Bent leading elbow", "Keep the front arm fully extended at contact to maximise bat speed and control."),
            ("Falling to off-side", "Stay side-on and balanced — lunging causes the weight to shift the wrong way."),
            ("Closed bat face", "Ensure the bat face is square at impact, angled slightly downward (0–20°) to keep the ball along the ground."),
        ],
        "drill": "50 Shadow Drives Daily: Stand in front of a mirror, no ball. Execute full cover drives — check straight bat, high front elbow, and balanced head position at follow-through. Film yourself from the side.",
        "improvement_example": "If your elbow extension was below 120°: imagine you are reaching out to shake someone's hand while swinging — your arm must be nearly straight through contact.",
    },
    "PULL SHOT": {
        "tagline": "The Dominator of Short-Pitch Bowling",
        "key_cue": "Get inside the line. Pivot on the back foot. Roll the wrists to keep it down.",
        "players": "Javed Miandad (1986 Sharjah six), Babar Azam (wrist roll), Imran Khan (aggressive style)",
        "common_mistakes": [
            ("Getting hit on the body", "Move your back foot early to get inside the line of the ball — don't let it come to you."),
            ("Top-edging to fine leg", "Roll your wrists through the shot to angle the ball downward. Open hands at impact cause top edges."),
            ("Hitting the air", "Watch the ball onto the bat — short balls are deceptive. Pick up the length early."),
            ("Losing balance", "Plant the back foot firmly before swinging. A stable base gives you time to execute."),
        ],
        "drill": "Underarm Short-Ball Drill: Have a partner throw the ball at chest height from 5 metres. Focus on stepping inside the line and rolling wrists. Increase pace gradually.",
        "improvement_example": "If hip rotation was below 50°: think of your hips as a gate that swings open. The faster you open the gate, the more power transfers to the ball.",
    },
    "CUT SHOT": {
        "tagline": "The Punisher of Short, Wide Deliveries",
        "key_cue": "Stay tall, play late. The cut is about patience — wait for the short, wide ball.",
        "players": "Younis Khan (10,099 Test runs), Inzamam-ul-Haq (deceptive footwork), Saeed Anwar (elegant point placement)",
        "common_mistakes": [
            ("Playing on a good length", "The cut shot only works on a short-pitched ball outside off stump. Playing it on a good length is the most common mistake."),
            ("Reaching for the ball", "Allow the ball to come to you — reaching causes cramped swing and loss of power."),
            ("Moving head towards the ball", "Keep your head still and let the hands do the work. Head movement disrupts timing."),
            ("Flat bat at contact", "Angle the bat face at 70–100° to guide the ball through the point/gully area."),
        ],
        "drill": "Wall Rebound Cut Drill: Stand side-on to a wall and hit a tennis ball against it, letting it rebound at shoulder height. Play repeated cut shots focusing on high hands and staying tall.",
        "improvement_example": "If bat angle was outside 70–100°: imagine cutting with a knife — the blade angle determines where the ball goes. Tilt the bat face to the off side to control the direction.",
    },
    "SWEEP SHOT": {
        "tagline": "The Spin Killer",
        "key_cue": "Get to the pitch. Open your hips early. Front knee down. Swing along the ground.",
        "players": "Mohammad Hafeez (aggressive sweeper), Shoaib Malik (sub-continental dominance), Azhar Ali (patient accumulator)",
        "common_mistakes": [
            ("Front knee not bending", "The sweep requires you to get low. If the knee is too straight, the bat comes across too high and produces a top edge."),
            ("Playing against the spin", "Sweep with the spin, not against it, to control the ball direction."),
            ("Head falling back", "Head must stay forward and over the ball — head falling back causes the ball to go in the air."),
            ("Too horizontal a swing", "Keep the bat at 75–105° to the horizontal for a flat trajectory — too horizontal causes miscues."),
        ],
        "drill": "Knee-Down Sweep Drill: Kneel on one knee on a mat. Have a partner roll/bowl the ball slowly. Execute sweep shots focusing entirely on the bat path and keeping the ball along the ground.",
        "improvement_example": "If front knee bend was less than 130°: crouch lower on your initial step — like you're doing a lunge in the gym. The lower your position, the more control you have.",
    },
    "DEFENSE": {
        "tagline": "The Foundation of Every Great Innings",
        "key_cue": "Head over the ball. Soft hands. Bat face angled down — let the ball die at your feet.",
        "players": "Younis Khan (near-impenetrable defence), Hanif Mohammad (970-min innings), Mohammad Yousuf (perfect technique)",
        "common_mistakes": [
            ("Hard hands at impact", "Grip the bat firmly on the handle but relax the bottom hand through impact — the ball should drop dead."),
            ("Bat face square to ground", "Angle the bat face downward (0–15° from vertical) so the ball is smothered into the pitch, not deflected to slip."),
            ("Head falling away", "Head must be forward, directly above the ball — if it falls to leg side, bat follows and you're exposed to the straight one."),
            ("Front knee too stiff", "Bend into a long stride with the front knee pointing toward mid-on — this covers the ball's line and presents full bat face."),
        ],
        "drill": "Soft-Hands Throw-Down: Stand at the crease while a partner throws at you with a bag of balls. Focus solely on soft hands and letting the ball stop dead. If you hear a loud 'thwack', you're playing too hard.",
        "improvement_example": "If bat angle was greater than 15° from vertical: place a small piece of tape on the top of your bat. When defending, that tape should point toward the stumps — not the sky.",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# 3. ECB / MCC STANDARDS DATA
# ──────────────────────────────────────────────────────────────────────────────
ECB_STANDARDS = {
    "COVER DRIVE": [
        ("Elbow Extension",  "120–180°",           "Full arm extension drives power through the ball"),
        ("Head Stability",   "< 90 cm drift",         "Still head = eyes tracking = better timing"),
        ("Bat Angle",        "0–20° from vertical",  "Straight bat presents full face to ball"),
        ("Hip Rotation",     "40–140°",             "Core rotation transfers body weight into shot"),
    ],
    "PULL SHOT": [
        ("Hip Rotation",     "50–130°",             "Explosive hips are the power source for this shot"),
        ("Elbow Extension",  "115–180°",            "Full arm extension maximises leverage"),
        ("Head Position",    "< 75 cm drift",         "Stay inside ball line, watch onto bat"),
        ("Bat Path",         "60–120° horizontal",  "Flat swing connects cleanly with short ball"),
    ],
    "CUT SHOT": [
        ("Elbow Extension",  "90–175°",             "Wide arms create the cutting angle to point/gully"),
        ("Bat Angle",        "70–100°",             "Angled face guides ball into gap"),
        ("Head Stability",   "< 80 cm drift",         "Still head = timing; moving head = edge"),
        ("High Hands",       "Above shoulder at contact", "Prevents top edge, controls direction"),
    ],
    "SWEEP SHOT": [
        ("Front Knee Bend",  "130–175°",            "Low position gets bat under the ball"),
        ("Bat Horizontal",   "75–105°",             "Flat swing keeps ball along ground"),
        ("Head Over Ball",   "Forward press",          "Head forward = ball stays down"),
        ("Weight Forward",   "~80% front foot",        "Stability and control through the shot"),
    ],
    "DEFENSE": [
        ("Bat Vertical",     "0–15° from perpendicular", "Straight bat = safe block, no edges"),
        ("Soft Hands",       "Elbow flex 120–170°",       "Relaxed grip = ball drops dead at feet"),
        ("Head Over Ball",   "Forward press essential", "Head forward = bat and pad together"),
        ("Front Knee",       "140–180°",             "Long stride covers the line of the ball"),
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# 4. HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def safe(text: str) -> str:
    """XML-escape a string for use inside Paragraph() content."""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def truncate(text: str, limit: int = 150) -> str:
    text = str(text)
    return text[:limit] + "..." if len(text) > limit else text


def grade_color(grade: str) -> str:
    """Returns hex color string for grade letter."""
    if grade in ("A+", "A"):  return SUCCESS_GREEN_HEX
    if grade in ("B+", "B"):  return NEON_BLUE_HEX
    if grade in ("C+", "C"):  return WARNING_ORANGE_HEX
    return ERROR_RED_HEX


def _normalize_shot_key(prediction: str) -> str:
    """Normalise prediction string to match ECB_STANDARDS keys."""
    p = prediction.upper().strip()
    # handle variants
    if "COVER" in p or "DRIVE" in p:   return "COVER DRIVE"
    if "PULL"  in p:                   return "PULL SHOT"
    if "CUT"   in p:                   return "CUT SHOT"
    if "SWEEP" in p:                   return "SWEEP SHOT"
    if "DEFEN" in p:                   return "DEFENSE"
    return p


# ──────────────────────────────────────────────────────────────────────────────
# 5. CANVAS FOOTER — drawn on every page
# ──────────────────────────────────────────────────────────────────────────────

def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor(FOOTER_GRAY_HEX))
    footer_text = "BattingEdge AI Cricket Analysis  |  ECB & MCC Standards  |  © BattingEdge 2025"
    canvas.drawCentredString(letter[0] / 2.0, 0.3 * inch, footer_text)
    canvas.restoreState()


# ──────────────────────────────────────────────────────────────────────────────
# 6. MAIN PDF GENERATOR
# ──────────────────────────────────────────────────────────────────────────────

def generate_pdf(result, output_path):
    """Generate professional PDF coaching report with all ECB/MCC fixes."""
    try:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.6 * inch,
        )
        elements = []
        styles = getSampleStyleSheet()

        # ── Style upsert helper ──
        def upsert_style(name, parent, **kwargs):
            if name in styles:
                for k, v in kwargs.items():
                    setattr(styles[name], k, v)
            else:
                styles.add(ParagraphStyle(name=name, parent=parent, **kwargs))

        upsert_style('MainTitle', styles['Heading1'],
            fontSize=28, textColor=C_NEON_BLUE, spaceAfter=6, spaceBefore=0,
            fontName='Helvetica-Bold', alignment=TA_LEFT)

        upsert_style('Subtitle', styles['Normal'],
            fontSize=12, textColor=C_SILVER, spaceAfter=15,
            fontName='Helvetica', alignment=TA_LEFT)

        upsert_style('SectionHeader', styles['Heading2'],
            fontSize=14, textColor=C_JET_BLACK, spaceBefore=12, spaceAfter=8,
            fontName='Helvetica-Bold', borderWidth=1, borderColor=C_NEON_BLUE,
            borderPadding=6, backColor=C_LIGHT_BG, leftIndent=0)

        upsert_style('BodyText', styles['Normal'],
            fontSize=10, leading=14, spaceAfter=8, textColor=C_DARK_SLATE,
            fontName='Helvetica', alignment=TA_JUSTIFY)

        upsert_style('CellText', styles['Normal'],
            fontSize=9, leading=11, textColor=C_DARK_SLATE,
            fontName='Helvetica', wordWrap='CJK')

        upsert_style('ScoreText', styles['Normal'],
            fontSize=36, leading=36, fontName='Helvetica-Bold',
            alignment=TA_CENTER, spaceAfter=0)

        upsert_style('CoachHeader', styles['Normal'],
            fontSize=11, leading=13, fontName='Helvetica-Bold',
            textColor=C_JET_BLACK, spaceAfter=4)

        upsert_style('CoachBody', styles['Normal'],
            fontSize=9, leading=13, fontName='Helvetica',
            textColor=C_DARK_SLATE, spaceAfter=3)

        upsert_style('WarningText', styles['Normal'],
            fontSize=9, leading=12, fontName='Helvetica',
            textColor=colors.HexColor('#92400E'), spaceAfter=0)

        upsert_style('MistakeTitle', styles['Normal'],
            fontSize=9, leading=11, fontName='Helvetica-Bold',
            textColor=colors.HexColor(ERROR_RED_HEX), spaceAfter=1)

        upsert_style('MistakeBody', styles['Normal'],
            fontSize=8, leading=11, fontName='Helvetica',
            textColor=C_DARK_SLATE, spaceAfter=2)

        # ── Extract data ──
        form       = result.get('form_analysis', {})
        score      = form.get('overall_score', 65)
        performance = form.get('performance_level', 'Intermediate')
        shot_type  = result.get('prediction', 'Unknown')
        confidence = result.get('confidence', 0)
        grade      = form.get('grade', 'B')

        logger.info(f"[PDF] Generating: {shot_type} | Score {score} | Grade {grade}")

        # ── PAGE USABLE WIDTH: 7.3 inches (8.5 - 0.6*2 margins) ──
        USABLE = 7.3 * inch

        # ══════════════════════════════════════════════
        # SECTION 1 — HEADER  (logo left, title right)
        # ══════════════════════════════════════════════
        logo_path = Path(__file__).parent.parent / "frontend" / "public" / "be_logo.png"

        logo_cell = Spacer(1, 1)
        if logo_path.exists():
            try:
                logo_cell = Image(str(logo_path), width=1.0 * inch, height=1.0 * inch)
                logo_cell.hAlign = 'LEFT'
            except Exception as e:
                logger.warning(f"[PDF] Logo load warning: {e}")

        meta_html = (
            f"<font size='14'><b>{safe(shot_type.upper())}</b></font>  "
            f"<font size='12' color='{SILVER_GRAY_HEX}'>(Confidence: {confidence:.1f}%)</font><br/>"
            f"<font size='10' color='#64748B'>{datetime.now().strftime('%B %d, %Y')}</font>"
        )
        title_para = Paragraph("BATTINGEDGE ANALYSIS", styles['MainTitle'])
        meta_para  = Paragraph(meta_html, styles['Subtitle'])

        # colWidths: 1.2 + 5.8 = 7.0 in ✓
        header_table = Table([[logo_cell, [title_para, meta_para]]],
                             colWidths=[1.2 * inch, 5.8 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(header_table)

        # Divider line — 7 in ✓
        divider = Table([['']], colWidths=[7 * inch])
        divider.setStyle(TableStyle([
            ('LINEABOVE',     (0, 0), (-1, 0), 2, C_NEON_BLUE),
            ('TOPPADDING',    (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(divider)
        elements.append(Spacer(1, 0.1 * inch))

        # ── Recording quality notice ──
        warning_bg   = colors.HexColor('#FFFBEB')
        warning_bord = colors.HexColor('#F59E0B')
        warn_para = Paragraph(
            "<b>⚠ Recording Accuracy Notice:</b> Results depend on video quality. "
            "For best accuracy, record <b>side-on</b> (bowler's view) with full body "
            "visible head to toe in good lighting. Front/back-on angles significantly "
            "reduce prediction accuracy.",
            styles['WarningText']
        )
        warn_table = Table([[warn_para]], colWidths=[7 * inch])
        warn_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), warning_bg),
            ('BOX',           (0, 0), (-1, -1), 1, warning_bord),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ]))
        elements.append(warn_table)
        elements.append(Spacer(1, 0.15 * inch))

        # ══════════════════════════════════════════════
        # SECTION 2 — SCORE BOX + GRADE
        # ══════════════════════════════════════════════
        if score >= 85:
            score_hex = SUCCESS_GREEN_HEX
            box_bg    = colors.HexColor('#ECFDF5')
            box_border = colors.HexColor(SUCCESS_GREEN_HEX)
        elif score >= 70:
            score_hex = NEON_BLUE_HEX
            box_bg    = colors.HexColor('#EFF6FF')
            box_border = colors.HexColor(NEON_BLUE_HEX)
        elif score >= 55:
            score_hex = WARNING_ORANGE_HEX
            box_bg    = colors.HexColor('#FFFBEB')
            box_border = colors.HexColor(WARNING_ORANGE_HEX)
        else:
            score_hex = ERROR_RED_HEX
            box_bg    = colors.HexColor('#FEF2F2')
            box_border = colors.HexColor(ERROR_RED_HEX)

        g_color = grade_color(grade)

        score_para = Paragraph(
            f"<font color='{score_hex}'>{score}</font>"
            f"<font size='18' color='{g_color}'>  {safe(grade)}</font>",
            styles['ScoreText']
        )
        perf_style = ParagraphStyle('_perf', parent=styles['Subtitle'], alignment=TA_CENTER)
        perf_para  = Paragraph(f"<b>{safe(performance)}</b>", perf_style)

        # Score table — 7 in ✓
        score_table = Table([[score_para], [perf_para]], colWidths=[7 * inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), box_bg),
            ('BOX',           (0, 0), (-1, -1), 2, box_border),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 0.2 * inch))

        # ══════════════════════════════════════════════
        # SECTION 3 — ECB/MCC STANDARDS TABLE  (Fix 4)
        # ══════════════════════════════════════════════
        shot_key  = _normalize_shot_key(shot_type)
        standards = ECB_STANDARDS.get(shot_key, [])

        if standards:
            group = []
            group.append(Paragraph(
                f"{safe(shot_type.title())} Technical Standards (ECB/MCC)",
                styles['SectionHeader']
            ))

            # Header row
            std_data = [[
                Paragraph('<b>Criterion</b>',       styles['CellText']),
                Paragraph('<b>ECB/MCC Standard</b>', styles['CellText']),
                Paragraph('<b>What This Means</b>',  styles['CellText']),
            ]]
            for criterion, standard, meaning in standards:
                std_data.append([
                    Paragraph(safe(criterion), styles['CellText']),
                    Paragraph(safe(standard),  styles['CellText']),
                    Paragraph(safe(meaning),   styles['CellText']),
                ])

            # colWidths: 1.8 + 1.5 + 4.0 = 7.3 in ✓
            std_table = Table(std_data, colWidths=[1.8 * inch, 1.5 * inch, 4.0 * inch])
            std_table.setStyle(TableStyle([
                # Header row — light blue background with dark text for readability
                ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR',     (0, 0), (-1, 0), colors.HexColor('#1A1A2E')),
                ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('TOPPADDING',    (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                # Alternating data rows: white / #F8FAFC
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_WHITE, C_LIGHT_BG]),
                # All cells
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 8),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
                ('TOPPADDING',    (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID',          (0, 0), (-1, -1), 0.5, C_SILVER),
            ]))
            group.append(std_table)
            elements.append(KeepTogether(group))
            elements.append(Spacer(1, 0.2 * inch))

        # ══════════════════════════════════════════════
        # SECTION 4 — COACH'S SUMMARY
        # ══════════════════════════════════════════════
        elements.append(Paragraph("Coach's Assessment", styles['SectionHeader']))
        summary = form.get('summary', 'Analysis completed.')
        elements.append(Paragraph(safe(summary), styles['BodyText']))
        elements.append(Spacer(1, 0.2 * inch))

        # ══════════════════════════════════════════════
        # SECTION 5 — STRENGTHS & IMPROVEMENTS  (Fix 6)
        # ══════════════════════════════════════════════
        strengths    = form.get('strengths', [])
        improvements = form.get('key_improvements', [])

        if strengths or improvements:
            col_data = [[
                Paragraph("<b>Strengths</b>",   styles['BodyText']),
                Paragraph("<b>Focus Areas</b>", styles['BodyText']),
            ]]
            max_rows = max(len(strengths[:3]), len(improvements[:3]))
            for i in range(max_rows):
                left_text = right_text = ""
                if i < len(strengths[:3]):
                    left_text = f"<bullet>&#x2713;</bullet> {safe(truncate(strengths[i]))}"
                if i < len(improvements[:3]):
                    right_text = f"<bullet>&#x2022;</bullet> {safe(truncate(improvements[i]))}"
                col_data.append([
                    Paragraph(left_text,  styles['BodyText']),
                    Paragraph(right_text, styles['BodyText']),
                ])

            # colWidths: 3.4 + 3.4 = 6.8 in ✓
            col_table = Table(col_data, colWidths=[3.4 * inch, 3.4 * inch])
            col_table.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR',     (0, 0), (-1, 0), colors.HexColor('#1A1A2E')),
                ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING',    (0, 0), (-1, 0), 8),
                ('LINEBELOW',     (0, 0), (-1, 0), 1.5, C_NEON_BLUE),
                ('VALIGN',        (0, 1), (-1, -1), 'TOP'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 10),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
                ('TOPPADDING',    (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID',          (0, 0), (-1, -1), 0.5, C_SILVER),
            ]))
            elements.append(KeepTogether(col_table))
            elements.append(Spacer(1, 0.25 * inch))

        # ══════════════════════════════════════════════
        # SECTION 6 — BIOMECHANICAL DATA  (Fix 5)
        # ══════════════════════════════════════════════
        checks = form.get('checks', [])
        if checks:
            group = []
            group.append(Paragraph("Biomechanical Data", styles['SectionHeader']))

            table_data = [[
                Paragraph('<b>Metric</b>',     styles['CellText']),
                Paragraph('<b>Your Value</b>', styles['CellText']),
                Paragraph('<b>Ideal Range</b>', styles['CellText']),
                Paragraph('<b>Rating</b>',     styles['CellText']),
                Paragraph('<b>Advice</b>',     styles['CellText']),
            ]]

            for check in checks:
                try:
                    name_str   = check.get('name', '-')
                    value_str  = str(check.get('value', '-'))
                    range_str  = str(check.get('ideal_range', '-'))
                    advice_str = str(check.get('advice', ''))
                    status_str = check.get('status', 'Unknown')

                    # Fix 5 — personalized advice with measured value
                    personalized = (
                        f"Your {name_str.lower()} measured {value_str} "
                        f"— ideal is {range_str}. {advice_str}"
                    )

                    # Rating color
                    if status_str == 'Excellent':  s_hex = SUCCESS_GREEN_HEX
                    elif status_str == 'Good':      s_hex = NEON_BLUE_HEX
                    elif status_str == 'Acceptable': s_hex = WARNING_ORANGE_HEX
                    else:                           s_hex = ERROR_RED_HEX

                    table_data.append([
                        Paragraph(safe(name_str),   styles['CellText']),
                        Paragraph(safe(value_str),  styles['CellText']),
                        Paragraph(safe(range_str),  styles['CellText']),
                        Paragraph(
                            f"<font color='{s_hex}'><b>{safe(status_str)}</b></font>",
                            styles['CellText']
                        ),
                        Paragraph(safe(personalized), styles['CellText']),
                    ])
                except Exception:
                    continue

            # colWidths: 1.3 + 0.8 + 1.1 + 0.9 + 2.9 = 7.0 in ✓
            bio_table = Table(table_data,
                              colWidths=[1.3*inch, 0.8*inch, 1.1*inch, 0.9*inch, 2.9*inch])
            bio_table.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR',     (0, 0), (-1, 0), colors.HexColor('#1A1A2E')),
                ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING',    (0, 0), (-1, 0), 8),
                ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 6),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
                ('GRID',          (0, 1), (-1, -1), 0.5, C_SILVER),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_WHITE, C_LIGHT_BG]),
            ]))
            group.append(bio_table)
            elements.append(KeepTogether(group))
            elements.append(Spacer(1, 0.25 * inch))

        # ══════════════════════════════════════════════
        # SECTION 7 — RECOMMENDED DRILLS
        # ══════════════════════════════════════════════
        drills = form.get('recommended_drills', [])
        if drills:
            group = []
            group.append(Paragraph("Recommended Drills", styles['SectionHeader']))
            for i, drill in enumerate(drills[:3], 1):
                try:
                    if isinstance(drill, dict):
                        d_name = drill.get('name', f'Drill {i}')
                        d_desc = drill.get('description', '')
                    else:
                        d_name = f'Drill {i}'
                        d_desc = str(drill)
                    drill_html = f"<b>{i}. {safe(d_name)}:</b> {safe(d_desc)}"
                    group.append(Paragraph(drill_html, styles['BodyText']))
                    group.append(Spacer(1, 0.1 * inch))
                except Exception:
                    continue
            elements.append(KeepTogether(group))

        # ══════════════════════════════════════════════
        # SECTION 8 — SHOT-SPECIFIC COACHING GUIDE
        # ══════════════════════════════════════════════
        coaching = SHOT_COACHING.get(shot_key)
        if coaching:
            group = []
            group.append(Paragraph("Shot-Specific Coaching Guide", styles['SectionHeader']))

            # Tagline + key cue
            tagline_para = Paragraph(
                f"<b>{safe(coaching['tagline'])}</b>",
                ParagraphStyle('_tl', parent=styles['BodyText'],
                               textColor=C_NEON_BLUE, fontSize=11, spaceAfter=4)
            )
            cue_para = Paragraph(
                f"<b>Key Coaching Cue:</b> {safe(coaching['key_cue'])}",
                styles['CoachBody']
            )
            players_para = Paragraph(
                f"<b>Players to study:</b> {safe(coaching['players'])}",
                ParagraphStyle('_pl', parent=styles['CoachBody'], textColor=C_SILVER)
            )
            group.append(tagline_para)
            group.append(cue_para)
            group.append(players_para)
            group.append(Spacer(1, 0.12 * inch))

            # Common mistakes table
            group.append(Paragraph("<b>Common Mistakes &amp; How to Fix Them:</b>", styles['CoachBody']))
            group.append(Spacer(1, 0.05 * inch))

            mistake_data = [[
                Paragraph('<b>Mistake</b>', styles['CellText']),
                Paragraph('<b>How to Fix It</b>', styles['CellText']),
            ]]
            for mistake, fix in coaching['common_mistakes']:
                mistake_data.append([
                    Paragraph(f"<font color='{ERROR_RED_HEX}'>{safe(mistake)}</font>", styles['CellText']),
                    Paragraph(safe(fix), styles['CellText']),
                ])

            mistake_table = Table(mistake_data, colWidths=[2.2 * inch, 5.1 * inch])
            mistake_table.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR',     (0, 0), (-1, 0), colors.HexColor('#1A1A2E')),
                ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('TOPPADDING',    (0, 0), (-1, 0), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_WHITE, C_LIGHT_BG]),
                ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING',   (0, 0), (-1, -1), 8),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
                ('TOPPADDING',    (0, 1), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('GRID',          (0, 0), (-1, -1), 0.5, C_SILVER),
            ]))
            group.append(mistake_table)
            group.append(Spacer(1, 0.12 * inch))

            # Recommended drill
            drill_bg = colors.HexColor('#EFF6FF')
            drill_para = Paragraph(
                f"<b>Training Drill:</b> {safe(coaching['drill'])}",
                styles['CoachBody']
            )
            drill_table = Table([[drill_para]], colWidths=[7 * inch])
            drill_table.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, -1), drill_bg),
                ('BOX',           (0, 0), (-1, -1), 1.5, C_NEON_BLUE),
                ('TOPPADDING',    (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING',   (0, 0), (-1, -1), 12),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
            ]))
            group.append(drill_table)
            group.append(Spacer(1, 0.08 * inch))

            # Improvement example
            example_bg = colors.HexColor('#F0FDF4')
            example_bord = colors.HexColor(SUCCESS_GREEN_HEX)
            example_para = Paragraph(
                f"<b>Improvement Tip:</b> {safe(coaching['improvement_example'])}",
                ParagraphStyle('_eg', parent=styles['CoachBody'],
                               textColor=colors.HexColor('#065F46'))
            )
            example_table = Table([[example_para]], colWidths=[7 * inch])
            example_table.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, -1), example_bg),
                ('BOX',           (0, 0), (-1, -1), 1.5, example_bord),
                ('TOPPADDING',    (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING',   (0, 0), (-1, -1), 12),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
            ]))
            group.append(example_table)

            elements.append(KeepTogether(group))
            elements.append(Spacer(1, 0.2 * inch))

        # ══════════════════════════════════════════════
        # SECTION 9 — GENERAL COACHING FOOTER
        # ══════════════════════════════════════════════
        general_bg   = colors.HexColor('#F8FAFC')
        general_bord = colors.HexColor('#CBD5E1')
        general_tips = [
            "Record from the side (bowler's view) with full body visible for best AI accuracy.",
            "Practice shadow shots daily — technical muscle memory is built without a ball.",
            "Film every session. Progress is invisible without comparison.",
            "Consistent grip pressure matters: firm top hand, relaxed bottom hand.",
            "Always warm up with forward defensive blocks before playing attacking shots.",
        ]
        tip_rows = [[Paragraph(f"• {safe(t)}", styles['CoachBody'])] for t in general_tips]
        general_table = Table(
            [[Paragraph("<b>General Coaching Principles</b>", styles['SectionHeader'])]] + tip_rows,
            colWidths=[7 * inch]
        )
        general_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), C_LIGHT_BG),
            ('BACKGROUND',    (0, 1), (-1, -1), general_bg),
            ('BOX',           (0, 0), (-1, -1), 1, general_bord),
            ('LINEBELOW',     (0, 0), (-1, 0), 1.5, C_NEON_BLUE),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(general_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Build — canvas footer runs on every page
        doc.build(elements, onFirstPage=_draw_footer, onLaterPages=_draw_footer)

        logger.info(f"[PDF] Generated successfully: {Path(output_path).name}")
        return True

    except Exception as e:
        logger.error(f"[PDF] Generation failed: {e}", exc_info=True)
        return False
