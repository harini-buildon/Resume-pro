"""
tests/test_pdf_report.py – Unit & Integration Tests for PDF Report Generation & Download
==========================================================================================
Verifies:
1. Direct generation of PDF reports with generate_report() handling Unicode, missing fields, and custom sections.
2. PDF file binary integrity (%PDF- magic header).
3. HTTP /download-report/<id> route returning 200 OK and PDF attachment payload.
"""

import sys
import os
import unittest
import uuid
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from database.db import init_db, create_user, save_resume, save_analysis
from utils.report_generator import generate_report, sanitize_text


class TestPDFReport(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key-pdf'
        init_db()
        self.client = app.test_client()

    def test_sanitize_text_handles_unicode_and_types(self):
        self.assertEqual(sanitize_text(None), '')
        self.assertEqual(sanitize_text(123), '123')
        self.assertEqual(sanitize_text('Check ✓ and cross ✗'), 'Check [OK] and cross [X]')
        self.assertEqual(sanitize_text('Smart quote “hello” & dash — test'), 'Smart quote "hello" & dash -- test')

    def test_generate_report_creates_valid_pdf_file(self):
        parsed_data = {
            'name': 'Alex Johnson',
            'email': 'alex.johnson@example.com',
            'phone': '+1 (555) 019-2834',
            'linkedin': 'linkedin.com/in/alexjohnson',
            'github': 'github.com/alexjohnson',
            'skills': ['Python', 'Machine Learning', 'SQL', 'Flask', 'Docker', 'TensorFlow']
        }
        ats_result = {
            'total_score': 85,
            'breakdown': {
                'skills': {'label': 'Skills Match', 'score': 35, 'max': 40},
                'experience': {'label': 'Experience', 'score': 25, 'max': 30},
                'formatting': {'label': 'Formatting', 'score': 25, 'max': 30}
            }
        }
        suggestions = [
            {'priority': 'critical', 'category': 'Skills', 'message': 'Add PyTorch and Kubernetes experience.'},
            {'priority': 'important', 'category': 'Formatting', 'message': 'Quantify achievements with metrics.'}
        ]
        job_recommendations = [
            {'role': 'Machine Learning Engineer', 'fit_percentage': 92, 'description': 'Build & deploy ML models.'}
        ]
        course_recommendations = [
            {'topic': 'Advanced PyTorch', 'skill': 'PyTorch', 'description': 'Deep learning course.', 'platforms': 'Coursera'}
        ]
        job_match = {
            'matched_skills': ['Python', 'Machine Learning', 'SQL'],
            'missing_skills': ['PyTorch', 'Kubernetes'],
            'match_percentage': 75.0
        }

        filepath, filename = generate_report(
            parsed_data=parsed_data,
            ats_result=ats_result,
            suggestions=suggestions,
            job_recommendations=job_recommendations,
            course_recommendations=course_recommendations,
            job_match=job_match
        )

        # File assertions
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(os.path.getsize(filepath) > 500)  # Non-trivial PDF file size

        # Header assertion (%PDF- magic bytes)
        with open(filepath, 'rb') as f:
            header = f.read(5)
            self.assertEqual(header, b'%PDF-')

        # Clean up created PDF file
        try:
            os.remove(filepath)
        except Exception:
            pass

    def test_download_report_http_route(self):
        # 1. Register test user
        identifier = f"pdf_user_{uuid.uuid4().hex[:8]}@example.com"
        user_id = create_user("PDF Tester", identifier, generate_password_hash("testpass123"))

        # 2. Log in session
        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['user_name'] = "PDF Tester"

        # 3. Save resume and analysis record
        parsed_data = {'name': 'PDF Tester', 'email': identifier, 'skills': ['Python', 'SQL']}
        resume_id = save_resume("sample_resume.pdf", "uploads/test.pdf", "Sample text", parsed_data, user_id=user_id)

        ats_result = {'total_score': 80, 'breakdown': {}}
        save_analysis(
            resume_id=resume_id,
            ats_score=80,
            score_breakdown={'skills': {'label': 'Skills', 'score': 40, 'max': 50}},
            matched_skills=['Python'],
            missing_skills=['Java'],
            match_percentage=75.0,
            suggestions=[{'priority': 'important', 'category': 'General', 'message': 'Add projects'}],
            job_recommendations=[{'role': 'Software Developer', 'fit_percentage': 85, 'description': 'Dev role'}],
            course_recommendations=[{'topic': 'Java Basics', 'skill': 'Java', 'description': 'Intro', 'platforms': 'Udemy'}],
            job_description="Looking for Python and Java dev"
        )

        # 4. Trigger download endpoint
        response = self.client.get(f'/download-report/{resume_id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertIn(b'%PDF-', response.data[:10])


if __name__ == '__main__':
    unittest.main()
