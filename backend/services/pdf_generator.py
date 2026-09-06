import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable


KNOWN_SECTIONS = [
    "SKILLS", "TECHNICAL SKILLS", "EXPERIENCE", "WORK EXPERIENCE",
    "PROFESSIONAL EXPERIENCE", "INTERNSHIP", "INTERNSHIPS", "PROJECTS",
    "ACADEMIC PROJECTS", "PERSONAL PROJECTS", "EDUCATION", "CERTIFICATIONS",
    "PUBLICATIONS", "ACHIEVEMENTS", "HONORS & AWARDS", "SUMMARY",
    "PROFESSIONAL SUMMARY", "OBJECTIVE"
]


def clean_line_text(text: str) -> str:
    """Removes non-printable/corrupted PDF glyphs and zero-width spaces."""
    text = text.replace('\u200b', '')
    text = text.replace('\ufffd', '')
    text = text.replace('\ufeff', '')
    return text.strip()


def escape_xml(text: str) -> str:
    """Escapes XML entities for ReportLab Paragraphs."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def generate_resume_pdf(resume_text: str, output_path: str | Path) -> str:
    """
    Generates a sleek, executive, ATS-friendly PDF resume from structured resume text
    using ReportLab and saves it to output_path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        'ResumeCandidateName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,  # Center
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=3
    )

    contact_style = ParagraphStyle(
        'ResumeContactInfo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        alignment=1,  # Center
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )

    section_heading_style = ParagraphStyle(
        'ResumeSectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f766e'),  # Elegant emerald/teal
        spaceBefore=8,
        spaceAfter=2,
        keepWithNext=True
    )

    item_title_style = ParagraphStyle(
        'ResumeItemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=4,
        spaceAfter=1,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ResumeBodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=2
    )

    bullet_style = ParagraphStyle(
        'ResumeBulletItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2
    )

    story = []

    # Clean input lines
    raw_lines = [clean_line_text(l) for l in resume_text.splitlines()]
    lines = [l for l in raw_lines if l]

    if not lines:
        story.append(Paragraph("Empty Resume Content", body_style))
        doc.build(story)
        return str(output_path)

    # 1. Candidate Name (first line)
    name_line = lines.pop(0)
    story.append(Paragraph(escape_xml(name_line), name_style))

    # 2. Candidate Contact details (lines directly following name that contain contact identifiers)
    contact_parts = []
    while lines and any(k in lines[0].lower() for k in ['email', 'linkedin', 'github', 'mobile', 'phone', '+', '@', 'http', '.com']):
        contact_line = lines.pop(0)
        # Split tokens separated by multiple spaces
        tokens = [clean_line_text(t) for t in re.split(r'\s{2,}', contact_line) if clean_line_text(t)]
        if tokens:
            contact_parts.extend(tokens)
        else:
            contact_parts.append(contact_line)

    if contact_parts:
        # Join with bullet separator
        escaped_parts = [escape_xml(p) for p in contact_parts]
        contact_html = " &bull; ".join(escaped_parts)
        story.append(Paragraph(contact_html, contact_style))
    else:
        story.append(Spacer(1, 4))

    # 3. Process the remaining body lines
    for line in lines:
        upper_line = line.upper().strip()

        # Check if line is a major section heading
        is_heading = (
            upper_line in KNOWN_SECTIONS or
            (len(line) < 35 and upper_line in [s.upper() for s in KNOWN_SECTIONS]) or
            (len(line) < 25 and line.isupper() and not line.startswith(("-", "•", "*", "◦")))
        )

        if is_heading:
            story.append(Spacer(1, 4))
            story.append(Paragraph(escape_xml(upper_line), section_heading_style))
            story.append(HRFlowable(
                width="100%",
                thickness=0.75,
                color=colors.HexColor('#cbd5e1'),
                spaceBefore=1,
                spaceAfter=4
            ))
            continue

        # Check if bullet point
        if line.startswith(("-", "•", "*", "◦", "▪")):
            bullet_content = line.lstrip("-•*◦▪ ").strip()
            escaped_bullet = escape_xml(bullet_content)
            story.append(Paragraph(f"&bull;&nbsp;{escaped_bullet}", bullet_style))
            continue

        # Check if sub-heading (Job Title | Company | Dates or Project Name | Stack)
        if "|" in line:
            escaped = escape_xml(line)
            story.append(Paragraph(f"<b>{escaped}</b>", item_title_style))
            continue

        # Check if category / key-value line (e.g. "Data & Languages: Python, SQL...")
        escaped = escape_xml(line)
        if ":" in line and len(line.split(":", 1)[0]) < 30 and not line.startswith("http"):
            parts = escaped.split(":", 1)
            story.append(Paragraph(f"<b>{parts[0]}:</b>{parts[1]}", body_style))
        else:
            story.append(Paragraph(escaped, body_style))

    doc.build(story)
    return str(output_path)
