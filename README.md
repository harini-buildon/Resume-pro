# 🚀 Pro Resume Analyzer – AI-Powered ATS & Career Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)](https://spacy.io)
[![Vercel Live Demo](https://img.shields.io/badge/Vercel-Live%20Application-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://resume-pro-woad-chi.vercel.app/)
[![Localhost](https://img.shields.io/badge/Localhost-http%3A%2F%2F127.0.0.1%3A5000-success?style=for-the-badge&logo=gunicorn&logoColor=white)](http://127.0.0.1:5000)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An enterprise-grade, AI-driven career optimization platform built with **Python**, **Flask**, **spaCy NLP**, **Scikit-learn**, **SQLite**, **PostgreSQL**, **Redis**, and an interactive **3D Glassmorphism UI**.

---

## 🌐 Application Deployment Links

| Deployment | URL / Access | Status |
|---|---|---|
| ⚡ **Live Vercel Application** | **[https://resume-pro-woad-chi.vercel.app/](https://resume-pro-woad-chi.vercel.app/)** | **Active (Serverless)** |
| 💻 **Live Local Host Server** | **[http://127.0.0.1:5000](http://127.0.0.1:5000)** | **Active (Gunicorn / Flask)** |

### 🛡️ Key Features & Protections Active
- **3D Dashboard**: Mouse-tilt cards, holographic gradient header, dead-centered ATS score gauge with radial glass aura.
- **Hybrid ATS Matching**: 50% Resume Structure + 50% Job Description Skill Overlap & TF-IDF Similarity.
- **PDF Report Generator**: FPDF2 margin resets & safe layout calculations.
- **Security**: `.env` credential isolation, `.gitignore`, MIME magic-bytes upload validation, SSRF URL protection.
- **Production Infrastructure**: Gunicorn WSGI multi-worker config (`Procfile`), Redis rate-limit support, DB connection pooling.

---

## 🌟 Key Features

### 1. 🎨 Interactive 3D Visual Dashboard
- **3D Card Mouse Tilt**: Interactive perspective tilt (`rotateX/Y` up to 10 deg) tracking mouse movements with real-time shadow physics.
- **Dead-Centered Neon ATS Ring**: Dynamic SVG progress ring with 3D radial glass backdrop disc (`.score-glass-backdrop`) and score-based gradients (Green >= 70, Amber 50-69, Red < 50).
- **Holographic Header**: Deep blue-to-indigo hero header with animated shimmer sweeps and flexbox spacing.

### 2. ⚡ Hybrid ATS Scoring Engine
- **General Analysis Mode**: Evaluates 8 core structural sections out of 100 points (Contact Info, Technical Skills, Education, Experience, Projects, Certifications, Formatting, Keyword Variety).
- **Targeted Job Description Match Mode**: Blends **50% Resume Structural Completeness + 50% Job Description Relevance**:
  - JD Relevance Score = (Weighted Skill Match % * 0.7) + (TF-IDF Cosine Similarity % * 0.3)
- Displays live target JD match statistics directly on the dashboard card (`Target JD Match: XX% (X matched, Y missing)`).

### 3. 🔑 Flexible Authentication & Session Security
- Register and log in using **either Email Address or Mobile Phone Number**.
- Secure PBKDF2/SHA256 password hashing.
- `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SECURE = True`, and `SESSION_COOKIE_SAMESITE = 'Lax'` for cookie protection.

### 4. 💼 Experience-Tailored Hiring Recommendations
- Automatically detects **Fresher / Student** (recommends **Internships**) vs. **Experienced Engineer** (**Full-Time Roles**).
- Recommends Y-Combinator startups & unicorns (Vercel, Supabase, Postman, Razorpay, Hasura) alongside Tech Giants (Google, Amazon, Microsoft, Meta, Stripe).
- Filters work mode for **Work From Home (Remote)** vs **In-Office / Hybrid**.

### 5. 🚀 3-Tier Career Project Ideas & STAR Interview Prep
- 🟢 **Basic (Foundation)**: Core domain skills.
- 🟡 **Medium (Full-Stack & APIs)**: REST API services, DB integration, async tasks.
- 🔴 **High (Production Architecture)**: Enterprise cloud pipelines, Kafka queues, Kubernetes, or RAG LLM services.
- **STAR Method AI Mock Interview Prep**: Behavioral and technical questions with answer frameworks.

### 6. 🤖 AI Tool Suite & Secure File Parsing
- **AI Bullet Point Enhancer**: Transforms weak bullet points into quantifiable metric-driven accomplishments.
- **AI Cover Letter Generator**: Generates customized cover letters with 1-click clipboard copying.
- **PDF Report Generator**: Compiles downloadable PDF reports using FPDF2 with margin safety and ASCII character sanitization.
- **Magic Bytes Validation**: Inspects binary signatures (`%PDF`, `PK`) to block disguised executable uploads.
- **SSRF Protection**: Prevents URL job scraper from probing private/internal IP ranges (`127.0.0.1`, `10.x.x.x`, `192.168.x.x`).

---

## 📁 Repository Structure

```
resume-analyzer/
├── app.py                    # Flask server, routing, rate limiting & error handlers
├── config.py                 # Configuration settings (SECRET_KEY, Vercel /tmp detection)
├── Procfile                  # Production Gunicorn WSGI startup configuration
├── vercel.json               # Vercel deployment settings (maxDuration: 60)
├── database/
│   └── db.py                 # SQLite & PostgreSQL ThreadedConnectionPool implementation
├── models/
│   └── resume.py             # Data schemas and structures
├── static/
│   ├── css/
│   │   ├── style.css         # Core CSS tokens & global styles
│   │   └── dashboard-3d.css  # 3D Glassmorphism & neon dashboard styles
│   ├── js/
│   │   ├── main.js           # Base JavaScript interactive logic
│   │   └── dashboard-3d.js   # 3D Mouse-tilt physics & counter animations
│   └── reports/              # Local PDF report storage directory
├── templates/
│   ├── base.html             # Common layout template with dark mode support
│   ├── index.html            # 3D Landing page
│   ├── upload.html           # File upload page
│   ├── analyze.html          # Job Description analysis & URL scraper
│   ├── dashboard.html        # 3D Candidate analysis dashboard & AI widgets
│   ├── cover_letter.html     # AI Cover Letter view
│   ├── signup.html           # User registration (Email/Phone)
│   ├── login.html            # User login page
│   ├── history.html          # Analysis history
│   └── error.html            # Friendly error handling page
├── utils/
│   ├── ats_scorer.py         # Hybrid ATS scoring algorithm
│   ├── nlp_processor.py      # spaCy NLP keyword extraction & synonym mapping
│   ├── company_recommender.py# Hiring company & internship recommendation engine
│   ├── project_recommender.py# 3-Tier project recommendation engine
│   ├── bullet_enhancer.py    # AI Bullet point quantifier
│   ├── cover_letter.py       # AI Cover Letter generator
│   ├── job_scraper.py        # Job posting URL scraper with SSRF protection
│   ├── interview_generator.py# STAR mock interview prep generator
│   ├── file_handler.py       # Upload validation & magic bytes MIME check
│   ├── text_extractor.py     # PDF & DOCX text extraction
│   ├── resume_parser.py      # Heuristic resume parser
│   └── report_generator.py   # PDF report generator with margin safety
└── tests/
    ├── test_ats.py           # ATS scoring unit tests
    ├── test_auth.py          # Authentication unit tests
    ├── test_company_recommender.py # Company recommender unit tests
    ├── test_project_recommender.py # Project recommender unit tests
    └── test_enhancements.py  # Enhancement modules unit tests
```

---

## 🔑 Environment Variables Setup

Copy `.env.example` to `.env`:

```env
# Flask Secret Key
SECRET_KEY=your_secure_secret_key_here

# Gemini AI API Key (Optional: for AI features)
GEMINI_API_KEY=your_gemini_api_key_here

# PostgreSQL Database URL (Optional: defaults to local SQLite if empty)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis URL for multi-worker rate limiting (Optional)
REDIS_URL=redis://localhost:6379/0
```

---

## 🛠️ Local Server Setup & Running

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/harini-buildon/Resume-pro.git
   cd Resume-pro
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies & spaCy Model**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Run Development Server**:
   ```bash
   python app.py
   ```

5. **Run Production Server (Gunicorn)**:
   ```bash
   gunicorn -w 4 --timeout 120 --bind 0.0.0.0:5000 app:app
   ```

6. **Access Application**:
   Open browser at **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## ☁️ Vercel Deployment Architecture

The application is fully pre-configured for seamless Vercel serverless deployment:

- **Ephemeral Storage**: Detects `VERCEL` environment and routes database and file uploads to `/tmp` writable storage (`/tmp/uploads`, `/tmp/reports`, `/tmp/database`).
- **Database Persistence**: Set `DATABASE_URL` in Vercel project environment variables to connect to PostgreSQL (Supabase, Neon, or Railway).
- **Execution Timeout**: Configured `maxDuration: 60` in `vercel.json` to allow full AI generation and PDF compilation on serverless functions.

---

## 🧪 Unit Test Suite — 34 / 34 Passed ✅

Run the automated test suite:

```bash
python -m pytest tests/ -v
```

Output:
```bash
======================== 34 passed in 4.62s ========================
```

---

## 📄 License
© 2026 Pro Resume Analyzer. All Rights Reserved. Released under the MIT License.

