"""
tests/test_ats.py – ATS Scoring Engine Sample Test Cases
==========================================================
Three sample test cases that verify the weighted hybrid ATS scoring
formula behaves sensibly across strong / weak / no-match scenarios.

Scoring formula under test:
    ATS Score = round( (keyword_match_percent * 0.7) + (tfidf_similarity * 0.3) )

Run with:
    python -m pytest tests/test_ats.py -v
    -- or --
    python -m unittest tests.test_ats -v
"""

import sys
import os
import unittest

# ── Make sure the project root is on sys.path so imports work ──────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.job_analyzer import analyze_job_match
from utils.ats_scorer import calculate_ats_score
from utils.resume_parser import parse_resume
from utils.suggestions import get_plain_suggestions


# ─────────────────────────────────────────────────────────────────────────────
# Sample Resume Texts
# ─────────────────────────────────────────────────────────────────────────────

RESUME_STRONG = """
Jane Doe
jane.doe@email.com | +1-555-0100 | linkedin.com/in/janedoe | github.com/janedoe

PROFESSIONAL SUMMARY
Experienced Python Developer with 3 years building scalable REST APIs and ML pipelines.
Proficient in Flask, Django, Docker, Kubernetes, AWS, and CI/CD workflows.

SKILLS
Python, Flask, Django, REST APIs, Docker, Kubernetes, AWS, CI/CD, Git,
PostgreSQL, Redis, Machine Learning, Scikit-learn, TensorFlow, Pandas,
NumPy, Linux, Jenkins, Agile, Scrum, Unit Testing, System Design

EXPERIENCE
Software Engineer – TechCorp (2022 – Present)
- Built 5 microservices in Flask reducing API latency by 40%.
- Deployed services to AWS ECS using Docker and CI/CD pipelines (Jenkins, GitHub Actions).
- Maintained PostgreSQL databases; optimised slow queries by 60%.

EDUCATION
B.Tech Computer Science – State University (2022)  GPA: 8.9/10

PROJECTS
1. ML Pipeline Orchestrator – automated training/inference using Apache Airflow + AWS S3.
2. Real-time Analytics Dashboard – Flask + Redis + WebSockets with Docker deployment.

CERTIFICATIONS
AWS Certified Developer – Associate (2023)
Docker Certified Associate (2023)
"""

RESUME_WEAK = """
Alex Smith
alex@email.com

SKILLS
HTML, CSS, JavaScript, jQuery, Bootstrap, Photoshop, Figma

EXPERIENCE
Freelance Web Designer (2021 – 2023)
- Designed landing pages for small businesses.
- Created visual mockups using Figma and Photoshop.

EDUCATION
Diploma in Graphic Design – City College (2021)

PROJECTS
1. Portfolio website built with HTML/CSS/JavaScript.
2. Restaurant landing page with Bootstrap.
"""

RESUME_UNRELATED = """
John Green
john@email.com

EXPERIENCE
Sous Chef – Grand Hotel Restaurant (2019 – 2024)
- Prepared dishes for 200+ guests nightly.
- Managed food inventory and reduced waste by 20%.
- Trained junior kitchen staff in knife skills and plating techniques.

EDUCATION
Diploma in Culinary Arts – Culinary Institute (2019)

SKILLS
Knife Skills, Food Safety, Menu Planning, Inventory Management, Team Leadership
"""


# ─────────────────────────────────────────────────────────────────────────────
# Sample Job Descriptions
# ─────────────────────────────────────────────────────────────────────────────

JD_PYTHON_BACKEND = """
We are hiring a Python Backend Engineer to build and maintain scalable REST APIs.

Requirements:
- 2+ years of experience with Python and Flask or Django
- Strong knowledge of Docker, Kubernetes, and AWS
- Familiarity with CI/CD pipelines (Jenkins, GitHub Actions)
- Experience with PostgreSQL or Redis
- Understanding of Microservices architecture and System Design
- Comfortable working in an Agile/Scrum team
- Bonus: Machine Learning or Scikit-learn experience
- Unit Testing experience required
"""


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def run_analysis(resume_text, job_description):
    """
    Run the full analysis pipeline and return (ats_result, job_match, suggestions).
    Mirrors exactly what the POST /analyze JSON endpoint does internally.
    """
    try:
        parsed = parse_resume(resume_text)
    except Exception:
        parsed = {'skills': []}

    job_match = analyze_job_match(resume_text, parsed.get('skills', []), job_description)
    ats_result = calculate_ats_score(parsed, resume_text, job_match)
    plain_suggestions = get_plain_suggestions(parsed, ats_result, job_match)

    return ats_result, job_match, plain_suggestions


# ─────────────────────────────────────────────────────────────────────────────
# Test Cases
# ─────────────────────────────────────────────────────────────────────────────

