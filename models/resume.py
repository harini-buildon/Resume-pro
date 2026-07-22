"""
models/resume.py – Data Models / Schema Definitions
=====================================================
This module defines the data structures used throughout the application.

WHY USE MODELS?
──────────────
Instead of passing around raw dictionaries with arbitrary keys,
we define clear schemas so every part of the code knows exactly
what fields to expect. This prevents bugs like typos in dict keys.

We use simple functions that return template dictionaries.
(For a more advanced project, you could use Python dataclasses or Pydantic.)
"""


def create_resume_data():
    """
    Returns a template dictionary for parsed resume information.
    
    This is the structure that resume_parser.py fills in after
    extracting information from the resume text.
    """
    return {
        'name': '',
        'email': '',
        'phone': '',
        'linkedin': '',
        'github': '',
        'education': [],       # List of education entries
        'skills': [],          # List of matched skill strings
        'experience': [],      # List of experience entries
        'projects': [],        # List of project entries
        'certifications': [],  # List of certification entries
        'languages': [],       # List of spoken/programming languages
        'summary': '',         # Professional summary text
    }


def create_analysis_result():
    """
    Returns a template dictionary for a complete analysis result.
    
    This is what gets displayed on the dashboard and stored in the database.
    """
    return {
        'ats_score': 0,
        'score_breakdown': {
            'contact_info': 0,      # Out of 15
            'skills': 0,            # Out of 20
            'education': 0,         # Out of 15
            'experience': 0,        # Out of 15
            'projects': 0,          # Out of 10
            'certifications': 0,    # Out of 5
            'formatting': 0,        # Out of 10
            'keyword_match': 0,     # Out of 10
        },
        'matched_skills': [],
        'missing_skills': [],
        'match_percentage': 0.0,
        'suggestions': [],
        'job_recommendations': [],
        'course_recommendations': [],
    }


def create_job_match():
    """
    Returns a template dictionary for job description comparison results.
    """
    return {
        'job_description': '',
        'job_skills': [],
        'matched_skills': [],
        'missing_skills': [],
        'match_percentage': 0.0,
        'similarity_score': 0.0,  # TF-IDF cosine similarity
    }
