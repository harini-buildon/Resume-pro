"""
utils/course_recommender.py – Learning & Course Recommendation Engine
======================================================================
This module suggests learning topics and resources based on the skills
a user is missing from their resume or from a job description.

HOW IT WORKS:
────────────
1. Takes a list of missing skills (from job comparison or general analysis)
2. Maps each missing skill to a recommended learning topic
3. Returns structured recommendations with descriptions

This helps users create a learning roadmap to improve their resume
and become more competitive for their target roles.
"""


# ──────────────────────────────────────────────────────────
# Skill → Learning Resource Mapping
# Each skill maps to a learning recommendation with:
# - topic: What to study
# - description: Brief explanation of what to learn
# - level: beginner / intermediate / advanced
# ──────────────────────────────────────────────────────────
SKILL_COURSES = {
    'Python': {
        'topic': 'Python Programming',
        'description': 'Start with Python basics: variables, loops, functions, OOP. Then explore libraries like Pandas and NumPy.',
        'level': 'beginner',
        'platforms': 'Coursera, freeCodeCamp, Python.org tutorial'
    },
    'Java': {
        'topic': 'Java Programming',
        'description': 'Learn Java fundamentals, OOP concepts, collections, and exception handling. Practice with small projects.',
        'level': 'beginner',
        'platforms': 'Udemy, Codecademy, Oracle Java tutorials'
    },
    'SQL': {
        'topic': 'SQL & Database Management',
        'description': 'Master SELECT, JOIN, GROUP BY, subqueries, indexing, and database design. Practice on LeetCode or HackerRank.',
        'level': 'beginner',
        'platforms': 'W3Schools, Khan Academy, SQLZoo'
    },
    'JavaScript': {
        'topic': 'JavaScript Essentials',
        'description': 'Learn DOM manipulation, ES6+ features, async/await, and closures. Build interactive web pages.',
        'level': 'beginner',
        'platforms': 'freeCodeCamp, JavaScript.info, Codecademy'
    },
    'React': {
        'topic': 'React.js Frontend Development',
        'description': 'Learn component-based architecture, hooks, state management, and routing. Build a portfolio project.',
        'level': 'intermediate',
        'platforms': 'React official docs, Scrimba, Udemy'
    },
    'Machine Learning': {
        'topic': 'Machine Learning Fundamentals',
        'description': 'Study supervised/unsupervised learning, regression, classification, and model evaluation. Use Scikit-learn.',
        'level': 'intermediate',
        'platforms': 'Andrew Ng\'s Coursera course, fast.ai, Google ML Crash Course'
    },
    'Deep Learning': {
        'topic': 'Deep Learning & Neural Networks',
        'description': 'Learn neural network architectures (CNN, RNN, Transformers), backpropagation, and optimization.',
        'level': 'advanced',
        'platforms': 'deeplearning.ai, fast.ai, Stanford CS231n'
    },
    'NLP': {
        'topic': 'Natural Language Processing',
        'description': 'Study tokenization, embeddings, sentiment analysis, named entity recognition, and transformers.',
        'level': 'advanced',
        'platforms': 'Hugging Face course, Stanford CS224n, Coursera NLP Specialization'
    },
    'TensorFlow': {
        'topic': 'TensorFlow Framework',
        'description': 'Learn to build, train, and deploy ML models using TensorFlow and Keras. Start with the official tutorials.',
        'level': 'intermediate',
        'platforms': 'TensorFlow.org, Coursera TF Developer Certificate'
    },
    'PyTorch': {
        'topic': 'PyTorch Framework',
        'description': 'Learn dynamic computation graphs, model building, and training loops. Popular in research.',
        'level': 'intermediate',
        'platforms': 'PyTorch.org tutorials, fast.ai, Udacity'
    },
    'Docker': {
        'topic': 'Docker & Containerization',
        'description': 'Learn to build, run, and manage containers. Understand Dockerfiles, images, volumes, and Docker Compose.',
        'level': 'intermediate',
        'platforms': 'Docker official docs, Docker Labs, KodeKloud'
    },
    'Kubernetes': {
        'topic': 'Kubernetes Orchestration',
        'description': 'Learn pods, deployments, services, and cluster management. Essential for cloud-native applications.',
        'level': 'advanced',
        'platforms': 'Kubernetes.io, KodeKloud, CKAD certification'
    },
    'AWS': {
        'topic': 'Amazon Web Services (AWS)',
        'description': 'Start with EC2, S3, Lambda, and RDS. Consider the AWS Cloud Practitioner certification.',
        'level': 'intermediate',
        'platforms': 'AWS Skill Builder, A Cloud Guru, Stephane Maarek on Udemy'
    },
    'Azure': {
        'topic': 'Microsoft Azure Cloud',
        'description': 'Learn Azure fundamentals: VMs, App Services, Azure Functions, and Azure DevOps.',
        'level': 'intermediate',
        'platforms': 'Microsoft Learn (free), AZ-900 certification path'
    },
    'GCP': {
        'topic': 'Google Cloud Platform',
        'description': 'Learn Compute Engine, Cloud Functions, BigQuery, and AI/ML services.',
        'level': 'intermediate',
        'platforms': 'Google Cloud Skills Boost, Coursera GCP courses'
    },
    'Git': {
        'topic': 'Git Version Control',
        'description': 'Master branching, merging, rebasing, and collaborative workflows. Use GitHub for your projects.',
        'level': 'beginner',
        'platforms': 'Git official docs, Atlassian Git tutorials, GitHub Learning Lab'
    },
    'Flask': {
        'topic': 'Flask Web Framework',
        'description': 'Build REST APIs and web apps with Flask. Learn routing, templates, forms, and database integration.',
        'level': 'beginner',
        'platforms': 'Flask Mega-Tutorial, Corey Schafer YouTube, Real Python'
    },
    'Django': {
        'topic': 'Django Web Framework',
        'description': 'Learn Django\'s MTV pattern, ORM, admin panel, and REST framework. Build a CRUD application.',
        'level': 'intermediate',
        'platforms': 'Django official tutorial, Django Girls, Real Python'
    },
    'REST APIs': {
        'topic': 'RESTful API Design',
        'description': 'Understand HTTP methods, status codes, authentication, and API best practices.',
        'level': 'intermediate',
        'platforms': 'Postman Learning Center, REST API Tutorial, MDN Web Docs'
    },
    'Pandas': {
        'topic': 'Pandas Data Analysis',
        'description': 'Master DataFrames, data cleaning, merging, grouping, and time series analysis.',
        'level': 'beginner',
        'platforms': 'Pandas official docs, Kaggle Learn, Real Python'
    },
    'Data Structures': {
        'topic': 'Data Structures & Algorithms',
        'description': 'Study arrays, linked lists, trees, graphs, sorting, and searching algorithms. Practice on LeetCode.',
        'level': 'intermediate',
        'platforms': 'LeetCode, HackerRank, GeeksforGeeks, Striver\'s SDE Sheet'
    },
    'Linux': {
        'topic': 'Linux System Administration',
        'description': 'Learn the command line, file system, permissions, shell scripting, and process management.',
        'level': 'beginner',
        'platforms': 'Linux Journey, The Linux Foundation, Ubuntu tutorials'
    },
    'Tableau': {
        'topic': 'Tableau Data Visualization',
        'description': 'Create interactive dashboards, charts, and reports. Learn calculated fields and LOD expressions.',
        'level': 'beginner',
        'platforms': 'Tableau Public (free), Tableau eLearning, Coursera'
    },
    'Power BI': {
        'topic': 'Power BI Analytics',
        'description': 'Build interactive reports and dashboards. Learn DAX formulas and data modeling.',
        'level': 'beginner',
        'platforms': 'Microsoft Learn, Guy in a Cube YouTube, Udemy'
    },
}


