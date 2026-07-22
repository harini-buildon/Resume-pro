"""
utils/resume_parser.py – Regex-Based Resume Parsing
=====================================================
This is the CORE module of the project. It takes the raw text extracted
from a resume and parses it into structured data using regular expressions.

KEY CONCEPTS FOR BEGINNERS:
──────────────────────────
REGULAR EXPRESSIONS (Regex):
- A regex is a pattern used to search for specific text patterns.
- Example: r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
  This matches email addresses like "john@example.com"
  
- Common regex symbols:
  \\b    → Word boundary (start/end of a word)
  \\d    → Any digit (0-9)
  \\s    → Any whitespace (space, tab, newline)
  +     → One or more of the preceding character
  *     → Zero or more of the preceding character
  []    → Character class (any character inside the brackets)
  ()    → Capture group (extract the matching part)
  |     → OR (match either the left or right pattern)
  re.IGNORECASE → Makes the pattern case-insensitive

SECTION-BASED PARSING:
- Resumes are divided into sections (Education, Experience, Skills, etc.)
- We detect section headers using keywords and extract the content below them
- This approach works for most standard resume formats
"""

import re
from utils.skills_db import match_skills


def extract_email(text):
    """
    Extract email address from resume text.
    
    Regex breakdown: [A-Za-z0-9._%+-]+ @ [A-Za-z0-9.-]+ . [A-Za-z]{2,}
    - Username part: letters, digits, dots, underscores, %, +, -
    - @ symbol
    - Domain part: letters, digits, dots, hyphens
    - TLD: at least 2 letters (com, org, edu, etc.)
    
    Returns:
        str: The first email found, or empty string
    """
    email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ''


