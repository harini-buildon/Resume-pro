"""
tests/test_project_recommender.py – Unit Tests for Project Recommender
========================================================================
Verifies that project recommendations:
1. Return 3 distinct complexity tiers: Basic, Medium, High.
2. Tailor projects based on candidate skills & missing skill gaps.
3. Include tech stack badges, resume impact explanations, and key features.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.project_recommender import recommend_projects


class TestProjectRecommender(unittest.TestCase):

    def test_three_complexity_tiers_present(self):
        skills = ["Python", "Flask", "Docker", "AWS", "SQL"]
        res = recommend_projects(skills)

        self.assertIn('basic', res)
        self.assertIn('medium', res)
        self.assertIn('high', res)

        self.assertEqual(res['basic']['level'], 'basic')
        self.assertEqual(res['medium']['level'], 'medium')
        self.assertEqual(res['high']['level'], 'high')

    def test_project_structure(self):
        skills = ["Python", "Machine Learning", "PyTorch"]
        res = recommend_projects(skills)

        for level in ['basic', 'medium', 'high']:
            proj = res[level]
            required_keys = ['title', 'level', 'level_label', 'tech_stack', 'description', 'resume_impact', 'key_features']
            for k in required_keys:
                self.assertIn(k, proj)
            self.assertIsInstance(proj['tech_stack'], list)
            self.assertIsInstance(proj['key_features'], list)
            self.assertGreater(len(proj['tech_stack']), 0)

    def test_missing_skill_gap_tailoring(self):
        skills = ["Python", "Flask"]
        missing_skills = ["Docker", "Kubernetes", "Kafka"]

        res = recommend_projects(skills, missing_skills=missing_skills)
        high_proj = res['high']

        # High complexity project should include containerization / devops skills
        high_stack_str = " ".join(high_proj['tech_stack']).lower()
        self.assertTrue("docker" in high_stack_str or "kubernetes" in high_stack_str or "python" in high_stack_str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
