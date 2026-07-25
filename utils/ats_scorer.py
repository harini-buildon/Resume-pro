"""
utils/ats_scorer.py – ATS (Applicant Tracking System) Score Calculator
========================================================================
This module calculates a resume's ATS compatibility score out of 100.

WHAT IS AN ATS?
──────────────
ATS (Applicant Tracking System) is software used by recruiters to
automatically screen resumes. It scans for keywords, proper formatting,
and relevant sections. A higher ATS score means the resume is more
likely to pass the automated screening and reach a human recruiter.

SCORING BREAKDOWN (Total: 100 points):
──────────────────────────────────────
1. Contact Information  : 15 points
2. Skills               : 20 points
3. Education            : 15 points
4. Experience           : 15 points
5. Projects             : 10 points
6. Certifications       :  5 points
7. Formatting           : 10 points
8. Keyword Match        : 10 points
"""


def score_contact_info(parsed_data):
    """
    Score the contact information section (max 15 points).
    
    Breakdown:
    - Email present:    4 points (essential for recruiters to contact you)
    - Phone present:    4 points (second most important contact method)
    - LinkedIn present: 4 points (professional online presence)
    - GitHub present:   3 points (shows you code publicly)
    
    Parameters:
        parsed_data (dict): The parsed resume data dictionary
    
    Returns:
        tuple: (score, details_dict)
    """
    score = 0
    details = {}
    
    if parsed_data.get('email'):
        score += 4
        details['email'] = '✅ Email found'
    else:
        details['email'] = '❌ Email not found'
    
    if parsed_data.get('phone'):
        score += 4
        details['phone'] = '✅ Phone found'
    else:
        details['phone'] = '❌ Phone not found'
    
    if parsed_data.get('linkedin'):
        score += 4
        details['linkedin'] = '✅ LinkedIn found'
    else:
        details['linkedin'] = '❌ LinkedIn not found'
    
    if parsed_data.get('github'):
        score += 3
        details['github'] = '✅ GitHub found'
    else:
        details['github'] = '❌ GitHub not found'
    
    return score, details


def score_skills(parsed_data):
    """
    Score the skills section (max 20 points).
    
    Scoring logic:
    - 0 skills:  0 points
    - 1-3 skills: 5 points
    - 4-6 skills: 10 points
    - 7-10 skills: 15 points
    - 11+ skills: 20 points (full marks)
    
    More recognized skills = better ATS score, because ATS systems
    scan for specific keywords that match job requirements.
    """
    skills = parsed_data.get('skills', [])
    count = len(skills)
    
    if count >= 11:
        score = 20
    elif count >= 7:
        score = 15
    elif count >= 4:
        score = 10
    elif count >= 1:
        score = 5
    else:
        score = 0
    
    details = f"{count} skills identified"
    return score, details


def score_education(parsed_data):
    """
    Score the education section (max 15 points).
    
    Scoring:
    - Education section present: 8 points
    - Multiple entries (school + college): 4 points
    - Degree keywords found: 3 points
    """
    education = parsed_data.get('education', [])
    score = 0
    
    if education:
        score += 8  # Education section exists
        
        if len(education) >= 2:
            score += 4  # Multiple education entries
        
        # Check for degree keywords
        edu_text = ' '.join(education).lower()
        degree_keywords = ['b.tech', 'btech', 'b.e', 'b.sc', 'bsc', 'm.tech', 'mtech',
                          'm.sc', 'msc', 'mba', 'phd', 'bachelor', 'master', 'diploma',
                          'bca', 'mca', 'b.com', 'bcom']
        
        if any(kw in edu_text for kw in degree_keywords):
            score += 3
    
    details = f"{len(education)} education entries found"
    return score, details


def score_experience(parsed_data):
    """
    Score the experience section (max 15 points).
    
    Scoring:
    - Experience section present: 8 points
    - Multiple entries: 4 points
    - Detailed entries (long text): 3 points
    """
    experience = parsed_data.get('experience', [])
    score = 0
    
    if experience:
        score += 8
        
        if len(experience) >= 3:
            score += 4
        elif len(experience) >= 2:
            score += 2
        
        # Check for detailed descriptions
        total_text = ' '.join(experience)
        if len(total_text) > 200:
            score += 3
    
    details = f"{len(experience)} experience entries found"
    return score, details


def score_projects(parsed_data):
    """
    Score the projects section (max 10 points).
    
    Scoring:
    - Projects section present: 5 points
    - 2+ projects: 3 points
    - 3+ projects: 5 points (replaces the 3 above)
    """
    projects = parsed_data.get('projects', [])
    score = 0
    
    if projects:
        score += 5
        
        if len(projects) >= 3:
            score += 5
        elif len(projects) >= 2:
            score += 3
    
    details = f"{len(projects)} projects found"
    return score, details


def score_certifications(parsed_data):
    """
    Score certifications (max 5 points).
    
    Scoring:
    - Any certification present: 3 points
    - 2+ certifications: 5 points
    """
    certs = parsed_data.get('certifications', [])
    score = 0
    
    if certs:
        score += 3
        if len(certs) >= 2:
            score += 2
    
    details = f"{len(certs)} certifications found"
    return score, details


