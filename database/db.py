"""
database/db.py – Database Setup & Multi-Engine Helper Functions (SQLite & PostgreSQL)
====================================================================================
This module handles all database operations for the Resume Analyzer.
It seamlessly supports SQLite (local offline development) and PostgreSQL / Supabase / Neon
(persistent serverless database for production on Vercel) when DATABASE_URL is set.
"""

import sqlite3
import json
import os
from config import DATABASE_PATH, DATABASE_URL


def is_postgres():
    """Check if PostgreSQL environment variable DATABASE_URL is active."""
    return bool(DATABASE_URL and DATABASE_URL.startswith(('postgres://', 'postgresql://')))


def get_db_connection():
    """
    Create and return a database connection (PostgreSQL if DATABASE_URL is set, else SQLite).
    """
    if is_postgres():
        url = DATABASE_URL
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        try:
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        except Exception as e:
            print(f"PostgreSQL connection error: {e}. Falling back to SQLite.")

    # Default to SQLite for local development
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    return conn


def execute_db(query, params=(), fetchone=False, fetchall=False, return_id=False):
    """
    Unified database query executor supporting both SQLite and PostgreSQL.
    Handles parameter placeholder translation (? -> %s) and returning inserted IDs.
    """
    conn = get_db_connection()
    use_pg = is_postgres() and not isinstance(conn, sqlite3.Connection)

    # Translate parameter placeholders if using PostgreSQL (%s instead of ?)
    if use_pg:
        query_exec = query.replace('?', '%s')
        if return_id and 'RETURNING' not in query_exec.upper():
            query_exec = query_exec.rstrip('; ') + ' RETURNING id'
    else:
        query_exec = query

    cursor = conn.cursor()
    cursor.execute(query_exec, params)

    inserted_id = None
    if return_id:
        if use_pg:
            row = cursor.fetchone()
            if row:
                inserted_id = row['id'] if isinstance(row, dict) else row[0]
        else:
            inserted_id = cursor.lastrowid

    res = None
    if fetchone:
        row = cursor.fetchone()
        res = dict(row) if row else None
    elif fetchall:
        rows = cursor.fetchall()
        res = [dict(row) for row in rows]

    conn.commit()
    conn.close()

    if return_id:
        return inserted_id
    return res


