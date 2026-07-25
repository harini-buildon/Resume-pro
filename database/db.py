"""
database/db.py – SQLite Database Setup & Helper Functions
==========================================================
This module handles all database operations for the Resume Analyzer.

KEY CONCEPTS FOR BEGINNERS:
──────────────────────────
1. SQLite: A lightweight database stored as a single file (no server needed).
2. Connection: We open a connection to talk to the database, like opening a file.
3. Cursor: Think of it as a pointer that executes SQL commands.
4. Commit: Saves changes permanently (like Ctrl+S for the database).
5. JSON storage: We store complex data (lists, dicts) as JSON strings in TEXT columns.

TABLES:
──────
- resumes: Stores uploaded resume files and their extracted text/parsed data.
- analyses: Stores the analysis results (ATS score, skills, suggestions, etc.).
"""

import sqlite3
import json
import os
from config import DATABASE_PATH


def get_db_connection():
    """
    Create and return a database connection.
    
    sqlite3.Row allows us to access columns by name (like a dictionary)
    instead of by index number. For example:
        row['filename'] instead of row[1]
    """
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn


def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ── Table 1: users ──
    # Stores registered users with identifier (Email or Phone Number)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            identifier TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ── Table 2: resumes ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            raw_text TEXT,
            parsed_data TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Migration: Add user_id column to resumes if table existed without it
    try:
        cursor.execute("ALTER TABLE resumes ADD COLUMN user_id INTEGER REFERENCES users(id)")
    except Exception:
        pass  # Column already exists

    # ── Table 3: analyses ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            ats_score REAL,
            score_breakdown TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            match_percentage REAL,
            suggestions TEXT,
            job_recommendations TEXT,
            course_recommendations TEXT,
            job_description TEXT,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


# ──────────────────────────────────────────────────────────
# User Auth Helpers
# ──────────────────────────────────────────────────────────

def create_user(full_name, identifier, password_hash):
    """
    Register a new user in the database.
    Identifier can be an Email Address or Phone Number.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        clean_identifier = identifier.strip().lower()
        cursor.execute(
            'INSERT INTO users (full_name, identifier, password_hash) VALUES (?, ?, ?)',
            (full_name.strip(), clean_identifier, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Identifier already registered
    finally:
        conn.close()


def get_user_by_identifier(identifier):
    """
    Retrieve user by Email or Phone Number.
    """
    if not identifier:
        return None
    conn = get_db_connection()
    clean_identifier = identifier.strip().lower()
    user = conn.execute('SELECT * FROM users WHERE identifier = ?', (clean_identifier,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    """Retrieve user by integer ID."""
    if not user_id:
        return None
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


# ──────────────────────────────────────────────────────────
# CRUD Operations (Resumes & Analyses)
# ──────────────────────────────────────────────────────────

def save_resume(filename, filepath, raw_text, parsed_data, user_id=None):
    """
    Save a new resume record to the database linked to user_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO resumes (filename, filepath, raw_text, parsed_data, user_id) VALUES (?, ?, ?, ?, ?)',
        (filename, filepath, raw_text, json.dumps(parsed_data), user_id)
    )
    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id


def get_resume(resume_id):
    """
    Retrieve a resume record by its ID.
    
    Returns:
        dict or None: The resume record, or None if not found
    """
    conn = get_db_connection()
    resume = conn.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,)).fetchone()
    conn.close()
    
    if resume:
        # Convert sqlite3.Row to a regular dict so we can modify it
        resume_dict = dict(resume)
        # Parse the JSON string back into a Python dictionary
        if resume_dict.get('parsed_data'):
            resume_dict['parsed_data'] = json.loads(resume_dict['parsed_data'])
        return resume_dict
    return None


def save_analysis(resume_id, ats_score, score_breakdown, matched_skills,
                  missing_skills, match_percentage, suggestions,
                  job_recommendations, course_recommendations, job_description):
    """
    Save an analysis result to the database.
    
    All complex data types (lists, dicts) are converted to JSON strings
    because SQLite only supports TEXT, INTEGER, REAL, and BLOB types.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analyses 
        (resume_id, ats_score, score_breakdown, matched_skills, missing_skills,
         match_percentage, suggestions, job_recommendations, course_recommendations,
         job_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        ats_score,
        json.dumps(score_breakdown),
        json.dumps(matched_skills),
        json.dumps(missing_skills),
        match_percentage,
        json.dumps(suggestions),
        json.dumps(job_recommendations),
        json.dumps(course_recommendations),
        job_description
    ))
    
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def get_analysis(analysis_id):
    """Retrieve an analysis record by its ID."""
    conn = get_db_connection()
    analysis = conn.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,)).fetchone()
    conn.close()
    
    if analysis:
        analysis_dict = dict(analysis)
        # Parse all JSON fields back to Python objects
        for field in ['score_breakdown', 'matched_skills', 'missing_skills',
                      'suggestions', 'job_recommendations', 'course_recommendations']:
            if analysis_dict.get(field):
                analysis_dict[field] = json.loads(analysis_dict[field])
        return analysis_dict
    return None


def get_analysis_by_resume(resume_id):
    """Get the most recent analysis for a given resume."""
    conn = get_db_connection()
    analysis = conn.execute(
        'SELECT * FROM analyses WHERE resume_id = ? ORDER BY analysis_date DESC LIMIT 1',
        (resume_id,)
    ).fetchone()
    conn.close()
    
    if analysis:
        analysis_dict = dict(analysis)
        for field in ['score_breakdown', 'matched_skills', 'missing_skills',
                      'suggestions', 'job_recommendations', 'course_recommendations']:
            if analysis_dict.get(field):
                analysis_dict[field] = json.loads(analysis_dict[field])
        return analysis_dict
    return None


def get_all_analyses(user_id=None):
    """Get all analyses with resume info, optionally filtered by user_id."""
    conn = get_db_connection()
    if user_id:
        results = conn.execute('''
            SELECT a.*, r.filename, r.upload_date 
            FROM analyses a 
            JOIN resumes r ON a.resume_id = r.id 
            WHERE r.user_id = ?
            ORDER BY a.analysis_date DESC
        ''', (user_id,)).fetchall()
    else:
        results = conn.execute('''
            SELECT a.*, r.filename, r.upload_date 
            FROM analyses a 
            JOIN resumes r ON a.resume_id = r.id 
            ORDER BY a.analysis_date DESC
        ''').fetchall()
    conn.close()
    return [dict(row) for row in results]
