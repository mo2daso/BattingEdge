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

# ==========================================
# 1. COLOR DEFINITIONS (SAFE MODE)
# ==========================================
# STRINGS (For XML tags like <font color="...">)
NEON_BLUE_HEX = '#00E5FF'
JET_BLACK_HEX = '#0A0E1A'
DARK_SLATE_HEX = '#1E293B'
SILVER_GRAY_HEX = '#94A3B8'
SUCCESS_GREEN_HEX = '#10B981'
WARNING_ORANGE_HEX = '#F59E0B'
ERROR_RED_HEX = '#EF4444'
LIGHT_BG_HEX = '#F8FAFC'
WHITE_HEX = '#FFFFFF'

# OBJECTS (For Table Styles)
C_NEON_BLUE = colors.HexColor(NEON_BLUE_HEX)
C_JET_BLACK = colors.HexColor(JET_BLACK_HEX)
C_DARK_SLATE = colors.HexColor(DARK_SLATE_HEX)
C_SILVER_GRAY = colors.HexColor(SILVER_GRAY_HEX)
C_LIGHT_BG = colors.HexColor(LIGHT_BG_HEX)
C_WHITE = colors.HexColor(WHITE_HEX)

# ==========================================
# 2. SHOT STANDARDS DATA
# ==========================================
SHOT_CRITERIA = {
    'cover drive': {
        'key_points': [
            'Elbow Extension: 120-180 degrees at contact',
            'Head Stability: <90cm drift from stance',
            'Bat Angle: 0-20 degrees from vertical',
            'Hip Rotation: 40-140 degrees through shot'
        ]
    },
    'pull shot': {
        'key_points': [
            'Hip Rotation: 50-130 degrees (critical for power)',
            'Elbow Extension: 115-180 degrees for leverage',
            'Head Position: Inside line, <75cm drift',
            'Bat Path: Horizontal (60-120 degrees)'
        ]
    },
    'cut shot': {
        'key_points': [
            'Elbow Extension: 90-175 degrees (width)',
            'Bat Angle: 70-100 degrees to guide square',
            'Head Stability: <80cm drift',
            'High Hands: Critical for control'
        ]
    },
    'sweep shot': {
        'key_points': [
            'Low Position: Front knee bent (130-175 degrees)',
            'Bat Angle: Horizontal (75-105 degrees)',
            'Head Over Ball: Critical for control',
            'Weight Forward: 80% on front leg'
        ]
    },
    'defense': {
        'key_points': [
            'Vertical Bat: 0-15 degrees from perpendicular',
            'Soft Hands: Slight elbow flex (120-170 degrees)',
            'Head Over Ball: Forward press essential',
            'Front Knee: Stride forward (140-180 degrees)'
        ]
    }
}

