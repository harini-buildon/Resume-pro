"""
app.py – Main Flask Application
================================
This is the main entry point of the AI-Powered Resume Analyzer project.
It defines all application routes, manages the upload flow, interacts with the 
database, and orchestrates the utility modules to perform analysis.

KEY CONCEPTS FOR BEGINNERS:
──────────────────────────
1. Routes: Functions decorated with @app.route() map a URL path to a Python function.
2. request: Flask object containing data sent from the browser (e.g., files, form text).
3. render_template: Renders an HTML page from the templates/ directory, inserting variables.
4. redirect / url_for: Navigates the browser to a different route.
5. flash: Stores temporary messages in the session to display alerts to the user.
6. DB Integration: Stores resume text, parsed fields, and analysis reports in SQLite.
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY
from database.db import (
    init_db, save_resume, get_resume, save_analysis, 
    get_analysis_by_resume, get_all_analyses,
    create_user, get_user_by_identifier, get_user_by_id
)
from utils.file_handler import save_uploaded_file, get_file_extension
from utils.text_extractor import extract_text
from utils.resume_parser import parse_resume
from utils.job_analyzer import analyze_job_match
from utils.ats_scorer import calculate_ats_score
from utils.suggestions import generate_suggestions, get_plain_suggestions
from utils.job_recommender import recommend_jobs
from utils.company_recommender import recommend_hiring_companies
from utils.project_recommender import recommend_projects
from utils.course_recommender import recommend_courses, recommend_general_courses
from utils.bullet_enhancer import enhance_bullet_point, enhance_resume_bullets_batch
from utils.cover_letter import generate_cover_letter
from utils.job_scraper import extract_job_from_url
from utils.interview_generator import generate_mock_interview
from utils.report_generator import generate_report
from utils.nlp_processor import get_spacy_nlp

# Initialize the Flask App
app = Flask(__name__)

# Security Extensions
csrf = CSRFProtect(app)

# ── Bug 3: Rate limiter – use Redis when available (shared across workers) ──
_limiter_storage = "memory://"  # Default: in-memory (single-worker local dev)
_redis_url = os.environ.get('REDIS_URL')
if _redis_url:
    try:
        _limiter_storage = _redis_url
        print(f"Rate limiter: using Redis ({_redis_url[:30]}...)")
    except Exception:
        print("Rate limiter: Redis URL set but unusable; falling back to memory://")

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=_limiter_storage
)

# ── Bug 2: Apply secure cookie settings from config ──
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize SQLite DB and Cache spaCy model at app startup (if installed)
try:
    init_db()
except Exception as e:
    print(f"Warning: Could not initialize DB at startup: {e}")

try:
    nlp_model = get_spacy_nlp()
    if nlp_model is not None:
        print("spaCy model (en_core_web_sm) loaded successfully at app startup.")
    else:
        print("spaCy model not installed/available; using pure Python NLP processor.")
except Exception as e:
    print(f"Warning: Could not pre-load spaCy model at startup: {e}")
def fetch_resume(resume_id):
    """

    Retrieve resume from database.
    If not found in DB (e.g. serverless cold start / ephemeral SQLite),
    fall back to Flask session cached data.
    """
    resume = get_resume(resume_id)
    if not resume and session.get('last_resume'):
        last = session['last_resume']
        if not resume_id or str(last.get('id')) == str(resume_id) or resume_id == 0:
            return last
    return resume


# ──────────────────────────────────────────────────────────

# Health Check Endpoint
# ──────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint — used by load balancers and uptime monitors."""
    status = {}

    # Check spaCy NLP model
    try:
        nlp = get_spacy_nlp()
        status['spacy_loaded'] = nlp is not None
    except Exception:
        status['spacy_loaded'] = False

    # Check database connectivity
    try:
        from database.db import execute_db
        execute_db('SELECT 1', fetchone=True)
        status['db'] = 'ok'
    except Exception as db_err:
        status['db'] = f'error: {str(db_err)[:80]}'

    http_status = 200 if status.get('db') == 'ok' else 503
    return jsonify({
        'status': 'healthy' if http_status == 200 else 'degraded',
        'spacy_loaded': status['spacy_loaded'],
        'db': status['db'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), http_status


# ──────────────────────────────────────────────────────────
# Custom Template Filter for Jinja
# ──────────────────────────────────────────────────────────
@app.template_filter('round')
def round_filter(value, precision=0):
    """Jinja template filter to round floats cleanly."""
    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return value


# ──────────────────────────────────────────────────────────
# Error Handlers
# ──────────────────────────────────────────────────────────
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle files that exceed the 16MB file upload limit."""
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'error': 'The uploaded file exceeds the 16MB limit.'}), 413
    return render_template(
        'error.html', 
        error_title="File Too Large", 
        error_message="The uploaded file exceeds the maximum allowed size of 16 MB. Please compress your file or upload a text-only version. Accepted file size range: 50 KB – 16 MB."
    ), 413


@app.errorhandler(404)
def page_not_found(error):
    """Handle non-existent URLs (404 Page Not Found)."""
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'error': 'Resource not found'}), 404
    return render_template(
        'error.html', 
        error_title="Page Not Found", 
        error_message="The page you are looking for does not exist or has been moved."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal python crashes gracefully."""
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'error': 'Internal server error'}), 500
    return render_template(
        'error.html', 
        error_title="Internal Server Error", 
        error_message="Something went wrong on our servers. We are looking into it. Please try again later."
    ), 500


