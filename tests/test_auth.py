"""
tests/test_auth.py – Unit & Integration Tests for User Authentication
========================================================================
Verifies:
1. Registration with Email & Phone Number.
2. Login with Email or Phone Number + Password hashing verification.
3. Preventing duplicate registration.
4. Flask session handling and logout.
"""

import sys
import os
import unittest
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from database.db import init_db, create_user, get_user_by_identifier, get_user_by_id


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        init_db()
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'

    def test_create_and_fetch_user_by_email(self):
        identifier = f"test_email_{uuid.uuid4().hex[:8]}@example.com"
        pwd_hash = generate_password_hash("securepass123")

        user_id = create_user("Test Email User", identifier, pwd_hash)
        self.assertIsNotNone(user_id)

        user = get_user_by_identifier(identifier)
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], "Test Email User")
        self.assertTrue(check_password_hash(user['password_hash'], "securepass123"))

    def test_create_and_fetch_user_by_phone(self):
        phone_identifier = f"+15550199{uuid.uuid4().hex[:4]}"
        pwd_hash = generate_password_hash("myphonepass456")

        user_id = create_user("Test Phone User", phone_identifier, pwd_hash)
        self.assertIsNotNone(user_id)

        user = get_user_by_identifier(phone_identifier)
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], "Test Phone User")
        self.assertTrue(check_password_hash(user['password_hash'], "myphonepass456"))

    def test_prevent_duplicate_identifier(self):
        identifier = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
        pwd_hash = generate_password_hash("password123")

        first_id = create_user("User One", identifier, pwd_hash)
        self.assertIsNotNone(first_id)

        second_id = create_user("User Two", identifier, pwd_hash)
        self.assertIsNone(second_id, "Duplicate identifier registration should return None")

    def test_signup_login_logout_flow(self):
        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        signup_data = {
            'full_name': 'Integration User',
            'identifier': unique_email,
            'password': 'password123',
            'confirm_password': 'password123'
        }
        res = self.client.post('/signup', data=signup_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Log out
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)

        # Log in
        login_data = {
            'identifier': unique_email,
            'password': 'password123'
        }
        res_login = self.client.post('/login', data=login_data, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)

    def test_download_report_requires_login(self):
        # Unauthenticated user attempting to download report
        res = self.client.get('/download-report/1', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.location)


if __name__ == '__main__':
    unittest.main(verbosity=2)
