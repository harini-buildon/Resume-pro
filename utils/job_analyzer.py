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

import math
import re
from collections import Counter
from utils.skills_db import match_skills
from utils.nlp_processor import extract_keywords_nlp, calculate_weighted_match

ENGLISH_STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'cannot', 'could',
    'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have',
    'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is',
    'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should',
    'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
    'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what',
    'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you', 'your', 'yours', 'yourself',
    'yourselves'
}


def _tokenize_text(text):
    """Tokenize text into unigrams and bigrams, ignoring stop words."""
    words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_\-\./+#]+\b', text)]
    unigrams = [w for w in words if w not in ENGLISH_STOP_WORDS and len(w) > 1]
    bigrams = [
        f"{words[i]} {words[i+1]}"
        for i in range(len(words) - 1)
        if words[i] not in ENGLISH_STOP_WORDS and words[i+1] not in ENGLISH_STOP_WORDS
    ]
    return unigrams + bigrams


def extract_job_skills(job_text):
    """Extract keywords and recognized skills from a job description using NLP."""
    return extract_keywords_nlp(job_text)


def compare_skills(resume_skills, job_skills):
    """Compare resume skills with job description skills using weighted matching."""
    return calculate_weighted_match(resume_skills, job_skills)


def calculate_tfidf_similarity(resume_text, job_text):
    """
    Calculate the similarity between resume and job description
    using pure Python TF-IDF Vectorization + Cosine Similarity.

    Uses unigrams AND bigrams so that multi-word skills like
    "Machine Learning", "System Design", "CI/CD" are scored properly.

    Sublinear TF scaling: 1 + log(tf) dampens high-frequency terms.
    Smooth IDF formula: log((1 + n) / (1 + df)) + 1 matches scikit-learn.
    """
    if not resume_text or not job_text:
        return 0.0

    try:
        tokens1 = _tokenize_text(resume_text)
        tokens2 = _tokenize_text(job_text)

        if not tokens1 or not tokens2:
            return 0.0

        tf1 = Counter(tokens1)
        tf2 = Counter(tokens2)

        vocab = set(tf1.keys()).union(set(tf2.keys()))
        num_docs = 2.0

        vec1 = {}
        vec2 = {}

        for term in vocab:
            df = (1.0 if term in tf1 else 0.0) + (1.0 if term in tf2 else 0.0)
            idf = math.log((1.0 + num_docs) / (1.0 + df)) + 1.0

            if term in tf1:
                vec1[term] = (1.0 + math.log(tf1[term])) * idf
            if term in tf2:
                vec2[term] = (1.0 + math.log(tf2[term])) * idf

        dot_product = sum(vec1.get(t, 0.0) * vec2.get(t, 0.0) for t in vocab)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return round(float(similarity) * 100, 1)
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