# ──────────────────────────────────────────────────────────
# Application Routes
# ──────────────────────────────────────────────────────────

@app.route('/')
def home():
    """Module 1 – Home Page"""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def upload():
    """
    Module 2 & 3 – Resume Upload & Extraction
    GET:  Display the file upload form.
    POST: Receive uploaded file (PDF/DOCX), extract raw text, parse data.
          Supports both HTML web form and JSON API clients.
    """
    if request.method == 'POST':
        if 'resume' not in request.files:
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'No file part in the request under key "resume".'}), 400
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        if file.filename == '':
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'No selected file.'}), 400
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        success, result = save_uploaded_file(file)
        if not success:
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': result}), 400
            flash(result, 'danger')
            return redirect(request.url)
        
        filepath = result
        filename = file.filename
        
        text_success, text_result = extract_text(filepath)
        if not text_success:
            if os.path.exists(filepath):
                os.remove(filepath)
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': text_result}), 400
            flash(text_result, 'danger')
            return redirect(request.url)
        
        raw_text = text_result
        try:
            parsed_data = parse_resume(raw_text)
        except Exception as e:
            parsed_data = {}
            
        try:
            user_id = session.get('user_id')
            resume_id = save_resume(filename, filepath, raw_text, parsed_data, user_id=user_id)
            
            # Cache active resume in Flask session for fallback recovery on ephemeral DB restarts
            session['last_resume'] = {
                'id': resume_id,
                'filename': filename,
                'filepath': filepath,
                'raw_text': raw_text[:2000],
                'parsed_data': parsed_data
            }
            
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'success',
                    'resume_id': resume_id,
                    'filename': filename,
                    'raw_text': raw_text,
                    'parsed_data': parsed_data
                }), 200
                
            flash('Resume uploaded and text extracted successfully!', 'success')
            return redirect(url_for('extracted', resume_id=resume_id))
        except Exception as e:
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return jsonify({'error': f"Database error: {str(e)}"}), 500
            flash(f"Database error while saving resume: {str(e)}", 'danger')
            return redirect(request.url)
            
    return render_template('upload.html')


# ──────────────────────────────────────────────────────────
# Extracted Text Review Route
# ──────────────────────────────────────────────────────────
@app.route('/extracted/<int:resume_id>')
def extracted(resume_id):
    """
    Module 4 – Extracted Text Review
    Shows the raw text extracted from the uploaded resume along with a
    quick preview of parsed fields (name, email, phone, skills).
    The user can then proceed to analysis or re-upload.
    """
    resume = fetch_resume(resume_id)
    if not resume:
        return render_template(
            'error.html',
            error_title="Resume Not Found",
            error_message="The resume record could not be found. Please upload your resume again to analyze."
        )

    return render_template(
        'extracted.html',
        resume_id=resume_id,
        filename=resume['filename'],
        text=resume['raw_text'],
        parsed_data=resume['parsed_data']
    )