def generate_pdf(result, output_path):
    """
    Generate professional PDF with enhanced visual design (Robust Version)
    """
    try:
        doc = SimpleDocTemplate(
            str(output_path), 
            pagesize=letter,
            rightMargin=0.6*inch, 
            leftMargin=0.6*inch,
            topMargin=0.5*inch, 
            bottomMargin=0.6*inch
        )
        elements = []
        styles = getSampleStyleSheet()
        
        # Helper to safely add or update styles
        def upsert_style(name, parent, **kwargs):
            if name in styles:
                style = styles[name]
                for k, v in kwargs.items():
                    setattr(style, k, v)
            else:
                styles.add(ParagraphStyle(name=name, parent=parent, **kwargs))

        # ==========================================
        # CUSTOM STYLES (Safe Upsert)
        # ==========================================
        upsert_style('MainTitle', styles['Heading1'],
            fontSize=28,
            textColor=C_NEON_BLUE,
            spaceAfter=6,
            spaceBefore=0,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT  # Changed to LEFT to match logo
        )
        
        upsert_style('Subtitle', styles['Normal'],
            fontSize=12,
            textColor=C_SILVER_GRAY,
            spaceAfter=15,
            fontName='Helvetica',
            alignment=TA_LEFT # Changed to LEFT
        )
        
        upsert_style('SectionHeader', styles['Heading2'],
            fontSize=14,
            textColor=C_JET_BLACK,
            spaceBefore=12,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=C_NEON_BLUE,
            borderPadding=6,
            backColor=C_LIGHT_BG,
            leftIndent=0
        )
        
        upsert_style('BodyText', styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=8,
            textColor=C_DARK_SLATE,
            fontName='Helvetica',
            alignment=TA_JUSTIFY
        )
        
        upsert_style('CellText', styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=C_DARK_SLATE,
            fontName='Helvetica',
            wordWrap='CJK'
        )
        
        upsert_style('CriteriaPoint', styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=C_DARK_SLATE,
            fontName='Helvetica',
            leftIndent=12,
            bulletIndent=6
        )
        
        upsert_style('ScoreText', styles['Normal'],
            fontSize=36,
            leading=36, # Tight leading to move closer to text below
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=0
        )
        
        # ==========================================
        # EXTRACT DATA
        # ==========================================
        form = result.get('form_analysis', {})
        score = form.get('overall_score', 65)
        performance = form.get('performance_level', 'Intermediate')
        shot_type = result.get('prediction', 'Unknown')
        confidence = result.get('confidence', 0)
        
        logger.info(f"Generating PDF: {shot_type} - Score {score}%")
        
        # ==========================================
        # 1. HEADER (LOGO LEFT, BIGGER META)
        # ==========================================
        logo_path = Path(__file__).parent.parent / "frontend" / "public" / "logo.png"
        
        header_data = []
        
        # Left Column: Logo
        if logo_path.exists():
            try:
                # Use KeepAspectRatio logic if needed, but simple Image is safer
                im = Image(str(logo_path), width=1.0*inch, height=1.0*inch)
                im.hAlign = 'LEFT'
                header_data.append(im)
            except Exception as e:
                logger.warning(f"Logo load warning: {e}")
                header_data.append(Spacer(1, 1)) # Placeholder
        else:
            header_data.append(Spacer(1, 1))

        # Right Column: Title and Meta
        meta_html = (
            f"<font size='14'><b>{shot_type.upper()}</b></font>  "
            f"<font size='12' color='#94A3B8'>(Confidence: {confidence:.1f}%)</font><br/>"
            f"<font size='10' color='#64748B'>{datetime.now().strftime('%B %d, %Y')}</font>"
        )
        
        title_para = Paragraph("BATTINGEDGE ANALYSIS", styles['MainTitle'])
        meta_para = Paragraph(meta_html, styles['Subtitle'])
        
        # Use a table to align Logo Left and Text Left next to it
        header_table = Table([[header_data[0], [title_para, meta_para]]], colWidths=[1.2*inch, 5.8*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(header_table)
        
        # Divider line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,0), 2, C_NEON_BLUE),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # ==========================================
        # 2. PERFORMANCE SCORE BOX (COMPACT)
        # ==========================================
        # Determine colors (Safe Hex Strings)
        if score >= 85:
            score_hex = SUCCESS_GREEN_HEX
            box_bg_obj = colors.HexColor('#ECFDF5')
            box_border_obj = colors.HexColor(SUCCESS_GREEN_HEX)
        elif score >= 70:
            score_hex = NEON_BLUE_HEX
            box_bg_obj = colors.HexColor('#EFF6FF')
            box_border_obj = colors.HexColor(NEON_BLUE_HEX)
        elif score >= 55:
            score_hex = WARNING_ORANGE_HEX
            box_bg_obj = colors.HexColor('#FFFBEB')
            box_border_obj = colors.HexColor(WARNING_ORANGE_HEX)
        else:
            score_hex = ERROR_RED_HEX
            box_bg_obj = colors.HexColor('#FEF2F2')
            box_border_obj = colors.HexColor(ERROR_RED_HEX)
        
        # Content
        score_para = Paragraph(f"<font color='{score_hex}'>{score}</font>", styles['ScoreText'])
        perf_para = Paragraph(f"<b>{performance}</b>", styles['Subtitle'])
        perf_para.style.alignment = TA_CENTER # Ensure center
        
        score_data = [[score_para], [perf_para]]
        score_table = Table(score_data, colWidths=[7*inch])
        
        # TIGHTER PADDING
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), box_bg_obj),
            ('BOX', (0,0), (-1,-1), 2, box_border_obj),
            ('TOPPADDING', (0,0), (-1,-1), 6),    # Reduced from 18
            ('BOTTOMPADDING', (0,0), (-1,-1), 8), # Reduced from 18
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # ==========================================
        # 3. SHOT STANDARDS (KEPT TOGETHER)
        # ==========================================
        shot_key = shot_type.lower()
        criteria = SHOT_CRITERIA.get(shot_key, {})
        
        if criteria:
            group_elements = []
            group_elements.append(Paragraph(f"{shot_type.title()} Standards", styles['SectionHeader']))
            for point in criteria.get('key_points', []):
                clean_point = str(point).replace('&', 'and').replace('<', '&lt;')
                bullet = f"<bullet>&bull;</bullet> {clean_point}"
                group_elements.append(Paragraph(bullet, styles['CriteriaPoint']))
            
            elements.append(KeepTogether(group_elements))
            elements.append(Spacer(1, 0.2*inch))
        
        # ==========================================
        # 4. COACH'S SUMMARY
        # ==========================================
        elements.append(Paragraph("Coach's Assessment", styles['SectionHeader']))
        
        summary = form.get('summary', 'Analysis completed.')
        summary_safe = str(summary).replace('&', '&amp;').replace('<', '&lt;')
        elements.append(Paragraph(summary_safe, styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        # ==========================================
        # 5. STRENGTHS & FOCUS AREAS (SIDE BY SIDE)
        # ==========================================
        strengths = form.get('strengths', [])
        improvements = form.get('key_improvements', [])
        
        if strengths or improvements:
            group_elements = []
            col_data = []
            
            # Header
            col_data.append([
                Paragraph("<b>Strengths</b>", styles['BodyText']),
                Paragraph("<b>Focus Areas</b>", styles['BodyText'])
            ])
            
            max_rows = max(len(strengths[:3]), len(improvements[:3]))
            for i in range(max_rows):
                left_text, right_text = "", ""
                
                if i < len(strengths[:3]):
                    safe_text = str(strengths[i]).replace('&', '&amp;').replace('<', '&lt;')
                    left_text = f"<bullet>✓</bullet> {safe_text}"
                
                if i < len(improvements[:3]):
                    safe_text = str(improvements[i]).replace('&', '&amp;').replace('<', '&lt;')
                    right_text = f"<bullet>•</bullet> {safe_text}"
                
                col_data.append([
                    Paragraph(left_text, styles['BodyText']),
                    Paragraph(right_text, styles['BodyText'])
                ])
            
            col_table = Table(col_data, colWidths=[3.4*inch, 3.4*inch])
            col_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), C_LIGHT_BG),
                ('TEXTCOLOR', (0,0), (-1,0), C_JET_BLACK),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('TOPPADDING', (0,0), (-1,0), 8),
                ('LINEBELOW', (0,0), (-1,0), 1.5, C_NEON_BLUE),
                ('VALIGN', (0,1), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ('TOPPADDING', (0,1), (-1,-1), 6),
                ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, C_SILVER_GRAY),
            ]))
            
            # Keep table together
            elements.append(KeepTogether(col_table))
            elements.append(Spacer(1, 0.25*inch))
        
        # ==========================================
        # 6. BIOMECHANICAL DATA (KEPT TOGETHER)
        # ==========================================
        checks = form.get('checks', [])
        if checks:
            group_elements = []
            group_elements.append(Paragraph("Biomechanical Data", styles['SectionHeader']))
            
            table_data = [[
                Paragraph('<b>Metric</b>', styles['CellText']),
                Paragraph('<b>Value</b>', styles['CellText']),
                Paragraph('<b>Target</b>', styles['CellText']),
                Paragraph('<b>Rating</b>', styles['CellText']),
                Paragraph('<b>Advice</b>', styles['CellText'])
            ]]
            
            for check in checks:
                try:
                    name = Paragraph(str(check.get('name', '-')), styles['CellText'])
                    value = Paragraph(str(check.get('value', '-')), styles['CellText'])
                    target = Paragraph(str(check.get('ideal_range', '-')), styles['CellText'])
                    
                    status_text = check.get('status', 'Unknown')
                    if status_text == 'Excellent': s_hex = SUCCESS_GREEN_HEX
                    elif status_text == 'Good': s_hex = NEON_BLUE_HEX
                    elif status_text == 'Acceptable': s_hex = WARNING_ORANGE_HEX
                    else: s_hex = ERROR_RED_HEX
                    
                    status = Paragraph(f"<font color='{s_hex}'><b>{status_text}</b></font>", styles['CellText'])
                    advice_safe = str(check.get('advice', '')).replace('&', '&amp;').replace('<', '&lt;')
                    advice = Paragraph(advice_safe, styles['CellText'])
                    
                    table_data.append([name, value, target, status, advice])
                except:
                    continue
            
            t = Table(table_data, colWidths=[1.3*inch, 0.8*inch, 1.1*inch, 0.9*inch, 2.9*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), C_JET_BLACK),
                ('TEXTCOLOR', (0,0), (-1,0), C_WHITE),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('TOPPADDING', (0,0), (-1,0), 8),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,1), (-1,-1), 0.5, C_SILVER_GRAY),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_LIGHT_BG]),
            ]))
            
            group_elements.append(t)
            elements.append(KeepTogether(group_elements))
            elements.append(Spacer(1, 0.25*inch))
        
        # ==========================================
        # 7. DRILLS
        # ==========================================
        drills = form.get('recommended_drills', [])
        if drills:
            group_elements = []
            group_elements.append(Paragraph("Recommended Drills", styles['SectionHeader']))
            for i, drill in enumerate(drills[:3], 1):
                try:
                    if isinstance(drill, dict):
                        d_name = drill.get('name', f'Drill {i}')
                        d_desc = drill.get('description', '')
                    else:
                        d_name = f'Drill {i}'
                        d_desc = str(drill)
                    
                    safe_name = str(d_name).replace('&', '&amp;').replace('<', '&lt;')
                    safe_desc = str(d_desc).replace('&', '&amp;').replace('<', '&lt;')
                    
                    drill_html = f"<b>{i}. {safe_name}:</b> {safe_desc}"
                    group_elements.append(Paragraph(drill_html, styles['BodyText']))
                    group_elements.append(Spacer(1, 0.1*inch))
                except:
                    continue
            elements.append(KeepTogether(group_elements))
            elements.append(Spacer(1, 0.15*inch))
        
        # ==========================================
        # 8. FOOTER
        # ==========================================
        footer_line = Table([['']], colWidths=[7*inch])
        footer_line.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,0), 1, C_SILVER_GRAY),
        ]))
        elements.append(footer_line)
        elements.append(Spacer(1, 0.1*inch))
        
        footer_text = (
            "<i><font size='8' color='#64748B'>"
            "AI-calibrated analysis based on ECB & MCC coaching standards. "
            "Measurements reflect 2D camera perspective. "
            "Practice under qualified supervision for best results. "
            "© BattingEdge 2025"
            "</font></i>"
        )
        elements.append(Paragraph(footer_text, styles['BodyText']))
        
        # Build
        doc.build(elements)
        logger.info(f"✅ PDF generated: {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}", exc_info=True)
        return False