def extract_phone(text):
    """
    Extract phone number from resume text.
    
    Supports multiple formats:
    - +91 9876543210 (Indian with country code)
    - (123) 456-7890 (US format)
    - 123-456-7890
    - 1234567890 (plain 10 digits)
    
    Returns:
        str: The first phone number found, or empty string
    """
    phone_patterns = [
        r'[\+]?[\d]{1,3}[-.\s]?[\(]?[\d]{1,4}[\)]?[-.\s]?[\d]{1,4}[-.\s]?[\d]{1,9}',
        r'[\+]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,9}',
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean up and validate: should have at least 10 digits
            digits = re.sub(r'\D', '', match)  # Remove non-digit characters
            if 10 <= len(digits) <= 15:
                return match.strip()
    
    return ''


def extract_linkedin(text):
    """
    Extract LinkedIn profile URL from resume text.
    
    Matches URLs like:
    - https://linkedin.com/in/username
    - https://www.linkedin.com/in/username
    - linkedin.com/in/username
    
    Returns:
        str: LinkedIn URL or empty string
    """
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+'
    match = re.search(linkedin_pattern, text, re.IGNORECASE)
    return match.group(0) if match else ''


def extract_github(text):
    """
    Extract GitHub profile URL from resume text.
    
    Matches URLs like:
    - https://github.com/username
    - github.com/username
    
    Returns:
        str: GitHub URL or empty string
    """
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+'
    match = re.search(github_pattern, text, re.IGNORECASE)
    return match.group(0) if match else ''


def extract_name(text):
    """
    Extract the candidate's name from the resume.
    
    Heuristic approach:
    1. The name is typically the FIRST line of a resume
    2. We clean it up by removing common prefixes and extra whitespace
    3. We validate that it looks like a name (2-5 words, mostly letters)
    
    This is the trickiest part of resume parsing because names vary widely.
    For production use, you'd want a Named Entity Recognition (NER) model.
    
    Returns:
        str: Extracted name or 'Not Found'
    """
    lines = text.strip().split('\n')
    
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        
        # Skip empty lines and lines that look like contact info
        if not line:
            continue
        if '@' in line:  # Likely an email
            continue
        if re.search(r'\d{5,}', line):  # Likely a phone number
            continue
        if 'linkedin' in line.lower() or 'github' in line.lower():
            continue
        if any(keyword in line.lower() for keyword in ['resume', 'curriculum', 'cv', 'http', 'www']):
            continue
        
        # Check if the line looks like a name:
        # - Contains mostly letters and spaces
        # - Has 2-5 words
        # - Each word starts with a capital letter (common for names)
        words = line.split()
        if 1 <= len(words) <= 5:
            # Check that most characters are letters or spaces
            letter_ratio = sum(1 for c in line if c.isalpha() or c.isspace()) / max(len(line), 1)
            if letter_ratio > 0.8:
                return line
    
    return 'Not Found'


def extract_section(text, section_keywords):
    """
    Extract content from a resume section based on header keywords.
    
    How it works:
    1. Search for a line that matches one of the section keywords
    2. Collect all lines until the next section header is found
    3. Return the collected content
    
    Parameters:
        text (str): Full resume text
        section_keywords (list): Keywords that identify the section header
                                 Example: ['education', 'academic']
    
    Returns:
        str: The content of the section, or empty string if not found
    """
    lines = text.split('\n')
    
    # Common section headers used to detect where a new section begins
    all_section_headers = [
        'education', 'experience', 'work experience', 'professional experience',
        'skills', 'technical skills', 'projects', 'certifications',
        'certificates', 'achievements', 'awards', 'languages',
        'interests', 'hobbies', 'objective', 'summary', 'profile',
        'professional summary', 'publications', 'references',
        'volunteer', 'activities', 'extracurricular', 'training',
        'coursework', 'relevant coursework'
    ]
    
    section_started = False
    section_content = []
    
    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower()
        
        # Check if this line is the start of our target section
        if not section_started:
            for keyword in section_keywords:
                if keyword.lower() in stripped_lower and len(stripped) < 80:
                    section_started = True
                    break
            continue
        
        # If section has started, check if we've hit a new section
        if section_started:
            # Check if this line is a new section header
            is_new_section = False
            for header in all_section_headers:
                # A section header is typically a short line matching a known header
                if (header in stripped_lower and 
                    len(stripped) < 80 and 
                    header not in [k.lower() for k in section_keywords]):
                    is_new_section = True
                    break
            
            if is_new_section:
                break  # Stop collecting – we've hit the next section
            
            if stripped:  # Only add non-empty lines
                section_content.append(stripped)
    
    return '\n'.join(section_content)


def extract_education(text):
    """
    Extract education information from the resume.
    
    Looks for the Education section and extracts individual entries.
    Also looks for degree keywords like B.Tech, MBA, B.Sc, etc.
    
    Returns:
        list: List of education entry strings
    """
    education_keywords = ['education', 'academic', 'qualification', 'academics']
    section_text = extract_section(text, education_keywords)
    
    if section_text:
        # Split into individual entries (each entry is typically 1-3 lines)
        entries = [entry.strip() for entry in section_text.split('\n') if entry.strip()]
        return entries
    
    # Fallback: search for degree keywords anywhere in the text
    degree_patterns = [
        r'(?:B\.?Tech|B\.?E|B\.?Sc|B\.?A|B\.?Com|BCA|BBA)[\s\S]{0,100}',
        r'(?:M\.?Tech|M\.?E|M\.?Sc|M\.?A|M\.?Com|MCA|MBA)[\s\S]{0,100}',
        r'(?:Ph\.?D|Doctorate)[\s\S]{0,100}',
        r'(?:Diploma|Certificate)[\s\S]{0,100}',
        r'(?:HSC|SSC|12th|10th|XII|X)[\s\S]{0,50}',
    ]
    
    entries = []
    for pattern in degree_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entries.extend([m.strip()[:150] for m in matches])  # Limit length
    
    return entries[:5]  # Return at most 5 entries


def extract_experience(text):
    """
    Extract work experience entries from the resume.
    
    Returns:
        list: List of experience entry strings
    """
    experience_keywords = [
        'experience', 'work experience', 'professional experience',
        'employment', 'work history', 'internship'
    ]
    section_text = extract_section(text, experience_keywords)
    
    if section_text:
        entries = [entry.strip() for entry in section_text.split('\n') if entry.strip()]
        return entries
    
    return []


def extract_projects(text):
    """
    Extract project entries from the resume.
    
    Returns:
        list: List of project entry strings
    """
    project_keywords = ['projects', 'personal projects', 'academic projects', 'key projects']
    section_text = extract_section(text, project_keywords)
    
    if section_text:
        entries = [entry.strip() for entry in section_text.split('\n') if entry.strip()]
        return entries
    
    return []


def extract_certifications(text):
    """
    Extract certification entries from the resume.
    
    Returns:
        list: List of certification strings
    """
    cert_keywords = ['certifications', 'certificates', 'certification', 'credentials']
    section_text = extract_section(text, cert_keywords)
    
    if section_text:
        entries = [entry.strip() for entry in section_text.split('\n') if entry.strip()]
        return entries
    
    # Fallback: look for common certification keywords
    cert_patterns = [
        r'(?:certified|certification|certificate)[\s\S]{0,100}',
        r'(?:AWS|Azure|Google Cloud|Coursera|Udemy|edX)[\s\S]{0,80}',
    ]
    
    entries = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entries.extend([m.strip()[:150] for m in matches])
    
    return entries[:10]


def extract_languages(text):
    """
    Extract spoken/known languages from the resume.
    
    Returns:
        list: List of language strings
    """
    # First try to find a Languages section
    lang_keywords = ['languages', 'language proficiency']
    section_text = extract_section(text, lang_keywords)
    
    if section_text:
        entries = [entry.strip() for entry in section_text.split('\n') if entry.strip()]
        return entries
    
    # Fallback: look for common language names
    common_languages = [
        'English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Malayalam',
        'Marathi', 'Bengali', 'Gujarati', 'Punjabi', 'Urdu',
        'French', 'German', 'Spanish', 'Japanese', 'Chinese',
        'Korean', 'Arabic', 'Portuguese', 'Russian', 'Italian'
    ]
    
    found = []
    text_lower = text.lower()
    for lang in common_languages:
        if lang.lower() in text_lower:
            found.append(lang)
    
    return found


def extract_summary(text):
    """
    Extract the professional summary/objective from the resume.
    
    Returns:
        str: Summary text or empty string
    """
    summary_keywords = ['summary', 'objective', 'profile', 'about me', 'professional summary']
    section_text = extract_section(text, summary_keywords)
    return section_text[:500] if section_text else ''  # Limit to 500 chars


def parse_resume(text):
    """
    MASTER FUNCTION – Parse all information from resume text.
    
    This is the main function called from app.py. It orchestrates
    all the individual extraction functions and returns a complete
    structured dictionary of resume data.
    
    Parameters:
        text (str): The full extracted text from the resume
    
    Returns:
        dict: Structured resume data with all fields populated
    """
    parsed = {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'linkedin': extract_linkedin(text),
        'github': extract_github(text),
        'education': extract_education(text),
        'skills': match_skills(text),          # Uses skills_db.py
        'experience': extract_experience(text),
        'projects': extract_projects(text),
        'certifications': extract_certifications(text),
        'languages': extract_languages(text),
        'summary': extract_summary(text),
    }
    
    return parsed