@app.route('/analyze', methods=['POST'])
@app.route('/analyze/<int:resume_id>', methods=['GET', 'POST'])
def analyze(resume_id=None):
    """
    Module 6 & JSON API – Job Description Input & Hybrid ATS Analysis
    Supports:
    1. Direct JSON API request: POST /analyze with body {"resume_text": "...", "job_description": "..."}
    2. HTML Form submit: POST /analyze/<resume_id> with job_description form field.
    """
    # 1. API Stateless JSON analysis
    if request.is_json or (request.method == 'POST' and not request.form and request.data):
        try:
            data = request.get_json(silent=True) or {}
            resume_text = data.get('resume_text', '').strip()
            job_description = data.get('job_description', '').strip()

            # Allow lookup by resume_id if raw text not provided
            if not resume_text and data.get('resume_id'):
                r = get_resume(data.get('resume_id'))
                if r:
                    resume_text = r['raw_text']

            if not resume_text:
                return jsonify({
                    'error': 'Missing required field: "resume_text" (or a valid "resume_id").'
                }), 400

            if not job_description:
                return jsonify({
                    'error': 'Missing required field: "job_description".'
                }), 400

            # Parse resume sections (best-effort; fall back gracefully)
            try:
                parsed = parse_resume(resume_text)
            except Exception:
                parsed = {'skills': []}

            # Run hybrid NLP + TF-IDF analysis
            job_match = analyze_job_match(resume_text, parsed.get('skills', []), job_description)

            # Compute ATS score using the hybrid formula:
            #   ATS = round( (keyword_match_percent * 0.7) + (tfidf_similarity * 0.3) )
            ats_result = calculate_ats_score(parsed, resume_text, job_match)

            # Build plain-string suggestions for the API (no icon/priority metadata)
            plain_suggestions = get_plain_suggestions(parsed, ats_result, job_match)

            # Build a transparent breakdown so callers can see every component
            breakdown = ats_result.get('breakdown', {})
            transparent_breakdown = {
                'formula': breakdown.get('formula', ''),
                'keyword_weight': breakdown.get('keyword_weight', 0.7),
                'similarity_weight': breakdown.get('similarity_weight', 0.3),
                'weighted_keyword_match_percent': breakdown.get('weighted_keyword_match_percent',
                                                               job_match['match_percentage']),
                'similarity_score': breakdown.get('similarity_score',
                                                  job_match['similarity_score']),
                'section_scores': {
                    k: v for k, v in breakdown.items()
                    if isinstance(v, dict) and 'score' in v
                }
            }

            # Recommend actively hiring companies & internships based on candidate experience & skills
            job_recs = recommend_jobs(parsed.get('skills', []))
            hiring_info = recommend_hiring_companies(
                parsed.get('skills', []),
                ats_score=ats_result['total_score'],
                parsed_data=parsed,
                raw_text=resume_text,
                job_recommendations=job_recs
            )

            # Recommend resume-boosting projects (Basic, Medium, High complexity)
            project_recs = recommend_projects(
                parsed.get('skills', []),
                missing_skills=job_match.get('missing_skills', [])
            )

            return jsonify({
                'ats_score': ats_result['total_score'],
                'matched_keywords': job_match['matched_skills'],
                'missing_keywords': job_match['missing_skills'],
                'keyword_match_percent': job_match['match_percentage'],
                'similarity_score': job_match['similarity_score'],
                'suggestions': plain_suggestions,
                'breakdown': transparent_breakdown,
                'hiring_companies': hiring_info['companies'],
                'candidate_profile': hiring_info['experience_level'],
                'project_recommendations': project_recs
            }), 200

        except Exception as e:
            return jsonify({'error': f"Server analysis failure: {str(e)}"}), 500

    # 2. HTML Web Form analysis route (/analyze/<int:resume_id>)
    if not resume_id:
        return jsonify({'error': 'Resume ID or resume_text required for analysis.'}), 400

    resume = fetch_resume(resume_id)
    if not resume:
        return render_template(
            'error.html', 
            error_title="Resume Not Found", 
            error_message="The resume record could not be found. Please upload your resume again to analyze."
        )
        
    if request.method == 'POST':
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            flash('Please paste a job description or click skip for general analysis.', 'warning')
            return redirect(request.url)
            
        try:
            job_match = analyze_job_match(
                resume['raw_text'], 
                resume['parsed_data'].get('skills', []), 
                job_description
            )
            
            ats_result = calculate_ats_score(
                resume['parsed_data'], 
                resume['raw_text'], 
                job_match
            )
            
            suggestions = generate_suggestions(
                resume['parsed_data'], 
                ats_result, 
                job_match
            )
            
            job_recommendations = recommend_jobs(resume['parsed_data'].get('skills', []))
            missing_skills = job_match.get('missing_skills', [])
            course_recommendations = recommend_courses(missing_skills)
            
            save_analysis(
                resume_id=resume_id,
                ats_score=ats_result['total_score'],
                score_breakdown=ats_result['breakdown'],
                matched_skills=job_match['matched_skills'],
                missing_skills=job_match['missing_skills'],
                match_percentage=job_match['match_percentage'],
                suggestions=suggestions,
                job_recommendations=job_recommendations,
                course_recommendations=course_recommendations,
                job_description=job_description
            )
            
            flash('Resume compared against job description successfully!', 'success')
            return redirect(url_for('dashboard', resume_id=resume_id))
            
        except Exception as e:
            flash(f"Error during job analysis: {str(e)}", 'danger')
            return redirect(request.url)
            
    return render_template('analyze.html', resume_id=resume_id)



