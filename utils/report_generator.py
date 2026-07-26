"""
utils/report_generator.py – Professional PDF Report Generation
================================================================
This module generates a downloadable PDF report summarizing the
complete resume analysis using the FPDF2 library.

KEY CONCEPTS FOR BEGINNERS:
──────────────────────────
FPDF (Free PDF):
- A lightweight library to create PDFs from scratch in Python
- You "draw" content on the page using coordinates and fonts
- The page is measured in millimeters by default
- Origin (0,0) is at the top-left corner

The report includes:
1. Header with title and date
2. Candidate information summary
3. ATS score with breakdown
4. Skills analysis (matched and missing)
5. Resume improvement suggestions
6. Job role recommendations
7. Course recommendations
"""

import os
from datetime import datetime
from fpdf import FPDF
from config import REPORT_FOLDER


class ResumeReport(FPDF):
    """
    Custom PDF class extending FPDF with our header and footer.
    
    By overriding header() and footer(), these methods are automatically
    called on every page of the PDF.
    """
    
    def header(self):
        """Add a header to every page."""
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 58, 138)  # Dark blue
        self.set_x(self.l_margin)
        self.cell(0, 10, 'Resume Pro - Analysis Report', align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Draw a blue line under the header
        self.set_draw_color(59, 130, 246)  # Blue line
        self.set_line_width(0.5)
        self.line(self.l_margin, 18, self.w - self.r_margin, 18)
        self.ln(5)
    
    def footer(self):
        """Add a footer with page number to every page."""
        self.set_y(-15)  # Position 15mm from bottom
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)  # Gray
        self.set_x(self.l_margin)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
    
    def section_title(self, title):
        """Add a styled section title."""
        self.ln(3)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 58, 138)  # Dark blue
        self.set_x(self.l_margin)
        self.cell(0, 8, sanitize_text(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(219, 234, 254)  # Light blue line
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)
    
    def body_text(self, text):
        """Add regular body text."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(55, 65, 81)  # Dark gray
        safe_text = sanitize_text(text)
        self.set_x(self.l_margin)
        avail_w = max(10, self.w - self.r_margin - self.l_margin)
        self.multi_cell(avail_w, 5, safe_text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    
    def key_value(self, key, value):
        """Add a key-value pair (like 'Email: john@example.com')."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(55, 65, 81)
        safe_key = sanitize_text(key)
        safe_val = sanitize_text(str(value))
        self.set_x(self.l_margin)
        self.cell(40, 6, f'{safe_key}:', new_x="END")
        self.set_font('Helvetica', '', 10)
        avail_w = max(10, self.w - self.r_margin - self.get_x())
        self.multi_cell(avail_w, 6, safe_val, new_x="LMARGIN", new_y="NEXT")
    
    def bullet_point(self, text):
        """Add a bullet point item."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(55, 65, 81)
        safe_text = sanitize_text(text)
        self.set_x(self.l_margin)
        self.cell(5, 5, '', new_x="END")  # Indent
        self.cell(5, 5, '-', new_x="END")  # Bullet character (safe ASCII)
        avail_w = max(10, self.w - self.r_margin - self.get_x())
        self.multi_cell(avail_w, 5, f' {safe_text}', new_x="LMARGIN", new_y="NEXT")

    def badge(self, text, color='blue'):
        """Add an inline badge/tag."""
        colors = {
            'blue': (219, 234, 254),
            'green': (209, 250, 229),
            'red': (254, 226, 226),
            'yellow': (254, 249, 195),
        }
        text_colors = {
            'blue': (30, 58, 138),
            'green': (6, 95, 70),
            'red': (153, 27, 27),
            'yellow': (133, 100, 4),
        }
        
        bg = colors.get(color, colors['blue'])
        tc = text_colors.get(color, text_colors['blue'])
        
        safe_text = sanitize_text(text)
        text_width = self.get_string_width(safe_text) + 6
        
        self.set_fill_color(*bg)
        self.set_text_color(*tc)
        self.set_font('Helvetica', '', 9)
        self.cell(text_width, 6, f' {safe_text} ', fill=True, new_x="END")
        self.cell(2, 6, '', new_x="END")  # Spacing


def sanitize_text(text):
    """
    Replace Unicode characters that FPDF can't render with ASCII equivalents.
    FPDF's built-in fonts (Helvetica, etc.) only support latin-1 characters.
    """
    if not text:
        return ''
    replacements = {
        '\u2713': '[OK]',    # ✓
        '\u2714': '[OK]',    # ✔
        '\u2715': '[X]',     # ✕
        '\u2716': '[X]',     # ✖
        '\u2717': '[X]',     # ✗
        '\u2718': '[X]',     # ✘
        '\u2022': '-',       # •
        '\u2023': '>',       # ‣
        '\u25cf': '-',       # ●
        '\u25cb': 'o',       # ○
        '\u2605': '*',       # ★
        '\u2606': '*',       # ☆
        '\u2192': '->',      # →
        '\u2190': '<-',      # ←
        '\u2191': '^',       # ↑
        '\u2193': 'v',       # ↓
        '\u201c': '"',       # "
        '\u201d': '"',       # "
        '\u2018': "'",       # '
        '\u2019': "'",       # '
        '\u2014': '--',      # —
        '\u2013': '-',       # –
        '\u2026': '...',     # …
        '\u00a0': ' ',       # non-breaking space
        '\u2764': '<3',      # ❤
        '\u2611': '[x]',     # ☑
        '\u2610': '[ ]',     # ☐
        '\u2612': '[x]',     # ☒
        '\u00e9': 'e',       # é
        '\u2019': "'",       # right single quote
        '\u00b7': '-',       # ·
        '\u00d7': 'x',       # ×
        '\u00f7': '/',       # ÷
        '\u2265': '>=',      # ≥
        '\u2264': '<=',      # ≤
        '\u2260': '!=',      # ≠
        '\u221e': 'inf',     # ∞
        '\u2211': 'sum',     # ∑
        '\u00b1': '+/-',     # ±
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove remaining emoji/unicode block characters as a fallback
    cleaned = ''
    for ch in text:
        try:
            ch.encode('latin-1')
            cleaned += ch
        except (UnicodeEncodeError, UnicodeDecodeError):
            cleaned += '?'

    # Break long unspaced words (>35 chars) so FPDF multi_cell never encounters horizontal space overflow
    words = cleaned.split(' ')
    processed = []
    for w in words:
        if len(w) > 35:
            w = ' '.join([w[i:i+35] for i in range(0, len(w), 35)])
        processed.append(w)
    return ' '.join(processed)


def generate_report(parsed_data, ats_result, suggestions, job_recommendations,
                    course_recommendations, job_match=None):
    """
    Generate a complete PDF report of the resume analysis.
    
    Parameters:
        parsed_data (dict): Parsed resume data
        ats_result (dict): ATS score and breakdown
        suggestions (list): Improvement suggestions
        job_recommendations (list): Recommended job roles
        course_recommendations (list): Recommended courses
        job_match (dict): Optional job matching results
    
    Returns:
        str: Path to the generated PDF file
    """
    # Ensure the reports directory exists
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    
    # Create the PDF
    pdf = ResumeReport()
    pdf.alias_nb_pages()  # Enable total page count in footer
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # ── Report Date ──
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}',
             align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # ── Section 1: Candidate Information ──
    pdf.section_title('1. Candidate Information')
    pdf.key_value('Name', parsed_data.get('name', 'Not Found'))
    pdf.key_value('Email', parsed_data.get('email', 'Not Found'))
    pdf.key_value('Phone', parsed_data.get('phone', 'Not Found'))
    pdf.key_value('LinkedIn', parsed_data.get('linkedin', 'Not Found'))
    pdf.key_value('GitHub', parsed_data.get('github', 'Not Found'))
    pdf.ln(3)
    
    # ── Section 2: ATS Score ──
    pdf.section_title('2. ATS Compatibility Score')
    
    total_score = ats_result.get('total_score', 0)
    pdf.set_font('Helvetica', 'B', 24)
    
    # Color based on score
    if total_score >= 70:
        pdf.set_text_color(6, 95, 70)    # Green
    elif total_score >= 50:
        pdf.set_text_color(133, 100, 4)  # Yellow
    else:
        pdf.set_text_color(153, 27, 27)  # Red
    
    pdf.cell(0, 12, f'{total_score}/100', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Score breakdown
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(55, 65, 81)
    pdf.cell(0, 6, 'Score Breakdown:', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    breakdown = ats_result.get('breakdown', {})
    for key, data in breakdown.items():
        if isinstance(data, dict):
            label = data.get('label', key)
            score = data.get('score', 0)
            max_score = data.get('max', 0)
            pdf.bullet_point(f'{label}: {score}/{max_score}')
    
    pdf.ln(3)
    
    # ── Section 3: Skills Analysis ──
    pdf.section_title('3. Skills Analysis')
    
    skills = parsed_data.get('skills', [])
    pdf.body_text(f'Total skills identified: {len(skills)}')
    
    if skills:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(55, 65, 81)
        pdf.cell(0, 6, 'Your Skills:', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        
        # Display skills as comma-separated list
        skills_text = ', '.join(skills)
        pdf.body_text(skills_text)
    
    # Job match skills (if provided)
    if job_match:
        matched = job_match.get('matched_skills', [])
        missing = job_match.get('missing_skills', [])
        match_pct = job_match.get('match_percentage', 0)
        
        pdf.ln(2)
        pdf.body_text(f'Job Match Percentage: {match_pct}%')
        
        if matched:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(6, 95, 70)
            pdf.cell(0, 6, 'Matched Skills:', new_x="LMARGIN", new_y="NEXT")
            pdf.body_text(', '.join(matched))
        
        if missing:
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(153, 27, 27)
            pdf.cell(0, 6, 'Missing Skills:', new_x="LMARGIN", new_y="NEXT")
            pdf.body_text(', '.join(missing))
    
    pdf.ln(3)
    
    # ── Section 4: Improvement Suggestions ──
    pdf.section_title('4. Resume Improvement Suggestions')
    
    for suggestion in suggestions:
        priority = suggestion.get('priority', 'nice-to-have')
        # Replace emoji icon with text label for PDF
        priority_labels = {
            'critical': '[CRITICAL]',
            'important': '[IMPORTANT]',
            'nice-to-have': '[TIP]'
        }
        label = priority_labels.get(priority, '[TIP]')
        message = suggestion.get('message', '')
        category = suggestion.get('category', '')
        pdf.bullet_point(f'{label} [{category}] {message}')
    
    pdf.ln(3)
    
    # ── Section 5: Job Recommendations ──
    pdf.section_title('5. Recommended Job Roles')
    
    if job_recommendations:
        for rec in job_recommendations:
            role = rec.get('role', '')
            fit = rec.get('fit_percentage', 0)
            desc = rec.get('description', '')
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(30, 58, 138)
            pdf.cell(0, 6, f'{role} (Fit: {fit}%)', new_x="LMARGIN", new_y="NEXT")
            pdf.body_text(desc)
    else:
        pdf.body_text('No strong job role matches found. Consider adding more skills to your resume.')
    
    pdf.ln(3)
    
    # ── Section 6: Course Recommendations ──
    pdf.section_title('6. Recommended Learning Topics')
    
    if course_recommendations:
        for course in course_recommendations[:8]:  # Limit to 8 courses
            skill = course.get('skill', '')
            topic = course.get('topic', '')
            desc = course.get('description', '')
            platforms = course.get('platforms', '')
            
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(55, 65, 81)
            pdf.cell(0, 6, f'{topic} ({skill})', new_x="LMARGIN", new_y="NEXT")
            pdf.body_text(desc)
            pdf.body_text(f'Where to learn: {platforms}')
            pdf.ln(1)
    else:
        pdf.body_text('Great job! No critical skills gaps identified.')
    
    # ── Save the PDF ──
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'resume_analysis_{timestamp}.pdf'
    filepath = os.path.join(REPORT_FOLDER, filename)
    
    pdf.output(filepath)
    
    return filepath, filename
