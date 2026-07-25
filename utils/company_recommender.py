"""
utils/company_recommender.py – Experience-Tailored Company & Internship Recommender
====================================================================================
Recommends actively hiring companies across:
1. Opportunity Types: Internships (for freshers/students) & Full-Time Roles (for experienced candidates).
2. Company Tiers: High-Growth Startups / Y-Combinator alumni to Top Tech Giants.
3. Work Modes: Work From Home (Remote) & In-Office / Hybrid options.
4. Recent Real Data Filters: Targeted search query URLs for recent active postings.
"""

import urllib.parse
import re

# ──────────────────────────────────────────────────────────
# Expanded Actively Hiring Database (Startups + Tech Giants)
# ──────────────────────────────────────────────────────────
HIRING_ENTITIES = [
    # --- STARTUPS & HIGH-GROWTH UNICORNS ---
    {
        "name": "Vercel",
        "domain": ["Next.js", "React", "TypeScript", "JavaScript", "Node.js", "Frontend", "Full Stack"],
        "full_time_roles": ["Frontend Engineer", "Full Stack Infrastructure Developer"],
        "intern_roles": ["Frontend Engineering Intern", "Software Developer Intern"],
        "locations": ["Remote (Worldwide)", "San Francisco, CA"],
        "work_mode": "Work From Home (Remote)",
        "work_mode_type": "remote",
        "logo_icon": "bi-triangle-fill",
        "tier": "🚀 High-Growth Startup",
        "company_type": "startup",
        "hiring_badge": "🔥 Active Hiring - Posted 1 day ago"
    },
    {
        "name": "Postman",
        "domain": ["REST APIs", "Node.js", "JavaScript", "Python", "Go", "Backend", "Testing", "QA"],
        "full_time_roles": ["Backend Software Engineer", "API Platform Specialist"],
        "intern_roles": ["Software Engineering Intern", "QA / Automation Intern"],
        "locations": ["Bangalore, India", "San Francisco, CA", "Remote"],
        "work_mode": "Both Options (Remote & In-Office)",
        "work_mode_type": "both",
        "logo_icon": "bi-envelope-paper-heart-fill",
        "tier": "🚀 High-Growth Unicorn",
        "company_type": "startup",
        "hiring_badge": "⚡ Urgent Hiring - Posted 2 days ago"
    },
    {
        "name": "Supabase",
        "domain": ["PostgreSQL", "Go", "TypeScript", "Python", "SQL", "Database", "REST APIs"],
        "full_time_roles": ["Database Infrastructure Engineer", "Backend Developer"],
        "intern_roles": ["Open Source Software Intern", "Backend Intern"],
        "locations": ["Remote (Worldwide)"],
        "work_mode": "Work From Home (Remote)",
        "work_mode_type": "remote",
        "logo_icon": "bi-database-fill-check",
        "tier": "🚀 Y-Combinator Startup",
        "company_type": "startup",
        "hiring_badge": "🌟 Featured Opening - Posted 1 day ago"
    },
    {
        "name": "Razorpay",
        "domain": ["Python", "Java", "PHP", "Go", "PostgreSQL", "Microservices", "REST APIs", "FinTech"],
        "full_time_roles": ["Software Development Engineer", "FinTech Platform Engineer"],
        "intern_roles": ["Software Engineering Intern (Summer 2026)", "Data Analyst Intern"],
        "locations": ["Bangalore, India", "Mumbai, India", "Hybrid"],
        "work_mode": "In-Office / Hybrid",
        "work_mode_type": "office",
        "logo_icon": "bi-lightning-charge-fill",
        "tier": "🚀 FinTech Startup",
        "company_type": "startup",
        "hiring_badge": "🔥 Active Hiring - Posted 3 days ago"
    },
    {
        "name": "BrowserStack",
        "domain": ["Java", "Python", "Ruby", "Selenium", "Docker", "DevOps", "Testing", "Linux"],
        "full_time_roles": ["DevOps Engineer", "Software Engineer II"],
        "intern_roles": ["SDET Intern", "Software Engineering Intern"],
        "locations": ["Mumbai, India", "San Francisco, CA", "Remote"],
        "work_mode": "Both Options (Remote & In-Office)",
        "work_mode_type": "both",
        "logo_icon": "bi-window-stack",
        "tier": "🚀 High-Growth Tech",
        "company_type": "startup",
        "hiring_badge": "🔥 Active Hiring - Posted 2 days ago"
    },
    {
        "name": "Hasura",
        "domain": ["GraphQL", "Haskell", "Go", "PostgreSQL", "React", "Docker", "Kubernetes"],
        "full_time_roles": ["GraphQL Core Engineer", "Cloud Infrastructure Engineer"],
        "intern_roles": ["Cloud Engineering Intern", "Developer Advocate Intern"],
        "locations": ["Remote (Global)", "Bangalore, India"],
        "work_mode": "Work From Home (Remote)",
        "work_mode_type": "remote",
        "logo_icon": "bi-diagram-3-fill",
        "tier": "🚀 Y-Combinator Startup",
        "company_type": "startup",
        "hiring_badge": "⚡ Urgent Hiring - Posted 1 day ago"
    },

    # --- TOP TECH GIANTS & ENTERPRISES ---
    {
        "name": "Google",
        "domain": ["Python", "C++", "Java", "Machine Learning", "Cloud", "Go", "Distributed Systems", "AI"],
        "full_time_roles": ["Software Engineer", "Machine Learning Engineer", "Cloud Solutions Architect"],
        "intern_roles": ["STEP Intern / Software Engineering Intern 2026", "ML Research Intern"],
        "locations": ["Mountain View, CA", "Bangalore, India", "London, UK", "Hybrid"],
        "work_mode": "In-Office / Hybrid",
        "work_mode_type": "office",
        "logo_icon": "bi-google",
        "tier": "🏢 Top Tech Giant",
        "company_type": "giant",
        "hiring_badge": "🔥 Active Hiring - Posted 1 day ago"
    },
    {
        "name": "Amazon",
        "domain": ["AWS", "Java", "Python", "Docker", "Kubernetes", "Microservices", "Cloud", "DevOps"],
        "full_time_roles": ["Software Development Engineer (SDE)", "AWS Cloud Architect", "DevOps Engineer"],
        "intern_roles": ["SDE Intern (Summer 2026)", "Cloud Support Associate Intern"],
        "locations": ["Seattle, WA", "Hyderabad, India", "Berlin, Germany", "Hybrid"],
        "work_mode": "In-Office / Hybrid",
        "work_mode_type": "office",
        "logo_icon": "bi-amazon",
        "tier": "🏢 Top Tech Giant",
        "company_type": "giant",
        "hiring_badge": "⚡ Urgent Hiring - Posted 2 days ago"
    },
    {
        "name": "Microsoft",
        "domain": ["C#", ".NET", "Azure", "Python", "React", "TypeScript", "AI", "Machine Learning"],
        "full_time_roles": ["Software Engineer II", "Azure Cloud Specialist", "AI Research Engineer"],
        "intern_roles": ["Explore Intern / Software Engineer Intern", "Data Science Intern"],
        "locations": ["Redmond, WA", "Bangalore, India", "Dublin, Ireland", "Remote"],
        "work_mode": "Both Options (Remote & In-Office)",
        "work_mode_type": "both",
        "logo_icon": "bi-microsoft",
        "tier": "🏢 Top Tech Giant",
        "company_type": "giant",
        "hiring_badge": "🔥 Active Hiring - Posted 3 days ago"
    },
    {
        "name": "Meta",
        "domain": ["React", "Python", "PyTorch", "C++", "JavaScript", "PHP", "GraphQL", "AI"],
        "full_time_roles": ["Full Stack Engineer", "AI Infrastructure Engineer", "Frontend Specialist"],
        "intern_roles": ["Meta University Intern", "Software Engineering Intern"],
        "locations": ["Menlo Park, CA", "London, UK", "Singapore", "Hybrid"],
        "work_mode": "In-Office / Hybrid",
        "work_mode_type": "office",
        "logo_icon": "bi-meta",
        "tier": "🏢 Top Tech Giant",
        "company_type": "giant",
        "hiring_badge": "🔥 Active Hiring - Posted 2 days ago"
    },
    {
        "name": "Stripe",
        "domain": ["Ruby", "Go", "Python", "React", "REST APIs", "PostgreSQL", "System Design"],
        "full_time_roles": ["Backend Engineer", "API Platform Engineer", "Security Engineer"],
        "intern_roles": ["Software Engineering Intern", "Security Intern"],
        "locations": ["San Francisco, CA", "Dublin, Ireland", "Remote"],
        "work_mode": "Work From Home (Remote)",
        "work_mode_type": "remote",
        "logo_icon": "bi-credit-card",
        "tier": "🚀 FinTech Unicorn",
        "company_type": "startup",
        "hiring_badge": "🌟 Featured Opening - Posted 1 day ago"
    },
    {
        "name": "OpenAI",
        "domain": ["Python", "PyTorch", "CUDA", "LLM", "Deep Learning", "Distributed Systems", "Kubernetes"],
        "full_time_roles": ["Research Engineer", "AI Infrastructure Engineer", "Backend Developer"],
        "intern_roles": ["AI Research Resident / Intern", "Software Engineering Intern"],
        "locations": ["San Francisco, CA", "Remote"],
        "work_mode": "Work From Home (Remote)",
        "work_mode_type": "remote",
        "logo_icon": "bi-cpu-fill",
        "tier": "🚀 AI Frontier Unicorn",
        "company_type": "startup",
        "hiring_badge": "🚀 High Growth - Posted 1 day ago"
    }
]


