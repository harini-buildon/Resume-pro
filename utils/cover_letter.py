"""
utils/cover_letter.py – AI Cover Letter Generator
===================================================
Generates a customized, professional cover letter matching candidate
resume strengths to the target Job Description.
"""

from datetime import datetime
from utils.llm_client import generate_text


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

    skills_str = ", ".join(candidate_skills[:5]) if candidate_skills else "Software Development"
    date_str = datetime.now().strftime("%B %d, %Y")

    # Construct the prompt for Gemini
    prompt = f"""
    Write a professional and highly personalized cover letter for the following candidate.
    Candidate Name: {candidate_name}
    Candidate Key Skills: {skills_str}
    Target Job Title: {job_title}
    Target Company: {company_name}
    Job Description context: {job_description if job_description else 'Standard software engineering role'}

    Do NOT include placeholder blocks like [Company Address] or [Phone Number]. 
    Just output the body of the cover letter, starting with the candidate's name and date at the top.
    Keep it concise, compelling, and under 300 words.
    """

    system_instruction = "You are an expert career coach writing professional cover letters."
    
    # Try Gemini API
    ai_generated_text = generate_text(prompt, system_instruction)

    if ai_generated_text:
        cover_letter_text = ai_generated_text.strip()
    else:
        # Fallback to static template if API fails or key is missing
        cover_letter_text = f"""{candidate_name}
{date_str}

Hiring Manager
{company_name}

RE: Application for {job_title} Position

Dear Hiring Manager,

I am writing to express my strong enthusiasm for the {job_title} position at {company_name}. With my proven background in software engineering, technical problem solving, and hands-on experience in key technologies including {skills_str}, I am confident in my ability to make an immediate, positive impact on your engineering team.

Throughout my technical background, I have consistently delivered robust, scalable solutions while maintaining a strong commitment to clean code standards and automated testing. My core skill set closely aligns with the requirements outlined for this role, specifically in designing high-performing systems and collaborating across multi-disciplinary teams.

What excites me most about {company_name} is your commitment to innovation and engineering excellence. I am particularly eager to leverage my expertise to contribute to your upcoming projects and help drive business goals forward.

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
