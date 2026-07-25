"""
utils/suggestions.py – Resume Improvement Suggestions Engine
==============================================================
This module generates intelligent, actionable suggestions to help
users improve their resumes and increase their ATS score.

HOW IT WORKS:
────────────
The engine checks each aspect of the parsed resume data and generates
specific suggestions based on what's missing or could be improved.

Suggestions are categorized by priority:
- 🔴 Critical: Issues that will significantly hurt your chances
- 🟡 Important: Improvements that would make a noticeable difference
- 🟢 Nice-to-have: Polish and fine-tuning
"""


def generate_suggestions(parsed_data, ats_result, job_match=None):
    """
    Generate a comprehensive list of resume improvement suggestions.
    
    Analyzes the parsed resume data and ATS score breakdown to produce
    targeted, actionable recommendations.
    
    Parameters:
        parsed_data (dict): Parsed resume data from resume_parser.py
        ats_result (dict): ATS score and breakdown from ats_scorer.py
        job_match (dict): Optional job matching results
    
    Returns:
        list: List of suggestion dictionaries, each containing:
            - 'category': str (e.g., 'Contact Info', 'Skills')
            - 'priority': str ('critical', 'important', 'nice-to-have')
            - 'icon': str (emoji icon)
            - 'message': str (the suggestion text)
    """
    suggestions = []
    
    # ── Contact Information Suggestions ──
    if not parsed_data.get('email'):
        suggestions.append({
            'category': 'Contact Information',
            'priority': 'critical',
            'icon': '🔴',
            'message': 'Add a professional email address. This is essential for recruiters to contact you. Use a format like firstname.lastname@gmail.com.'
        })
    
    if not parsed_data.get('phone'):
        suggestions.append({
            'category': 'Contact Information',
            'priority': 'critical',
            'icon': '🔴',
            'message': 'Add your phone number with country code. Recruiters often prefer to call candidates directly.'
        })
    
    if not parsed_data.get('linkedin'):
        suggestions.append({
            'category': 'Contact Information',
            'priority': 'important',
            'icon': '🟡',
            'message': 'Add your LinkedIn profile URL. 87% of recruiters use LinkedIn for hiring. Create a profile at linkedin.com if you don\'t have one.'
        })
    
    if not parsed_data.get('github'):
        suggestions.append({
            'category': 'Contact Information',
            'priority': 'important',
            'icon': '🟡',
            'message': 'Add your GitHub profile URL. It demonstrates your coding activity and open-source contributions to recruiters.'
        })
    
    # ── Skills Suggestions ──
    skills = parsed_data.get('skills', [])
    
    if len(skills) == 0:
        suggestions.append({
            'category': 'Skills',
            'priority': 'critical',
            'icon': '🔴',
            'message': 'No recognized technical skills found! Add a dedicated "Skills" section listing your programming languages, frameworks, tools, and technologies.'
        })
    elif len(skills) < 5:
        suggestions.append({
            'category': 'Skills',
            'priority': 'important',
            'icon': '🟡',
            'message': f'Only {len(skills)} skills detected. Aim for at least 8-10 relevant skills. Include programming languages, frameworks, databases, and tools you\'re proficient in.'
        })
    elif len(skills) < 10:
        suggestions.append({
            'category': 'Skills',
            'priority': 'nice-to-have',
            'icon': '🟢',
            'message': f'{len(skills)} skills found. Consider adding more specific tools and technologies to reach 10+ skills for better ATS matching.'
        })
    
    # ── Education Suggestions ──
    education = parsed_data.get('education', [])
    
    if not education:
        suggestions.append({
            'category': 'Education',
            'priority': 'critical',
            'icon': '🔴',
            'message': 'No education section found. Add your degree, university name, graduation year, and GPA/CGPA if it\'s above 7.0.'
        })
    elif len(education) < 2:
        suggestions.append({
            'category': 'Education',
            'priority': 'nice-to-have',
            'icon': '🟢',
            'message': 'Consider adding more education details like relevant coursework, academic achievements, or previous degrees.'
        })
    
    # ── Experience Suggestions ──
    experience = parsed_data.get('experience', [])
    
    if not experience:
        suggestions.append({
            'category': 'Experience',
            'priority': 'important',
            'icon': '🟡',
            'message': 'No work experience section found. Add internships, freelance work, or relevant part-time positions. Even a 1-month internship counts!'
        })
    else:
        # Check for measurable achievements
        exp_text = ' '.join(experience).lower()
        has_numbers = any(char.isdigit() for char in exp_text)
        
        if not has_numbers:
            suggestions.append({
                'category': 'Experience',
                'priority': 'important',
                'icon': '🟡',
                'message': 'Add measurable achievements to your experience entries. Use numbers: "Increased performance by 30%", "Managed team of 5", "Processed 10K+ records daily".'
            })
    
    # ── Projects Suggestions ──
    projects = parsed_data.get('projects', [])
    
    if not projects:
        suggestions.append({
            'category': 'Projects',
            'priority': 'critical',
            'icon': '🔴',
            'message': 'No projects section found. Add 2-3 relevant projects with descriptions, technologies used, and outcomes. This is crucial for freshers!'
        })
    elif len(projects) < 2:
        suggestions.append({
            'category': 'Projects',
            'priority': 'important',
            'icon': '🟡',
            'message': 'Add more projects to showcase your skills. Aim for at least 2-3 projects. Include personal projects, hackathon entries, or academic projects.'
        })
    
    # ── Certifications Suggestions ──
    certifications = parsed_data.get('certifications', [])
    
    if not certifications:
        suggestions.append({
            'category': 'Certifications',
            'priority': 'nice-to-have',
            'icon': '🟢',
            'message': 'Consider adding certifications from platforms like Coursera, Udemy, AWS, Google, or Microsoft. They validate your skills and stand out to recruiters.'
        })
    
    # ── Summary Suggestions ──
    if not parsed_data.get('summary'):
        suggestions.append({
            'category': 'Professional Summary',
            'priority': 'important',
            'icon': '🟡',
            'message': 'Add a professional summary (2-3 sentences) at the top of your resume. Highlight your key skills, experience level, and career goals.'
        })
    
    # ── Job-Specific Suggestions ──
    if job_match:
        missing = job_match.get('missing_skills', [])
        match_pct = job_match.get('match_percentage', 0)
        
        if missing:
            missing_str = ', '.join(missing[:5])  # Show up to 5 missing skills
            suggestions.append({
                'category': 'Job Match',
                'priority': 'critical' if match_pct < 50 else 'important',
                'icon': '🔴' if match_pct < 50 else '🟡',
                'message': f'You\'re missing these skills from the job description: {missing_str}. Learn and add these skills to improve your match.'
            })
        
        if match_pct < 30:
            suggestions.append({
                'category': 'Job Match',
                'priority': 'critical',
                'icon': '🔴',
                'message': f'Your skill match is only {match_pct}%. This role might not be the best fit, or you need significant upskilling. Consider roles that better match your current skills.'
            })
    
    # ── General Formatting Tips ──
    suggestions.append({
        'category': 'General Tips',
        'priority': 'nice-to-have',
        'icon': '💡',
        'message': 'Use a clean, single-column resume format. Avoid images, tables, and complex formatting that ATS systems may not parse correctly.'
    })
    
    suggestions.append({
        'category': 'General Tips',
        'priority': 'nice-to-have',
        'icon': '💡',
        'message': 'Keep your resume to 1-2 pages. Use action verbs (Developed, Implemented, Designed, Optimized) to describe your achievements.'
    })
    
    # Sort by priority: critical → important → nice-to-have
    priority_order = {'critical': 0, 'important': 1, 'nice-to-have': 2}
    suggestions.sort(key=lambda s: priority_order.get(s['priority'], 3))
    
    return suggestions


def get_plain_suggestions(parsed_data, ats_result, job_match=None):
    """
    Return a flat list of suggestion message strings (no priority/icon metadata).
    Used by the JSON API (/analyze) response so callers get simple strings like:
        ["Add a professional email address.", "Add 'Docker' to skills section", ...]

    Parameters:
        parsed_data (dict): Parsed resume data
        ats_result  (dict): ATS score result from ats_scorer.py
        job_match   (dict): Optional job matching results

    Returns:
        list[str]: Ordered suggestion strings (critical → important → nice-to-have)
    """
    rich_suggestions = generate_suggestions(parsed_data, ats_result, job_match)
    return [s['message'] for s in rich_suggestions]
