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
from utils.nlp_processor import extract_keywords_nlp, calculate_weighted_match


def extract_job_skills(job_text):
    """Extract keywords and recognized skills from a job description using spaCy NLP."""
    return extract_keywords_nlp(job_text)


def compare_skills(resume_skills, job_skills):
    """Compare resume skills with job description skills using weighted matching."""
    return calculate_weighted_match(resume_skills, job_skills)


def calculate_tfidf_similarity(resume_text, job_text):
    """
    Calculate the similarity between resume and job description
    using TF-IDF Vectorization + Cosine Similarity.

    Uses unigrams AND bigrams (ngram_range=(1, 2)) so that multi-word
    skills like "Machine Learning", "System Design", "CI/CD" are scored
    as coherent phrases rather than disconnected single tokens.

    sublinear_tf=True applies log-normalization to term frequency,
    dampening the effect of very frequent words and giving rarer
    technical terms a fairer weight.
    """
    if not resume_text or not job_text:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),   # unigrams + bigrams
            min_df=1,
            sublinear_tf=True,    # log(1 + tf) – dampens high-frequency terms
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = round(float(similarity[0][0]) * 100, 1)
        return score
    except Exception as e:
        print(f"TF-IDF calculation error: {e}")
        return 0.0


def analyze_job_match(resume_text, resume_skills, job_text):
    """
    Complete hybrid job match analysis – combines spaCy NLP weighted keyword matching 
    and TF-IDF Cosine Similarity.
    
    Returns:
        dict: Complete analysis results including matched/missing keywords,
              weighted match percentage, and TF-IDF similarity score.
    """
    # If resume_skills is passed as strings/raw_text or list, extract keywords using spaCy NLP
    if isinstance(resume_skills, str):
        resume_kws = extract_keywords_nlp(resume_skills)
    elif isinstance(resume_skills, list) and resume_skills:
        # Also combine with full text extraction to catch noun chunks & entities
        resume_kws = list(set(resume_skills) | set(extract_keywords_nlp(resume_text)))
    else:
        resume_kws = extract_keywords_nlp(resume_text)

    # Extract keywords from job description
    jd_kws = extract_keywords_nlp(job_text)
    
    # Calculate weighted keyword match
    match_res = calculate_weighted_match(resume_kws, jd_kws)
    
    # Calculate TF-IDF similarity
    similarity_score = calculate_tfidf_similarity(resume_text, job_text)
    
    return {
        'job_skills': jd_kws,
        'matched_skills': match_res['matched'],
        'missing_skills': match_res['missing'],
        'match_percentage': match_res['match_percentage'],
        'similarity_score': similarity_score,
        'resume_keywords': resume_kws,
        'jd_keywords': jd_kws
    }

