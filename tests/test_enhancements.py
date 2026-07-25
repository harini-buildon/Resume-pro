"""
tests/test_enhancements.py – Unit Tests for All 6 Enhancement Modules
=======================================================================
Verifies:
1. AI Bullet Point Enhancer & Quantifier.
2. AI Cover Letter Generator.
3. Job Description URL Extractor.
4. AI Mock Interview Generator (STAR framework).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.bullet_enhancer import enhance_bullet_point, enhance_resume_bullets_batch
from utils.cover_letter import generate_cover_letter
from utils.job_scraper import extract_job_from_url
from utils.interview_generator import generate_mock_interview


class TestEnhancements(unittest.TestCase):

    def test_bullet_enhancer_basic(self):
        input_bullet = "Worked on Python code and fixed database bugs"
        res = enhance_bullet_point(input_bullet)

        self.assertIn('enhanced', res)
        self.assertIn('impact_score', res)
        self.assertTrue(any(verb in res['enhanced'] for verb in ["Engineered", "Optimized", "Architected", "Implemented"]))
        self.assertIn("%", res['enhanced'], "Enhanced bullet should contain a metric percentage")

    def test_bullet_enhancer_batch(self):
        bullets = ["Built React frontend components", "Worked on SQL queries"]
        res = enhance_resume_bullets_batch(bullets)

        self.assertEqual(len(res), 2)
        self.assertIsNotNone(res[0]['enhanced'])

    def test_cover_letter_generator(self):
        cl = generate_cover_letter(
            candidate_name="Alex Johnson",
            candidate_skills=["Python", "FastAPI", "Docker", "PostgreSQL"],
            job_title="Senior Backend Engineer",
            company_name="Acme Corp"
        )

        self.assertIn('cover_letter_text', cl)
        self.assertIn("Alex Johnson", cl['cover_letter_text'])
        self.assertIn("Acme Corp", cl['cover_letter_text'])
        self.assertIn("Senior Backend Engineer", cl['cover_letter_text'])

    def test_job_scraper_invalid_url(self):
        res = extract_job_from_url("invalid-url-string")
        self.assertEqual(res['status'], 'error')
        self.assertIn("Invalid URL", res['error_message'])

    def test_mock_interview_generator(self):
        questions = generate_mock_interview(
            candidate_skills=["Python", "Docker", "React"],
            missing_skills=["Kubernetes", "AWS"],
            target_role="Full Stack Engineer"
        )

        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)
        self.assertLessEqual(len(questions), 5)

        for q in questions:
            self.assertIn('question', q)
            self.assertIn('answer_framework', q)
            self.assertIn('type', q)


if __name__ == '__main__':
    unittest.main(verbosity=2)