@app.route('/dashboard/<int:resume_id>')
def dashboard(resume_id):
    """
    Module 11 – Responsive Dashboard
    Presents the full analysis results: ATS Score, parsed items, matched/missing skills, 
    career recommendations, and improvement tips.
    If no prior job description analysis was saved, performs a general (non-JD) analysis.
    """
    resume = fetch_resume(resume_id)
    if not resume:
        return render_template(
            'error.html', 
            error_title="Resume Not Found", 
            error_message="The resume record could not be found. Please upload your resume again to view results."
        )
        
    # Check if there is already an analysis saved for this resume
    analysis = get_analysis_by_resume(resume_id)
    
    # If no analysis exists, run a default General Analysis
    if not analysis:
        try:
            # General analysis doesn't have a job match
            ats_result = calculate_ats_score(resume['parsed_data'], resume['raw_text'])
            suggestions = generate_suggestions(resume['parsed_data'], ats_result)
            job_recommendations = recommend_jobs(resume['parsed_data'].get('skills', []))
            
            # Suggest general courses based on current skills gaps
            course_recommendations = recommend_general_courses(resume['parsed_data'].get('skills', []))
            
            # Save general analysis
            save_analysis(
                resume_id=resume_id,
                ats_score=ats_result['total_score'],
                score_breakdown=ats_result['breakdown'],
                matched_skills=[],
                missing_skills=[],
                match_percentage=0.0,
                suggestions=suggestions,
                job_recommendations=job_recommendations,
                course_recommendations=course_recommendations,
                job_description="General Analysis (No Job Description provided)"
            )
            # Fetch the newly saved general analysis
            analysis = get_analysis_by_resume(resume_id)
            
        except Exception as e:
            return render_template(
                'error.html', 
                error_title="Analysis Error", 
                error_message=f"Failed to generate general analysis: {str(e)}"
            )

    # Prepare data for dashboard template
    # Re-structure matched/missing lists for easy presentation
    job_match = None
    if analysis['job_description'] != "General Analysis (No Job Description provided)":
        job_match = {
            'matched_skills': analysis['matched_skills'],
            'missing_skills': analysis['missing_skills'],
            'match_percentage': analysis['match_percentage']
        }
        
    # Recommend active hiring companies and internships (Startups, Tech Giants, Remote/WFH, Office)
    hiring_info = recommend_hiring_companies(
        resume['parsed_data'].get('skills', []),
        ats_score=analysis['ats_score'],
        parsed_data=resume['parsed_data'],
        raw_text=resume.get('raw_text', ''),
        job_recommendations=analysis['job_recommendations']
    )

    # Recommend 3-tier projects to boost resume value (Basic, Medium, High)
    missing_skills_list = job_match.get('missing_skills', []) if job_match else []
    project_recs = recommend_projects(
        resume['parsed_data'].get('skills', []),
        missing_skills=missing_skills_list
    )

    # Generate mock interview questions based on candidate skills & missing skill gaps
    interview_questions = generate_mock_interview(
        resume['parsed_data'].get('skills', []),
        missing_skills=missing_skills_list
    )

    return render_template(
        'dashboard.html',
        resume_id=resume_id,
        parsed_data=resume['parsed_data'],
        ats_result={
            'total_score': analysis['ats_score'],
            'breakdown': analysis['score_breakdown']
        },
        job_match=job_match,
        suggestions=analysis['suggestions'],
        job_recommendations=analysis['job_recommendations'],
        course_recommendations=analysis['course_recommendations'],
        hiring_info=hiring_info,
        hiring_companies=hiring_info['companies'],
        project_recommendations=project_recs,
        interview_questions=interview_questions
    )


