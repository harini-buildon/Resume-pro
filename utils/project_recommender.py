"""
utils/project_recommender.py – Career Growth Project Recommender
===================================================================
Recommends resume-boosting project ideas tailored to the candidate's
skills and missing skill gaps, categorized into 3 complexity tiers:
1. 🟢 Basic Level (Foundation & Core Skills)
2. 🟡 Medium Level (Full Stack / REST APIs / End-to-End)
3. 🔴 High Level (Production-grade / Cloud / AI / Microservices)
"""

PROJECT_CATALOG = [
    # --- PYTHON & BACKEND ---
    {
        "domain": ["python", "flask", "django", "fastapi", "rest apis", "backend", "sql"],
        "level": "basic",
        "level_label": "🟢 Basic (Foundation)",
        "title": "RESTful Task Management & Auth API",
        "tech_stack": ["Python", "Flask", "SQLite", "JWT Auth", "Postman"],
        "description": "Build a secure REST API with user registration, JWT authentication, and CRUD task endpoints.",
        "resume_impact": "Demonstrates core backend API design, authentication flows, and relational database handling.",
        "key_features": ["JWT Authentication", "Role-based Access Control", "Swagger API Documentation"]
    },
    {
        "domain": ["python", "flask", "django", "fastapi", "rest apis", "postgresql", "redis"],
        "level": "medium",
        "level_label": "🟡 Medium (Full-Stack & Caching)",
        "title": "High-Throughput E-Commerce Backend with Redis Caching",
        "tech_stack": ["Python", "Django", "PostgreSQL", "Redis", "Celery", "Docker"],
        "description": "Design a resilient backend with inventory management, asynchronous email queues, and Redis session caching.",
        "resume_impact": "Proves ability to build scalable e-commerce systems, optimize slow DB queries, and handle async workers.",
        "key_features": ["Redis Cache Layer", "Celery Async Tasks", "PostgreSQL Query Indexing"]
    },
    {
        "domain": ["python", "docker", "kubernetes", "microservices", "aws", "ci/cd"],
        "level": "high",
        "level_label": "🔴 High (Production Microservices)",
        "title": "Distributed Event-Driven Microservices Platform",
        "tech_stack": ["Python", "FastAPI", "Apache Kafka", "Docker", "Kubernetes", "AWS ECS", "GitHub Actions"],
        "description": "Build an event-driven microservices architecture communicating via Kafka with automated CI/CD pipeline deployment.",
        "resume_impact": "High-value enterprise project showing cloud deployment, message queues, and Kubernetes orchestration.",
        "key_features": ["Event-Driven Kafka Messaging", "Kubernetes Auto-scaling", "Automated CI/CD Deployment"]
    },

    # --- DATA SCIENCE & AI / ML ---
    {
        "domain": ["python", "pandas", "numpy", "scikit-learn", "machine learning", "data analysis", "tableau"],
        "level": "basic",
        "level_label": "🟢 Basic (Foundation)",
        "title": "Customer Churn Prediction & Exploratory EDA",
        "tech_stack": ["Python", "Pandas", "Scikit-learn", "Matplotlib", "Seaborn", "Jupyter"],
        "description": "Clean a 10,000+ customer dataset, perform exploratory statistical analysis, and train a Logistic Regression / Random Forest classifier.",
        "resume_impact": "Validates data wrangling, feature engineering, and binary classification modeling skills.",
        "key_features": ["Exploratory Data Analysis (EDA)", "Feature Scaling & Encoding", "Model Evaluation Metrics"]
    },
    {
        "domain": ["python", "machine learning", "nlp", "scikit-learn", "spacy", "flask", "transformers"],
        "level": "medium",
        "level_label": "🟡 Medium (ML API Deployment)",
        "title": "Automated Resume Parser & NLP Sentiment Service",
        "tech_stack": ["Python", "spaCy", "Scikit-learn", "TF-IDF", "Flask", "Docker"],
        "description": "Develop an NLP service that parses unstructured documents, extracts key entities, and serves predictions via REST API.",
        "resume_impact": "Shows ability to bridge Machine Learning / NLP models with web server deployment.",
        "key_features": ["Entity Extraction with spaCy", "TF-IDF Text Classification", "Dockerized Container Service"]
    },
    {
        "domain": ["python", "deep learning", "pytorch", "tensorflow", "llm", "ai", "langchain"],
        "level": "high",
        "level_label": "🔴 High (Production AI & LLMs)",
        "title": "Enterprise RAG AI Assistant with Vector DB & LLM",
        "tech_stack": ["Python", "PyTorch", "LangChain", "Pinecone Vector DB", "OpenAI / Llama 3", "FastAPI", "Docker"],
        "description": "Build a Retrieval-Augmented Generation (RAG) system that embeds corporate docs into Vector DB for accurate domain Q&A.",
        "resume_impact": "Top-tier AI resume booster proving expertise in modern LLMs, Vector Databases, and RAG pipelines.",
        "key_features": ["Vector Search & Embeddings", "LangChain RAG Pipeline", "Real-Time Streaming Responses"]
    },

    # --- FRONTEND & FULL STACK ---
    {
        "domain": ["javascript", "html", "css", "react", "typescript", "bootstrap", "tailwind"],
        "level": "basic",
        "level_label": "🟢 Basic (Foundation)",
        "title": "Interactive Kanban Project Board with Drag & Drop",
        "tech_stack": ["React", "JavaScript / TypeScript", "Tailwind CSS", "HTML5 Drag API"],
        "description": "Create a responsive Trello-style Kanban board supporting column drag-and-drop, task filters, and local storage persistence.",
        "resume_impact": "Demonstrates strong component state management, UI event handling, and clean modern styling.",
        "key_features": ["Drag & Drop Interactivity", "State Management", "Responsive UI Design"]
    },
    {
        "domain": ["javascript", "react", "node.js", "express", "mongodb", "full stack", "typescript"],
        "level": "medium",
        "level_label": "🟡 Medium (Full-Stack MERN)",
        "title": "Real-Time Collaborative Workspace & Chat App",
        "tech_stack": ["React", "Node.js", "Express", "MongoDB", "Socket.io", "TypeScript"],
        "description": "Build a full-stack web application featuring WebSocket real-time messaging, multi-user rooms, and JWT user authentication.",
        "resume_impact": "Essential full-stack portfolio item proving real-time bi-directional communication and NoSQL database modeling.",
        "key_features": ["WebSocket Real-Time Messaging", "MongoDB Schema Design", "TypeScript Type Safety"]
    },

    # --- DEVOPS & CLOUD ---
    {
        "domain": ["docker", "aws", "devops", "linux", "git", "ci/cd", "terraform", "kubernetes"],
        "level": "medium",
        "level_label": "🟡 Medium (DevOps Pipeline)",
        "title": "Automated Cloud Infrastructure & CI/CD Pipeline",
        "tech_stack": ["Docker", "AWS S3 / EC2", "GitHub Actions", "Nginx", "Linux Shell"],
        "description": "Create a multi-stage Docker build pipeline that runs automated linting/tests and auto-deploys to AWS on git push.",
        "resume_impact": "Validates cloud automation, infrastructure as code concepts, and continuous integration workflows.",
        "key_features": ["Multi-Stage Dockerfile", "GitHub Actions Pipeline", "AWS Cloud Hosting"]
    }
]


