"""
tests/test_company_recommender.py – Unit Tests for Company & Internship Recommender
=====================================================================================
Verifies that company recommendations:
1. Support experience-tailoring (Internships for students/freshers vs Full-time roles for experienced).
2. Classify company tiers (Startups / Unicorns vs Top Tech Giants).
3. Identify work modes (Work From Home / Remote vs In-Office / Hybrid).
4. Generate valid Google Jobs search URLs with recent time filters.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.company_recommender import recommend_hiring_companies, detect_candidate_experience_level


class TestCompanyRecommender(unittest.TestCase):

    def test_fresher_experience_detection(self):
        parsed_student = {'experience': [], 'education': ['B.Tech Computer Science 2026']}
        raw_text = "Pursuing B.Tech Computer Science student looking for software internship"

        exp_info = detect_candidate_experience_level(parsed_student, raw_text)
        self.assertTrue(exp_info['is_fresher'])
        self.assertEqual(exp_info['preferred_opportunity'], 'internship')

    def test_experienced_candidate_detection(self):
        parsed_exp = {
            'experience': [
                'Software Engineer at TechCorp (2022 - Present)',
                'Junior Developer at WebStudio (2020 - 2022)'
            ]
        }
        exp_info = detect_candidate_experience_level(parsed_exp, "Senior backend engineer with 4 years experience")
        self.assertFalse(exp_info['is_fresher'])
        self.assertEqual(exp_info['preferred_opportunity'], 'full_time')

    def test_internship_recommendations_for_fresher(self):
        skills = ["React", "JavaScript", "Python", "HTML"]
        parsed_fresher = {'experience': []}

        res = recommend_hiring_companies(skills, ats_score=70, parsed_data=parsed_fresher, raw_text="Student candidate")
        self.assertIn('companies', res)
        companies = res['companies']
        self.assertGreater(len(companies), 0)

        # Check internship badges and work modes
        for comp in companies:
            self.assertIn("Internship", comp['opportunity_type'])
            self.assertIn('work_mode', comp)
            self.assertTrue(
                "Remote" in comp['work_mode'] or "Office" in comp['work_mode'] or "Both" in comp['work_mode']
            )

    def test_mix_of_startups_and_tech_giants(self):
        skills = ["Python", "Flask", "Docker", "AWS", "PostgreSQL"]

        res = recommend_hiring_companies(skills, ats_score=85)
        companies = res['companies']

        company_types = [c['company_type'] for c in companies]
        self.assertTrue(any(t == 'startup' for t in company_types), "Should include high-growth startups")
        self.assertTrue(any(t == 'giant' for t in company_types), "Should include top tech giants")

    def test_recent_hiring_badge_and_search_url(self):
        skills = ["Java", "Microservices", "Kubernetes"]
        res = recommend_hiring_companies(skills, ats_score=80)

        for comp in res['companies']:
            self.assertTrue(comp['apply_url'].startswith("https://www.google.com/search?"))
            self.assertIn("qdr%3Aw", comp['apply_url'])  # Recent past week filter
            self.assertTrue(
                "Active" in comp['hiring_badge'] or
                "Urgent" in comp['hiring_badge'] or
                "Featured" in comp['hiring_badge'] or
                "Growth" in comp['hiring_badge']
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