@app.route('/download-report/<int:resume_id>')
def download_report(resume_id):
    """
    Module 12 – Downloadable PDF Report
    Requires user authentication (Log In or Sign Up) before allowing free PDF report downloads.
    """
    if not session.get('user_id'):
        flash('Please Log In or Sign Up to download your free ATS report.', 'warning')
        return redirect(url_for('login'))

    resume = fetch_resume(resume_id)
    analysis = get_analysis_by_resume(resume_id)
    
    if not resume or not analysis:
        return render_template(
            'error.html', 
            error_title="Report Generation Failed", 
            error_message="Could not find resume or analysis records required to construct the PDF."
        )
        
    try:
        # Re-structure job match structure if applicable
        job_match = None
        if analysis['job_description'] != "General Analysis (No Job Description provided)":
            job_match = {
                'matched_skills': analysis['matched_skills'],
                'missing_skills': analysis['missing_skills'],
                'match_percentage': analysis['match_percentage']
            }
            
        # Call the report generator
        filepath, filename = generate_report(
            parsed_data=resume['parsed_data'],
            ats_result={
                'total_score': analysis['ats_score'],
                'breakdown': analysis['score_breakdown']
            },
            suggestions=analysis['suggestions'],
            job_recommendations=analysis['job_recommendations'],
            course_recommendations=analysis['course_recommendations'],
            job_match=job_match
        )

        # Send PDF file from dynamic report folder
        return send_from_directory(
            os.path.dirname(filepath),
            filename,
            as_attachment=True
        )

    except Exception as e:
        # Bug 4 fix: log the error, clean up any partial file, return specific message
        import logging
        logging.exception("Report generation failed for resume_id=%s", resume_id)
        # Clean up temp file if partially written
        try:
            if 'filepath' in dir() and filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            pass
        error_msg = str(e)
        if 'fpdf' in error_msg.lower() or 'FPDF' in error_msg:
            friendly = "PDF library error. Please try again or contact support."
        elif 'UnicodeEncode' in error_msg or 'latin-1' in error_msg:
            friendly = "Your resume contains unsupported characters. The PDF could not be generated."
        else:
            friendly = f"An error occurred while compiling your PDF document: {error_msg}"
        return render_template(
            'error.html',
            error_title="Report Generation Error",
            error_message=friendly
        )


