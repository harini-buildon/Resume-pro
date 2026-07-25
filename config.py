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

# ──────────────────────────────────────────────
# Base directory – resolves to the project root
# os.path.abspath(__file__) gives the full path of this config file,
# and os.path.dirname() strips the filename to get the directory.
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────
# Flask Settings
# ──────────────────────────────────────────────
SECRET_KEY = 'resume-analyzer-secret-key-change-in-production'

# ──────────────────────────────────────────────
# File Upload Settings
# ──────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MIN_CONTENT_LENGTH = 50 * 1024         # 50 KB minimum upload size
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maximum upload size

# ──────────────────────────────────────────────
# Database Settings
# ──────────────────────────────────────────────
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'resume_analyzer.db')

# ──────────────────────────────────────────────
# Report Settings
# ──────────────────────────────────────────────
REPORT_FOLDER = os.path.join(BASE_DIR, 'static', 'reports')
