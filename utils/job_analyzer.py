"""
utils/job_analyzer.py – Job Description Analysis & Comparison
==============================================================
This module compares a resume against a job description using:
1. Simple skill matching (set intersection)
2. TF-IDF Vectorization + Cosine Similarity (ML-based comparison)

KEY CONCEPTS FOR BEGINNERS:
──────────────────────────

TF-IDF (Term Frequency – Inverse Document Frequency):
- TF (Term Frequency): How often a word appears in a document.
  If "Python" appears 5 times in a 100-word resume, TF = 5/100 = 0.05
  
- IDF (Inverse Document Frequency): How rare a word is across documents.
  Common words like "the" get low IDF; rare words like "TensorFlow" get high IDF.
  
- TF-IDF = TF × IDF → Words that are frequent in this document but rare
  overall get the highest scores. This helps identify important keywords.

COSINE SIMILARITY:
- Measures how similar two documents are, on a scale of 0 to 1.
- 0 = completely different, 1 = identical
- It compares the angle between two TF-IDF vectors.
- Think of it as: "How much do these two texts talk about the same topics?"

WHY USE BOTH METHODS?
- Skill matching gives exact, interpretable results (which skills match/miss)
- TF-IDF similarity gives an overall "semantic" similarity score
- Together, they provide a comprehensive comparison
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skills_db import match_skills


def extract_job_skills(job_text):
    """
    Extract recognized skills from a job description.
    
    Uses the same skills database as the resume parser to ensure
    consistent skill names across the comparison.
    
    Parameters:
        job_text (str): The job description text
    
    Returns:
        list: List of skill names found in the job description
    """
    return match_skills(job_text)


def compare_skills(resume_skills, job_skills):
    """
    Compare resume skills with job description skills.
    
    Uses Python set operations:
    - Intersection (&): Skills in BOTH the resume and job description
    - Difference (-): Skills in the job but NOT in the resume
    
    Parameters:
        resume_skills (list): Skills extracted from the resume
        job_skills (list): Skills extracted from the job description
    
    Returns:
        dict: {
            'matched': list of matched skills,
            'missing': list of missing skills,
            'match_percentage': float (0-100)
        }
    """
    # Convert to sets for efficient comparison
    resume_set = set(skill.lower() for skill in resume_skills)
    job_set = set(skill.lower() for skill in job_skills)
    
    # Find matched and missing skills
    matched_lower = resume_set & job_set  # Intersection
    missing_lower = job_set - resume_set   # Difference
    
    # Map back to original casing from job_skills
    matched = [s for s in job_skills if s.lower() in matched_lower]
    missing = [s for s in job_skills if s.lower() in missing_lower]
    
    # Calculate match percentage
    if len(job_skills) > 0:
        match_pct = (len(matched) / len(job_skills)) * 100
    else:
        match_pct = 0.0
    
    return {
        'matched': matched,
        'missing': missing,
        'match_percentage': round(match_pct, 1)
    }


def calculate_tfidf_similarity(resume_text, job_text):
    """
    Calculate the similarity between resume and job description
    using TF-IDF Vectorization and Cosine Similarity.
    
    Step-by-step process:
    1. Create a TF-IDF Vectorizer that converts text into numerical vectors
    2. Fit and transform both texts into TF-IDF vectors
    3. Calculate the cosine similarity between the two vectors
    4. Return a percentage score
    
    Parameters:
        resume_text (str): Full text of the resume
        job_text (str): Full text of the job description
    
    Returns:
        float: Similarity score as a percentage (0-100)
    """
    if not resume_text or not job_text:
        return 0.0
    
    try:
        # Step 1: Create the TF-IDF Vectorizer
        # stop_words='english' removes common words like "the", "is", "at"
        # that don't carry meaningful information
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Step 2: Transform both texts into TF-IDF vectors
        # fit_transform() learns the vocabulary AND transforms in one step
        # We pass both texts as a list so they share the same vocabulary
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        
        # Step 3: Calculate cosine similarity
        # tfidf_matrix[0] = resume vector, tfidf_matrix[1] = job description vector
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        # Step 4: Convert to percentage (similarity is a 2D array)
        score = round(float(similarity[0][0]) * 100, 1)
        
        return score
    
    except Exception as e:
        print(f"TF-IDF calculation error: {e}")
        return 0.0


def analyze_job_match(resume_text, resume_skills, job_text):
    """
    Complete job match analysis – combines skill matching and TF-IDF similarity.
    
    This is the main function called from app.py when a user provides
    a job description for comparison.
    
    Parameters:
        resume_text (str): Full resume text
        resume_skills (list): Skills extracted from the resume
        job_text (str): Job description text
    
    Returns:
        dict: Complete analysis results including:
            - job_skills: Skills found in the job description
            - matched_skills: Skills in both resume and JD
            - missing_skills: Skills in JD but not resume
            - match_percentage: Skill match percentage
            - similarity_score: TF-IDF cosine similarity score
    """
    # Extract skills from job description
    job_skills = extract_job_skills(job_text)
    
    # Compare skills
    skill_comparison = compare_skills(resume_skills, job_skills)
    
    # Calculate TF-IDF similarity
    similarity_score = calculate_tfidf_similarity(resume_text, job_text)
    
    return {
        'job_skills': job_skills,
        'matched_skills': skill_comparison['matched'],
        'missing_skills': skill_comparison['missing'],
        'match_percentage': skill_comparison['match_percentage'],
        'similarity_score': similarity_score,
    }