@app.route('/history')
def history():
    """
    Analysis History Route
    Requires user login. Displays only the authenticated user's private history.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('Please Log In or Sign Up to view your private analysis history.', 'warning')
        return redirect(url_for('login'))

    try:
        db_history = get_all_analyses(user_id=user_id)

        # Clean formatting on dates for display
        # Bug 6 fix: handle both SQLite ('2024-07-26 15:32:15') and PostgreSQL
        # ('2024-07-26 15:32:15.123456') timestamp formats
        for item in db_history:
            if 'analysis_date' in item and item['analysis_date']:
                try:
                    raw = str(item['analysis_date'])
                    # Strip microseconds and timezone suffix if present
                    raw = raw.split('.')[0].split('+')[0].strip()
                    dt = datetime.strptime(raw, '%Y-%m-%d %H:%M:%S')
                    item['analysis_date'] = dt.strftime('%B %d, %Y, %I:%M %p')
                except Exception:
                    pass  # Keep original string if parsing fails
    except Exception as e:
        flash(f"Failed to load history: {str(e)}", 'danger')
        db_history = []
        
    return render_template('history.html', history=db_history)


# ──────────────────────────────────────────────────────────
# AI Enhancements & Tool Endpoints
# ──────────────────────────────────────────────────────────

@app.route('/api/enhance-bullet', methods=['POST'])
@csrf.exempt
def api_enhance_bullet():
    """AI Bullet Point Enhancer Endpoint."""
    data = request.get_json(silent=True) or {}
    bullet_text = data.get('bullet_text', '')
    enhanced = enhance_bullet_point(bullet_text)
    return jsonify(enhanced), 200


@app.route('/api/fetch-job-url', methods=['POST'])
@csrf.exempt
def api_fetch_job_url():
    """Job Description URL Scraper Endpoint."""
    data = request.get_json(silent=True) or {}
    job_url = data.get('job_url', '')
    res = extract_job_from_url(job_url)
    return jsonify(res), 200 if res['status'] == 'success' else 400


@app.route('/cover-letter/<int:resume_id>')
def cover_letter(resume_id):
    """AI Cover Letter Generator Route."""
    # Bug 8 fix: require authentication before generating cover letters
    if not session.get('user_id'):
        flash('Please Log In or Sign Up to generate a cover letter.', 'warning')
        return redirect(url_for('login'))

    # Bug 1 fix: use fetch_resume() for cold-start / ephemeral DB resilience
    resume = fetch_resume(resume_id)
    analysis = get_analysis_by_resume(resume_id)

    if not resume:
        return render_template(
            'error.html',
            error_title="Resume Not Found",
            error_message="Could not find resume record for cover letter generation."
        )

    candidate_name = resume['parsed_data'].get('name', 'Candidate')
    candidate_skills = resume['parsed_data'].get('skills', [])
    job_title = "Software Engineer"
    company_name = "Target Hiring Company"

    cl_data = generate_cover_letter(
        candidate_name=candidate_name,
        candidate_skills=candidate_skills,
        job_title=job_title,
        company_name=company_name
    )

    return render_template(
        'cover_letter.html',
        resume_id=resume_id,
        cover_letter=cl_data,
        candidate_name=candidate_name
    )


# ──────────────────────────────────────────────────────────
# User Authentication Routes (Sign Up, Log In, Log Out)
# ──────────────────────────────────────────────────────────

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    """
    User Registration Route
    Supports signing up with Full Name, Email or Phone Number, and Password.
    """
    if session.get('user_id'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not identifier or not password:
            flash('All fields are required.', 'danger')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter your password.', 'danger')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('signup.html')

        existing = get_user_by_identifier(identifier)
        if existing:
            flash('An account with this Email or Phone Number already exists. Please Log In.', 'warning')
            return redirect(url_for('login'))

        password_hash = generate_password_hash(password)
        user_id = create_user(full_name, identifier, password_hash)

        if user_id:
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['user_identifier'] = identifier
            flash(f"Welcome, {full_name}! Your account was created successfully.", 'success')
            return redirect(url_for('upload'))
        else:
            flash('Failed to create account. Please try again.', 'danger')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """
    User Login Route
    Authenticates user via Email or Phone Number + Password.
    """
    if session.get('user_id'):
        return redirect(url_for('home'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Please provide your Email or Phone Number and Password.', 'danger')
            return render_template('login.html')

        user = get_user_by_identifier(identifier)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_identifier'] = user['identifier']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid Email/Phone Number or Password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Log Out Route
    Clears active user session.
    """
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


# ──────────────────────────────────────────────────────────
# Run Local Server
# ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Make sure local uploads directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run server locally on http://localhost:5000 in debug mode
    # Debug mode reloads code automatically on edits and prints tracebacks.
    app.run(debug=True, port=5000)
