"""
config.py – Application Configuration
======================================
This file stores all configuration constants used across the Flask app.
Keeping configuration in one place makes the project easy to manage and modify.

Key concepts:
- SECRET_KEY: Flask uses this for session security and flash messages.
- UPLOAD_FOLDER: Where uploaded resumes are stored on disk.
- ALLOWED_EXTENSIONS: Only PDF and DOCX files are accepted.
- MAX_CONTENT_LENGTH: Limits upload size to prevent abuse (16 MB).
- DATABASE_PATH: Location of the SQLite database file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ──────────────────────────────────────────────
# Base directory & Environment detection
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_VERCEL = bool(os.environ.get('VERCEL')) or 'VERCEL' in os.environ

# ──────────────────────────────────────────────
# Flask Settings
# ──────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'resume-analyzer-secret-key-change-in-production')

# Security Settings for Session Cookies
SESSION_COOKIE_SECURE = True   # Requires HTTPS in production
SESSION_COOKIE_HTTPONLY = True # Prevent client-side JS from accessing cookies


# ──────────────────────────────────────────────
# File Upload & Database Settings (Writable /tmp on Vercel / Cloud Functions)
# ──────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

if IS_VERCEL:
    UPLOAD_FOLDER = '/tmp/uploads'
    DATABASE_PATH = '/tmp/database/resume_analyzer.db'
    REPORT_FOLDER = '/tmp/reports'
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'resume_analyzer.db')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'static', 'reports')

ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MIN_CONTENT_LENGTH = 50              # 50 bytes minimum upload size (prevents empty files)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maximum upload size

# Ensure target directories exist safely with fallback to /tmp
for folder in [UPLOAD_FOLDER, os.path.dirname(DATABASE_PATH), REPORT_FOLDER]:
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Directory creation notice for {folder}: {e}")
