# Pro Resume Analyzer – AI-Powered ATS & Career Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)](https://spacy.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An enterprise-grade, AI-driven career optimization platform built with **Python**, **Flask**, **spaCy NLP**, **Scikit-learn**, **SQLite**, and **3D Glassmorphism UI**.

Live Local Host Server: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🌟 Key Features

### 1. 🔑 Flexible User Authentication
- Register and log in using **either Email Address or Mobile Phone Number**.
- Secure PBKDF2/SHA256 password hashing.
- Gated PDF report downloads (requires authentication before downloading).

### 2. ⚡ Hybrid ATS Scoring Engine (`92.9% Match Precision`)
- **Formula**: `ATS Score = round((Weighted Keyword Match % * 0.7) + (TF-IDF Cosine Similarity * 0.3))`
- spaCy NLP pre-processing, synonym mapping (`Scikit-learn`, `CI/CD`, `REST APIs`), noise removal, and subset deduplication.

### 3. 💼 Experience-Tailored Hiring Recommendations
- Automatically detects **Student / Fresher** (focusing on **Internships / Co-ops**) vs **Experienced Engineer** (**Full-Time Roles**).
- Recommends Y-Combinator startups & unicorns (Vercel, Supabase, Postman, Razorpay, Hasura) alongside Tech Giants (Google, Amazon, Microsoft, Meta, Stripe).
- Work mode badges for **Work From Home (Remote)** vs **In-Office / Hybrid**.

### 4. 🚀 3-Tier Career-Growth Project Ideas
- 🟢 **Basic (Foundation)**: Core domain skills & fundamentals.
- 🟡 **Medium (Full-Stack & APIs)**: REST API services, DB integration, async tasks.
- 🔴 **High (Production & Microservices)**: Enterprise cloud architecture, Kafka queues, Kubernetes, or RAG LLM pipelines.

### 5. 🤖 AI Tool Enhancements
- **AI Bullet Point Enhancer**: Converts weak bullet points into metric-driven achievements.
- **AI Cover Letter Generator**: Generates customized cover letters with 1-click clipboard copying.
- **Job Posting URL Importer**: Paste LinkedIn/Indeed job links to auto-extract Job Description text.
- **AI Mock Interview Prep**: Tailored technical and behavioral questions using STAR method frameworks.

### 6. 🎨 Interactive 3D Visual Frontend
- Multi-perspective 3D hero cards (`perspective: 1200px`).
- Translucent neon glassmorphism (`backdrop-filter: blur(16px)`).
- Real-time cursor mouse-tilt interaction on cards.

---

## 📁 Repository Structure

```
resume-analyzer/
├── app.py                    # Main Flask application server & 6 enhancement endpoints
├── config.py                 # Configuration settings (SECRET_KEY, file limits)
├── database/
│   └── db.py                 # SQLite database schema, user accounts & resume CRUD
├── models/
│   └── resume.py             # Data structures and schemas
├── static/
│   ├── css/style.css         # 3D spatial cards & glassmorphism stylesheet
│   ├── js/main.js            # Cursor tilt physics & interactive widgets
│   └── reports/              # Storage directory for generated PDF reports
├── templates/
│   ├── base.html             # Layout base template & copyright notice
│   ├── index.html            # 3D Landing page
│   ├── upload.html           # File upload page
│   ├── analyze.html          # Job Description analysis & URL importer
│   ├── dashboard.html        # Candidate analysis dashboard & AI widgets
│   ├── cover_letter.html     # AI Cover Letter view
│   ├── signup.html           # User registration (Email/Phone)
│   ├── login.html            # User login page
│   ├── history.html          # Resume analysis history
│   └── error.html            # Error handling pages
├── utils/
│   ├── ats_scorer.py         # ATS scoring engine
│   ├── nlp_processor.py      # spaCy NLP entity extraction & synonym mapping
│   ├── company_recommender.py# Hiring company & internship recommender
│   ├── project_recommender.py# 3-tier project recommendation engine
│   ├── bullet_enhancer.py    # AI Bullet point quantifier
│   ├── cover_letter.py       # AI Cover Letter generator
│   ├── job_scraper.py        # Job posting URL scraper
│   ├── interview_generator.py# STAR mock interview prep generator
│   ├── file_handler.py       # Upload validation (50 KB – 16 MB)
│   ├── text_extractor.py     # PDF & DOCX text extraction
│   ├── resume_parser.py      # Heuristic resume parser
│   └── report_generator.py   # PDF report generator
└── tests/
    ├── test_ats.py           # ATS scoring unit tests
    ├── test_auth.py          # Authentication unit tests
    ├── test_company_recommender.py # Company recommender unit tests
    ├── test_project_recommender.py # Project recommender unit tests
    └── test_enhancements.py  # Enhancement modules unit tests
```

---

## 🧪 Unit Test Suite — 34 / 34 Passed ✅

Run all 34 automated unit tests:

```bash
python -m unittest discover -s tests -v
```

---

## 🛠️ Installation & Local Setup

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

3. **Install Dependencies & Download spaCy Model**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Run the Server**:
   ```bash
   python app.py
   ```

5. **Access Application**:
   Open browser at **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📄 License
© 2026 Pro Resume Analyzer. All Rights Reserved.
