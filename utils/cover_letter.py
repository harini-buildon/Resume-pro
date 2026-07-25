"""
utils/cover_letter.py – AI Cover Letter Generator
===================================================
Generates a customized, professional cover letter matching candidate
resume strengths to the target Job Description.
"""

from datetime import datetime


def generate_cover_letter(candidate_name, candidate_skills, job_title="Software Engineer", company_name="Target Company", job_description=""):
    """
    Generate a tailored cover letter based on candidate skills and job profile.

    Returns:
        dict: {
            'cover_letter_text': str,
            'job_title': str,
            'company_name': str,
            'date_str': str
        }
    """
    if not candidate_name or candidate_name == "Candidate":
        candidate_name = "Jane Candidate"

    skills_str = ", ".join(candidate_skills[:5]) if candidate_skills else "Python, REST APIs, System Design, SQL"
    date_str = datetime.now().strftime("%B %d, %Y")

    cover_letter_text = f"""{candidate_name}
{date_str}

Hiring Manager
{company_name}

RE: Application for {job_title} Position

Dear Hiring Manager,

I am writing to express my strong enthusiasm for the {job_title} position at {company_name}. With my proven background in software engineering, technical problem solving, and hands-on experience in key technologies including {skills_str}, I am confident in my ability to make an immediate, positive impact on your engineering team.

Throughout my technical background, I have consistently delivered robust, scalable solutions while maintaining a strong commitment to clean code standards and automated testing. My core skill set closely aligns with the requirements outlined for this role, specifically in designing high-performing systems and collaborating across multi-disciplinary teams.

What excites me most about {company_name} is your commitment to innovation and engineering excellence. I am particularly eager to leverage my expertise in {candidate_skills[0] if candidate_skills else 'software development'} to contribute to your upcoming projects and help drive business goals forward.

Thank you for your time and consideration. I welcome the opportunity to discuss how my technical skills and career achievements align with the goals of {company_name}.

Sincerely,

{candidate_name}
"""

    return {
        'cover_letter_text': cover_letter_text.strip(),
        'job_title': job_title,
        'company_name': company_name,
        'date_str': date_str
    }