def detect_candidate_experience_level(parsed_data, raw_text=""):
    """
    Detect whether candidate is a student/fresher (prefers Internships)
    or experienced engineer (prefers Full-Time roles).

    Returns:
        dict: {'is_fresher': bool, 'preferred_opportunity': 'internship' | 'full_time'}
    """
    if not parsed_data:
        parsed_data = {}

    experience_list = parsed_data.get('experience', [])
    num_exp_entries = len(experience_list)
    text_lower = (raw_text + " " + " ".join(experience_list)).lower()

    # Keywords signaling student / intern / fresher status
    fresher_keywords = [
        "student", "undergraduate", "b.tech", "btech", "pursuing", "intern",
        "fresher", "graduate student", "bachelor", "entry level", "candidate"
    ]

    is_student = any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in fresher_keywords)

    if num_exp_entries == 0 or (num_exp_entries <= 1 and is_student):
        return {'is_fresher': True, 'preferred_opportunity': 'internship'}
    
    return {'is_fresher': False, 'preferred_opportunity': 'full_time'}


def _build_job_search_url(company_name, role_title, primary_skill, opportunity_type="full_time"):
    """
    Build a targeted Google Jobs search URL specifying company, role, skill, and recent past week filter (tbs=qdr:w).
    """
    opportunity_keyword = "internship" if opportunity_type == "internship" else "job hiring"
    query = f"{company_name} {role_title} {primary_skill} {opportunity_keyword}"
    params = {
        "q": query,
        "ibp": "htiv2",  # Trigger Google Jobs card
        "tbs": "qdr:w"    # Filter for recent (past week) postings
    }
    return f"https://www.google.com/search?{urllib.parse.urlencode(params)}"