def score_formatting(raw_text, parsed_data):
    """
    Score resume formatting quality (max 10 points).
    
    Checks:
    - Reasonable length (300-5000 words): 4 points
    - Has section headers: 3 points
    - Has a summary/objective: 3 points
    
    ATS systems prefer well-formatted resumes with clear sections.
    """
    score = 0
    details = {}
    
    # Check resume length (word count)
    word_count = len(raw_text.split())
    
    if 300 <= word_count <= 5000:
        score += 4
        details['length'] = f'✅ Good length ({word_count} words)'
    elif word_count < 300:
        score += 1
        details['length'] = f'⚠️ Too short ({word_count} words) – aim for 300+ words'
    else:
        score += 2
        details['length'] = f'⚠️ Very long ({word_count} words) – consider condensing'
    
    # Check for section headers
    section_keywords = ['education', 'experience', 'skills', 'projects']
    headers_found = sum(1 for kw in section_keywords if kw in raw_text.lower())
    
    if headers_found >= 3:
        score += 3
        details['sections'] = f'✅ {headers_found}/4 key sections found'
    elif headers_found >= 2:
        score += 2
        details['sections'] = f'⚠️ Only {headers_found}/4 key sections found'
    else:
        score += 1
        details['sections'] = f'❌ Only {headers_found}/4 key sections found'
    
    # Check for summary/objective
    if parsed_data.get('summary'):
        score += 3
        details['summary'] = '✅ Professional summary present'
    else:
        details['summary'] = '❌ No professional summary found'
    
    return score, details


def score_keyword_match(parsed_data, job_match=None):
    """
    Score keyword matching (max 10 points).
    
    If a job description was provided:
    - Uses the match percentage from the job analysis
    
    If no job description:
    - Scores based on the number of industry-relevant skills found
    
    Parameters:
        parsed_data (dict): Parsed resume data
        job_match (dict): Optional job matching results
    """
    score = 0
    
    if job_match and job_match.get('match_percentage', 0) > 0:
        # Score based on job match percentage
        match_pct = job_match['match_percentage']
        if match_pct >= 80:
            score = 10
        elif match_pct >= 60:
            score = 8
        elif match_pct >= 40:
            score = 6
        elif match_pct >= 20:
            score = 4
        else:
            score = 2
        details = f"Job match: {match_pct}%"
    else:
        # No job description – score based on skill variety
        skills_count = len(parsed_data.get('skills', []))
        if skills_count >= 10:
            score = 10
        elif skills_count >= 7:
            score = 8
        elif skills_count >= 4:
            score = 5
        elif skills_count >= 1:
            score = 3
        else:
            score = 0
        details = f"Based on {skills_count} skills (no job description provided)"
    
    return score, details


def calculate_ats_score(parsed_data, raw_text, job_match=None):
    """
    Calculate ATS compatibility score.
    If job_match is provided, computes:
      Final Score = round((weighted_keyword_match_% * 0.7) + (similarity_score * 0.3))
    Otherwise falls back to general section-based scoring.
    """
    contact_score, contact_details = score_contact_info(parsed_data)
    skills_score, skills_details = score_skills(parsed_data)
    education_score, education_details = score_education(parsed_data)
    experience_score, experience_details = score_experience(parsed_data)
    projects_score, projects_details = score_projects(parsed_data)
    certs_score, certs_details = score_certifications(parsed_data)
    format_score, format_details = score_formatting(raw_text, parsed_data)
    keyword_score, keyword_details = score_keyword_match(parsed_data, job_match)
    
    section_total = (contact_score + skills_score + education_score + 
                     experience_score + projects_score + certs_score + 
                     format_score + keyword_score)

    if job_match:
        kw_match_pct = float(job_match.get('match_percentage', 0.0))
        sim_score = float(job_match.get('similarity_score', 0.0))
        
        raw_final = (kw_match_pct * 0.7) + (sim_score * 0.3)
        final_ats_score = int(round(raw_final))
        
        formula_str = f"({kw_match_pct:.1f}% * 0.7) + ({sim_score:.1f}% * 0.3) = {final_ats_score}"
        
        breakdown = {
            'weighted_keyword_match_percent': kw_match_pct,
            'similarity_score': sim_score,
            'keyword_weight': 0.7,
            'similarity_weight': 0.3,
            'formula': formula_str,
            'contact_info': {'score': contact_score, 'max': 15, 'label': 'Contact Information', 'details': contact_details},
            'skills': {'score': skills_score, 'max': 20, 'label': 'Technical Skills', 'details': skills_details},
            'education': {'score': education_score, 'max': 15, 'label': 'Education', 'details': education_details},
            'experience': {'score': experience_score, 'max': 15, 'label': 'Work Experience', 'details': experience_details},
            'projects': {'score': projects_score, 'max': 10, 'label': 'Projects', 'details': projects_details},
            'certifications': {'score': certs_score, 'max': 5, 'label': 'Certifications', 'details': certs_details},
            'formatting': {'score': format_score, 'max': 10, 'label': 'Resume Formatting', 'details': format_details},
            'keyword_match': {'score': keyword_score, 'max': 10, 'label': 'Keyword Match', 'details': keyword_details}
        }
        
        return {
            'total_score': final_ats_score,
            'breakdown': breakdown
        }
    else:
        return {
            'total_score': section_total,
            'breakdown': {
                'contact_info': {'score': contact_score, 'max': 15, 'label': 'Contact Information', 'details': contact_details},
                'skills': {'score': skills_score, 'max': 20, 'label': 'Technical Skills', 'details': skills_details},
                'education': {'score': education_score, 'max': 15, 'label': 'Education', 'details': education_details},
                'experience': {'score': experience_score, 'max': 15, 'label': 'Work Experience', 'details': experience_details},
                'projects': {'score': projects_score, 'max': 10, 'label': 'Projects', 'details': projects_details},
                'certifications': {'score': certs_score, 'max': 5, 'label': 'Certifications', 'details': certs_details},
                'formatting': {'score': format_score, 'max': 10, 'label': 'Resume Formatting', 'details': format_details},
                'keyword_match': {'score': keyword_score, 'max': 10, 'label': 'Keyword Match', 'details': keyword_details}
            }
        }

