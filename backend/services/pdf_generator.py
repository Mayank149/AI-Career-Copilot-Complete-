from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def generate_resume_pdf(resume_text: str, output_path: str | Path) -> str:
    """
    Generates a clean, modern, ATS-friendly PDF resume from raw text
    using ReportLab and saves it to output_path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styling
    title_style = ParagraphStyle(
        'ResumeTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )

    section_header_style = ParagraphStyle(
        'ResumeSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#059669'),  # Emerald brand color
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        spaceAfter=2
    )

    story = []
    lines = [line.strip() for line in resume_text.splitlines()]

    # Filter empty lines at start
    while lines and not lines[0]:
        lines.pop(0)

    # First line often candidate name
    if lines:
        first_line = lines.pop(0)
        story.append(Paragraph(first_line, title_style))
        story.append(Spacer(1, 4))

    section_keywords = [
        "SUMMARY", "PROFESSIONAL SUMMARY", "OBJECTIVE", "SKILLS", "TECHNICAL SKILLS",
        "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT", "PROJECTS", "EDUCATION",
        "CERTIFICATIONS", "ACHIEVEMENTS", "PUBLICATIONS"
    ]

    for line in lines:
        if not line:
            story.append(Spacer(1, 4))
            continue

        upper_line = line.upper().rstrip(":")
        # Check if heading
        if upper_line in section_keywords or (len(line) < 30 and line.endswith(":") and not line.startswith(("-", "•", "*"))):
            story.append(Spacer(1, 6))
            story.append(Paragraph(line.rstrip(":").upper(), section_header_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceBefore=2, spaceAfter=4))
        elif line.startswith(("-", "•", "*")):
            bullet_text = line.lstrip("-•* ").strip()
            # Escape HTML characters for ReportLab
            bullet_text = bullet_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"&bull; {bullet_text}", bullet_style))
        else:
            escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(escaped_line, body_style))

    doc.build(story)
    return str(output_path)