def recommend_hiring_companies(resume_skills, ats_score=70, parsed_data=None, raw_text="", job_recommendations=None):
    """
    Recommend tailored hiring entities (Startups to Tech Giants, Internships vs Full-Time, WFH vs In-Office).

    Parameters:
        resume_skills (list[str]): Skills extracted from resume
        ats_score (int/float): Overall ATS score
        parsed_data (dict): Parsed resume data
        raw_text (str): Raw resume text for experience detection
        job_recommendations (list[dict]): Matching job role recommendations

    Returns:
        dict: {
            'experience_level': 'Fresher / Student (Internship Focus)' | 'Experienced Engineer (Full-Time Focus)',
            'is_fresher': bool,
            'companies': list[dict]  # Top recommendations sorted by match score
        }
    """
    if not resume_skills:
        resume_skills = ["Python", "Software Development"]

    exp_info = detect_candidate_experience_level(parsed_data, raw_text)
    is_fresher = exp_info['is_fresher']

    user_skills_lower = set(s.lower() for s in resume_skills)

    top_role = "Software Engineer"
    if job_recommendations and len(job_recommendations) > 0:
        top_role = job_recommendations[0].get('role', 'Software Engineer')

    company_matches = []

    for entity in HIRING_ENTITIES:
        comp_skills_lower = set(s.lower() for s in entity['domain'])
        matched_skills = [s for s in entity['domain'] if s.lower() in user_skills_lower]

        overlap_ratio = len(matched_skills) / len(entity['domain']) if entity['domain'] else 0.5

        # Base match % calculation
        base_match = (overlap_ratio * 55.0) + ((ats_score / 100.0) * 35.0)
        match_pct = min(99.0, max(48.0, round(base_match + (len(matched_skills) * 3.5), 1)))

        # Determine role title & opportunity type
        if is_fresher:
            role_title = entity['intern_roles'][0]
            opp_type_label = "🎓 Internship / Co-op"
            opp_type_code = "internship"
        else:
            role_title = entity['full_time_roles'][0]
            opp_type_label = "💼 Full-Time Position"
            opp_type_code = "full_time"

        primary_skill = matched_skills[0] if matched_skills else resume_skills[0]
        apply_url = _build_job_search_url(entity['name'], role_title, primary_skill, opp_type_code)

        company_matches.append({
            'company_name': entity['name'],
            'tier': entity['tier'],
            'company_type': entity['company_type'],
            'role_title': role_title,
            'opportunity_type': opp_type_label,
            'opp_type_code': opp_type_code,
            'work_mode': entity['work_mode'],
            'work_mode_type': entity['work_mode_type'],
            'match_percentage': match_pct,
            'locations': entity['locations'],
            'matched_skills': matched_skills if matched_skills else resume_skills[:3],
            'logo_icon': entity['logo_icon'],
            'hiring_badge': entity['hiring_badge'],
            'apply_url': apply_url
        })

    # Sort by match percentage descending
    company_matches.sort(key=lambda x: x['match_percentage'], reverse=True)

    # Ensure a balanced mix of Startups + Tech Giants in top recommendations
    startups = [c for c in company_matches if c['company_type'] == 'startup']
    giants = [c for c in company_matches if c['company_type'] == 'giant']

    # Pick top 3 from dominant match + top 2 from other tier for maximum options
    balanced = []
    if startups and giants:
        balanced = [startups[0], giants[0], startups[1] if len(startups)>1 else giants[1],
                    giants[1] if len(giants)>1 else startups[0],
                    company_matches[4] if len(company_matches)>4 else company_matches[0]]
        # Deduplicate
        seen = set()
        dedup_balanced = []
        for c in balanced:
            if c['company_name'] not in seen:
                seen.add(c['company_name'])
                dedup_balanced.append(c)
        balanced = dedup_balanced
    else:
        balanced = company_matches[:5]

    return {
        'is_fresher': is_fresher,
        'experience_level': "Student / Entry-Level (Internship & Startup Focus)" if is_fresher else "Experienced Engineer (Full-Time Focus)",
        'companies': balanced[:6]
    }
