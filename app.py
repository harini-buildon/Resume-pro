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
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from config import SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from database.db import (
    init_db, save_resume, get_resume, save_analysis, 
    get_analysis_by_resume, get_all_analyses
)
from utils.file_handler import save_uploaded_file, get_file_extension
from utils.text_extractor import extract_text
from utils.resume_parser import parse_resume
from utils.job_analyzer import analyze_job_match
from utils.ats_scorer import calculate_ats_score
from utils.suggestions import generate_suggestions
from utils.job_recommender import recommend_jobs
from utils.course_recommender import recommend_courses, recommend_general_courses
from utils.report_generator import generate_report

# Initialize the Flask App
app = Flask(__name__)

# Apply configuration settings
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize the SQLite Database when the app starts
init_db()


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
    return render_template(
        'error.html', 
        error_title="File Too Large", 
        error_message="The uploaded file exceeds the maximum allowed size of 16 MB. Please compress your file or upload a text-only version."
    ), 413


@app.errorhandler(404)
def page_not_found(error):
    """Handle non-existent URLs (404 Page Not Found)."""
    return render_template(
        'error.html', 
        error_title="Page Not Found", 
        error_message="The page you are looking for does not exist or has been moved."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal python crashes gracefully."""
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
    """
    Module 1 – Home Page
    Renders the professional landing page.
    """
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Module 2 & 3 – Resume Upload & Extraction
    GET:  Display the file upload form.
    POST: Receive the uploaded file, validate it, save it, 
          extract text, parse structured data, save to DB, and redirect.
    """
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No file part in the request.', 'danger')
            return redirect(request.url)
            
        file = request.files['resume']
        
        # Validate and save file securely
        success, result = save_uploaded_file(file)
        
        if not success:
            flash(result, 'danger')  # Result is the error message
            return redirect(request.url)
        
        filepath = result  # On success, result is the absolute filepath
        filename = file.filename
        
        # Step 3: Extract text from the saved file
        text_success, text_result = extract_text(filepath)
        
        if not text_success:
            flash(text_result, 'danger')
            # Clean up uploaded file if extraction failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(request.url)
        
        raw_text = text_result
        
        # Step 4: Parse basic resume content (Name, Email, Skills, etc.)
        try:
            parsed_data = parse_resume(raw_text)
        except Exception as e:
            flash(f"Error parsing resume structure: {str(e)}", 'warning')
            parsed_data = {}
            
        # Step 5: Save resume & raw text & parsed structure in SQLite
        try:
            resume_id = save_resume(filename, filepath, raw_text, parsed_data)
            flash('Resume uploaded and text extracted successfully!', 'success')
            # Redirect to the extracted text review page
            return redirect(url_for('extracted', resume_id=resume_id))
        except Exception as e:
            flash(f"Database error while saving resume: {str(e)}", 'danger')
            return redirect(request.url)
            
    # GET Request: Renders the upload form
    return render_template('upload.html')


@app.route('/extracted/<int:resume_id>')
def extracted(resume_id):
    """
    Module 3 – Text Extraction Display
    Loads the resume from the database and shows the raw text.
    Allows the candidate to preview how the parser read their layout.
    """
    resume = get_resume(resume_id)
    if not resume:
        return render_template(
            'error.html', 
            error_title="Resume Not Found", 
            error_message="The resume record could not be found in our database."
        )
        
    return render_template(
        'extracted.html', 
        resume_id=resume_id,
        filename=resume['filename'],
        text=resume['raw_text'],
        parsed_data=resume['parsed_data']
    )


@app.route('/analyze/<int:resume_id>', methods=['GET', 'POST'])
def analyze(resume_id):
    """
    Module 6 – Job Description Input & Analysis
    GET:  Display job description input text box.
    POST: Compare resume against job description using TF-IDF & Cosine Similarity.
          Saves results into database and redirects to the dashboard.
    """
    resume = get_resume(resume_id)
    if not resume:
        return render_template(
            'error.html', 
            error_title="Resume Not Found", 
            error_message="The resume record could not be found."
        )
        
    if request.method == 'POST':
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            flash('Please paste a job description or click skip for general analysis.', 'warning')
            return redirect(request.url)
            
        try:
            # 1. Compare skills & calculate cosine similarity
            job_match = analyze_job_match(
                resume['raw_text'], 
                resume['parsed_data'].get('skills', []), 
                job_description
            )
            
            # 2. Calculate ATS Score with job match factors
            ats_result = calculate_ats_score(
                resume['parsed_data'], 
                resume['raw_text'], 
                job_match
            )
            
            # 3. Generate suggestions
            suggestions = generate_suggestions(
                resume['parsed_data'], 
                ats_result, 
                job_match
            )
            
            # 4. Job & course recommendations
            job_recommendations = recommend_jobs(resume['parsed_data'].get('skills', []))
            
            # Recommend course material based on missing JD skills
            missing_skills = job_match.get('missing_skills', [])
            course_recommendations = recommend_courses(missing_skills)
            
            # 5. Save analysis to SQLite database
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
            
    # GET Request: Renders the paste JD form
    return render_template('analyze.html', resume_id=resume_id)


@app.route('/dashboard/<int:resume_id>')
def dashboard(resume_id):
    """
    Module 11 – Responsive Dashboard
    Presents the full analysis results: ATS Score, parsed items, matched/missing skills, 
    career recommendations, and improvement tips.
    If no prior job description analysis was saved, performs a general (non-JD) analysis.
    """
    resume = get_resume(resume_id)
    if not resume:
        return render_template(
            'error.html', 
            error_title="Resume Not Found", 
            error_message="The resume record could not be found."
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
        course_recommendations=analysis['course_recommendations']
    )


@app.route('/download-report/<int:resume_id>')
def download_report(resume_id):
    """
    Module 12 – Downloadable PDF Report
    Uses the report generator utility to compile a professional PDF report on the fly 
    and sends it to the user's browser as an attachment.
    """
    resume = get_resume(resume_id)
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
        return render_template(
            'error.html', 
            error_title="Report Generation Error", 
            error_message=f"An error occurred while compiling your PDF document: {str(e)}"
        )


@app.route('/history')
def history():
    """
    Analysis History Route
    Loads all previous resume records and analysis results to let the user review
    past projects and download old reports.
    """
    try:
        db_history = get_all_analyses()
        
        # Clean formatting on dates for display
        for item in db_history:
            if 'analysis_date' in item:
                # Format SQL date string: '2026-07-15 11:20:00' -> 'July 15, 2026, 11:20 AM'
                try:
                    dt = datetime.strptime(item['analysis_date'], '%Y-%m-%d %H:%M:%S')
                    item['analysis_date'] = dt.strftime('%B %d, %Y, %I:%M %p')
                except Exception:
                    pass
    except Exception as e:
        flash(f"Failed to load history: {str(e)}", 'danger')
        db_history = []
        
    return render_template('history.html', history=db_history)


# ──────────────────────────────────────────────────────────
# Run Local Server
# ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Make sure local uploads directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run server locally on http://localhost:5000 in debug mode
    # Debug mode reloads code automatically on edits and prints tracebacks.
    app.run(debug=True, port=5000)