def recommend_projects(resume_skills, missing_skills=None):
    """
    Recommend project ideas split into 3 complexity levels (Basic, Medium, High).

    Parameters:
        resume_skills (list[str]): Extracted resume skills
        missing_skills (list[str]): Optional missing skills from job match

    Returns:
        dict: {
            'basic': dict,
            'medium': dict,
            'high': dict,
            'all_projects': list[dict]
        }
    """
    if not resume_skills:
        resume_skills = ["Python", "Web Development"]

    all_user_skills = set(s.lower() for s in resume_skills)
    if missing_skills:
        all_user_skills.update(s.lower() for s in missing_skills)

    scored_projects = []

    for proj in PROJECT_CATALOG:
        proj_domain_lower = set(s.lower() for s in proj['domain'])
        overlap = len(proj_domain_lower & all_user_skills)

        # Give higher weight to projects addressing missing skills
        missing_boost = 0
        if missing_skills:
            missing_boost = len(proj_domain_lower & set(s.lower() for s in missing_skills)) * 2

        score = overlap + missing_boost
        scored_projects.append((score, proj))

    # Sort projects by score descending
    scored_projects.sort(key=lambda x: x[0], reverse=True)

    # Pick top project for each tier (Basic, Medium, High)
    basic_proj = next((p for s, p in scored_projects if p['level'] == 'basic'), PROJECT_CATALOG[0])
    medium_proj = next((p for s, p in scored_projects if p['level'] == 'medium'), PROJECT_CATALOG[1])
    high_proj = next((p for s, p in scored_projects if p['level'] == 'high'), PROJECT_CATALOG[2])

    return {
        'basic': basic_proj,
        'medium': medium_proj,
        'high': high_proj,
        'all_projects': [basic_proj, medium_proj, high_proj]
    }