def recommend_courses(missing_skills):
    """
    Recommend courses/learning topics based on missing skills.
    
    Parameters:
        missing_skills (list): Skills the user is missing
    
    Returns:
        list: List of course recommendation dicts, each containing:
            - 'skill': str (the missing skill)
            - 'topic': str (what to study)
            - 'description': str (learning path details)
            - 'level': str (beginner/intermediate/advanced)
            - 'platforms': str (where to learn)
    """
    recommendations = []
    
    for skill in missing_skills:
        # Look up the skill in our course database
        if skill in SKILL_COURSES:
            course = SKILL_COURSES[skill]
            recommendations.append({
                'skill': skill,
                'topic': course['topic'],
                'description': course['description'],
                'level': course['level'],
                'platforms': course['platforms']
            })
        else:
            # Generic recommendation for skills not in our database
            recommendations.append({
                'skill': skill,
                'topic': f'Learn {skill}',
                'description': f'Search for beginner-friendly tutorials on {skill}. Practice with hands-on projects.',
                'level': 'beginner',
                'platforms': 'YouTube, Coursera, Udemy, official documentation'
            })
    
    return recommendations


def recommend_general_courses(resume_skills):
    """
    Recommend general learning topics based on what the user already knows.
    
    Identifies skill gaps in the user's profile and suggests
    complementary skills they should learn.
    
    Parameters:
        resume_skills (list): Skills the user currently has
    
    Returns:
        list: Course recommendations for complementary skills
    """
    user_skills_lower = set(s.lower() for s in resume_skills)
    
    # Define skill progressions
    # If user knows X, suggest they learn Y next
    progressions = {
        'python': ['Flask', 'Django', 'Pandas', 'Machine Learning'],
        'machine learning': ['Deep Learning', 'TensorFlow', 'PyTorch', 'NLP'],
        'html': ['CSS', 'JavaScript', 'React'],
        'javascript': ['React', 'Node.js', 'TypeScript'],
        'sql': ['PostgreSQL', 'MongoDB', 'Data Analysis'],
        'git': ['Docker', 'CI/CD', 'GitHub Actions'],
    }
    
    suggested_skills = set()
    
    for user_skill in user_skills_lower:
        if user_skill in progressions:
            for next_skill in progressions[user_skill]:
                if next_skill.lower() not in user_skills_lower:
                    suggested_skills.add(next_skill)
    
    return recommend_courses(list(suggested_skills)[:5])