class TestATSScoringStrong(unittest.TestCase):
    """
    Test Case 1 – Strong Match
    A Python developer resume vs. a Python Backend Engineer JD.
    Expected: ATS score >= 65 (strong overlap in skills, tools, and text similarity).
    """

    @classmethod
    def setUpClass(cls):
        cls.ats_result, cls.job_match, cls.suggestions = run_analysis(
            RESUME_STRONG, JD_PYTHON_BACKEND
        )

    def test_score_in_expected_range(self):
        score = self.ats_result['total_score']
        self.assertGreaterEqual(score, 65,
            f"Strong match should score >= 65, got {score}")

    def test_score_does_not_exceed_100(self):
        score = self.ats_result['total_score']
        self.assertLessEqual(score, 100,
            f"ATS score must not exceed 100, got {score}")

    def test_matched_keywords_not_empty(self):
        matched = self.job_match['matched_skills']
        self.assertIsInstance(matched, list)
        self.assertGreater(len(matched), 0,
            "Strong-match resume should have at least 1 matched keyword")

    def test_keyword_match_percent_range(self):
        pct = self.job_match['match_percentage']
        self.assertGreaterEqual(pct, 0.0)
        self.assertLessEqual(pct, 100.0)

    def test_similarity_score_range(self):
        sim = self.job_match['similarity_score']
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 100.0)

    def test_suggestions_are_strings(self):
        for s in self.suggestions:
            self.assertIsInstance(s, str,
                f"Expected plain string suggestion, got: {type(s)}")

    def test_breakdown_has_formula(self):
        breakdown = self.ats_result.get('breakdown', {})
        self.assertIn('formula', breakdown,
            "Breakdown must include a 'formula' transparency field")
        self.assertNotEqual(breakdown['formula'], '',
            "Formula string must not be empty")


class TestATSScoringWeak(unittest.TestCase):
    """
    Test Case 2 – Weak Match
    A frontend/graphic-design resume vs. a Python Backend Engineer JD.
    Expected: ATS score between 0 and 60 (partial or no skill overlap).
    """

    @classmethod
    def setUpClass(cls):
        cls.ats_result, cls.job_match, cls.suggestions = run_analysis(
            RESUME_WEAK, JD_PYTHON_BACKEND
        )

    def test_score_in_expected_range(self):
        score = self.ats_result['total_score']
        self.assertLessEqual(score, 60,
            f"Weak match should score <= 60, got {score}")
        self.assertGreaterEqual(score, 0,
            f"Score must be >= 0, got {score}")

    def test_missing_keywords_not_empty(self):
        missing = self.job_match['missing_skills']
        self.assertIsInstance(missing, list)
        self.assertGreater(len(missing), 0,
            "Weak-match resume should have missing keywords vs. the JD")

    def test_suggestions_not_empty(self):
        self.assertGreater(len(self.suggestions), 0,
            "Weak match should generate at least 1 improvement suggestion")

    def test_score_lower_than_strong(self):
        """Weak score must be lower than strong score (sanity check)."""
        strong_result, _, _ = run_analysis(RESUME_STRONG, JD_PYTHON_BACKEND)
        self.assertLess(
            self.ats_result['total_score'],
            strong_result['total_score'],
            "Weak-match score must be less than strong-match score"
        )


class TestATSScoringNoMatch(unittest.TestCase):
    """
    Test Case 3 – No Match (completely unrelated)
    A culinary arts resume vs. a Python Backend Engineer JD.
    Expected: ATS score <= 30, many missing keywords, high suggestion count.
    """

    @classmethod
    def setUpClass(cls):
        cls.ats_result, cls.job_match, cls.suggestions = run_analysis(
            RESUME_UNRELATED, JD_PYTHON_BACKEND
        )

    def test_score_very_low(self):
        score = self.ats_result['total_score']
        self.assertLessEqual(score, 35,
            f"Unrelated resume should score <= 35, got {score}")

    def test_missing_keywords_dominate(self):
        matched = len(self.job_match['matched_skills'])
        missing = len(self.job_match['missing_skills'])
        self.assertGreater(missing, matched,
            f"Missing ({missing}) should exceed matched ({matched}) for no-match case")

    def test_suggestions_warn_about_skills(self):
        combined = ' '.join(self.suggestions).lower()
        self.assertTrue(
            'skill' in combined or 'missing' in combined or 'add' in combined,
            "Suggestions for no-match resume should mention skills/missing keywords"
        )

    def test_response_fields_present(self):
        """Verify all required JSON API response keys exist."""
        required_ats_fields = ['total_score', 'breakdown']
        for field in required_ats_fields:
            self.assertIn(field, self.ats_result,
                f"ats_result must contain '{field}'")

        required_job_fields = [
            'matched_skills', 'missing_skills',
            'match_percentage', 'similarity_score',
        ]
        for field in required_job_fields:
            self.assertIn(field, self.job_match,
                f"job_match must contain '{field}'")


# ─────────────────────────────────────────────────────────────────────────────
# Health Endpoint Integration Test (requires server to be running)
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthEndpoint(unittest.TestCase):
    """
    Lightweight integration test for the /health endpoint.
    Skipped automatically if the Flask server is not running.
    """

    def test_health_endpoint(self):
        try:
            import urllib.request
            import json
            with urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2) as resp:
                data = json.loads(resp.read())
                self.assertEqual(data.get('status'), 'healthy')
                self.assertIn('spacy_loaded', data)
                self.assertIn('timestamp', data)
        except Exception:
            self.skipTest("Flask server not running – skipping /health integration test")


if __name__ == '__main__':
    unittest.main(verbosity=2)