def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    Supports both SQLite and PostgreSQL syntax automatically.
    """
    conn = get_db_connection()
    use_pg = is_postgres() and not isinstance(conn, sqlite3.Connection)
    cursor = conn.cursor()

    pk_type = "SERIAL PRIMARY KEY" if use_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"

    # ── Table 1: users ──
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            id {pk_type},
            full_name TEXT NOT NULL,
            identifier TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ── Table 2: resumes ──
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS resumes (
            id {pk_type},
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
        if use_pg:
            cursor.execute("ALTER TABLE resumes ADD COLUMN user_id INTEGER REFERENCES users(id)")
        else:
            cursor.execute("ALTER TABLE resumes ADD COLUMN user_id INTEGER REFERENCES users(id)")
    except Exception:
        pass  # Column already exists

    # ── Table 3: analyses ──
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS analyses (
            id {pk_type},
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
    try:
        clean_identifier = identifier.strip().lower()
        return execute_db(
            'INSERT INTO users (full_name, identifier, password_hash) VALUES (?, ?, ?)',
            (full_name.strip(), clean_identifier, password_hash),
            return_id=True
        )
    except Exception:
        return None  # Identifier already registered or DB error


def get_user_by_identifier(identifier):
    """Retrieve user by Email or Phone Number."""
    if not identifier:
        return None
    clean_identifier = identifier.strip().lower()
    return execute_db('SELECT * FROM users WHERE identifier = ?', (clean_identifier,), fetchone=True)


def get_user_by_id(user_id):
    """Retrieve user by integer ID."""
    if not user_id:
        return None
    return execute_db('SELECT * FROM users WHERE id = ?', (user_id,), fetchone=True)


# ──────────────────────────────────────────────────────────
# CRUD Operations (Resumes & Analyses)
# ──────────────────────────────────────────────────────────

def save_resume(filename, filepath, raw_text, parsed_data, user_id=None):
    """Save a new resume record to the database linked to user_id."""
    parsed_json = json.dumps(parsed_data) if isinstance(parsed_data, (dict, list)) else parsed_data
    return execute_db(
        'INSERT INTO resumes (filename, filepath, raw_text, parsed_data, user_id) VALUES (?, ?, ?, ?, ?)',
        (filename, filepath, raw_text, parsed_json, user_id),
        return_id=True
    )


def get_resume(resume_id):
    """Retrieve a resume record by its ID."""
    resume_dict = execute_db('SELECT * FROM resumes WHERE id = ?', (resume_id,), fetchone=True)
    if resume_dict:
        if resume_dict.get('parsed_data') and isinstance(resume_dict['parsed_data'], str):
            try:
                resume_dict['parsed_data'] = json.loads(resume_dict['parsed_data'])
            except Exception:
                pass
        return resume_dict
    return None


def save_analysis(resume_id, ats_score, score_breakdown, matched_skills,
                  missing_skills, match_percentage, suggestions,
                  job_recommendations, course_recommendations, job_description):
    """Save an analysis result to the database."""
    return execute_db('''
        INSERT INTO analyses 
        (resume_id, ats_score, score_breakdown, matched_skills, missing_skills,
         match_percentage, suggestions, job_recommendations, course_recommendations,
         job_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        ats_score,
        json.dumps(score_breakdown) if not isinstance(score_breakdown, str) else score_breakdown,
        json.dumps(matched_skills) if not isinstance(matched_skills, str) else matched_skills,
        json.dumps(missing_skills) if not isinstance(missing_skills, str) else missing_skills,
        match_percentage,
        json.dumps(suggestions) if not isinstance(suggestions, str) else suggestions,
        json.dumps(job_recommendations) if not isinstance(job_recommendations, str) else job_recommendations,
        json.dumps(course_recommendations) if not isinstance(course_recommendations, str) else course_recommendations,
        job_description
    ), return_id=True)


def get_analysis(analysis_id):
    """Retrieve an analysis record by its ID."""
    analysis_dict = execute_db('SELECT * FROM analyses WHERE id = ?', (analysis_id,), fetchone=True)
    if analysis_dict:
        for field in ['score_breakdown', 'matched_skills', 'missing_skills',
                      'suggestions', 'job_recommendations', 'course_recommendations']:
            if analysis_dict.get(field) and isinstance(analysis_dict[field], str):
                try:
                    analysis_dict[field] = json.loads(analysis_dict[field])
                except Exception:
                    pass
        return analysis_dict
    return None


def get_analysis_by_resume(resume_id):
    """Get the most recent analysis for a given resume."""
    analysis_dict = execute_db(
        'SELECT * FROM analyses WHERE resume_id = ? ORDER BY analysis_date DESC LIMIT 1',
        (resume_id,), fetchone=True
    )
    if analysis_dict:
        for field in ['score_breakdown', 'matched_skills', 'missing_skills',
                      'suggestions', 'job_recommendations', 'course_recommendations']:
            if analysis_dict.get(field) and isinstance(analysis_dict[field], str):
                try:
                    analysis_dict[field] = json.loads(analysis_dict[field])
                except Exception:
                    pass
        return analysis_dict
    return None


def get_all_analyses(user_id=None):
    """Get all analyses for a specific user. Returns empty list if no user_id is provided for privacy."""
    if not user_id:
        return []

    results = execute_db('''
        SELECT a.*, r.filename, r.upload_date 
        FROM analyses a 
        JOIN resumes r ON a.resume_id = r.id 
        WHERE r.user_id = ?
        ORDER BY a.analysis_date DESC
    ''', (user_id,), fetchall=True)
    
    for row in (results or []):
        for field in ['score_breakdown', 'matched_skills', 'missing_skills',
                      'suggestions', 'job_recommendations', 'course_recommendations']:
            if row.get(field) and isinstance(row[field], str):
                try:
                    row[field] = json.loads(row[field])
                except Exception:
                    pass
    return results or []
