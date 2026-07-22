"""
utils/job_recommender.py – Job Role Recommendation Engine
==========================================================
This module recommends suitable job roles based on the skills
found in a user's resume.

HOW IT WORKS:
────────────
1. We define a mapping of job roles to their required skill sets
2. For each role, we count how many of its required skills the user has
3. We calculate a "fit percentage" for each role
4. We return the top matching roles sorted by fit

This is a rule-based approach. In a production system, you might
use a trained ML model, but this approach is transparent and
easy to understand for beginners.
"""


# ──────────────────────────────────────────────────────────
# Job Role → Required Skills Mapping
# Each role has a list of skills that are typically required
# ──────────────────────────────────────────────────────────
JOB_ROLES = {
    'Data Analyst': {
        'skills': ['Python', 'SQL', 'Excel', 'Pandas', 'NumPy', 'Tableau',
                   'Power BI', 'Data Analysis', 'Data Visualization',
                   'Statistics', 'R', 'Matplotlib'],
        'description': 'Analyze data to help businesses make better decisions.',
        'icon': '📊'
    },
    'Data Scientist': {
        'skills': ['Python', 'SQL', 'Machine Learning', 'Deep Learning',
                   'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch',
                   'Statistics', 'R', 'Data Visualization', 'NLP'],
        'description': 'Build predictive models and extract insights from complex data.',
        'icon': '🔬'
    },
    'Machine Learning Engineer': {
        'skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow',
                   'PyTorch', 'Scikit-learn', 'Docker', 'AWS', 'Linux',
                   'Data Structures', 'Algorithms', 'REST APIs', 'Git'],
        'description': 'Design and deploy machine learning models at scale.',
        'icon': '🤖'
    },
    'AI Engineer': {
        'skills': ['Python', 'Machine Learning', 'Deep Learning', 'NLP',
                   'Computer Vision', 'TensorFlow', 'PyTorch', 'Docker',
                   'AWS', 'Large Language Models', 'Transformers', 'Hugging Face'],
        'description': 'Build AI-powered products and intelligent systems.',
        'icon': '🧠'
    },
    'Python Developer': {
        'skills': ['Python', 'Flask', 'Django', 'REST APIs', 'SQL',
                   'Git', 'Docker', 'Linux', 'PostgreSQL', 'MongoDB',
                   'FastAPI', 'Unit Testing'],
        'description': 'Develop backend systems and APIs using Python.',
        'icon': '🐍'
    },
    'Backend Developer': {
        'skills': ['Python', 'Java', 'Node.js', 'REST APIs', 'SQL',
                   'PostgreSQL', 'MongoDB', 'Docker', 'Git', 'Linux',
                   'Microservices', 'AWS', 'Redis'],
        'description': 'Build server-side logic, APIs, and database systems.',
        'icon': '⚙️'
    },
    'Full Stack Developer': {
        'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js',
                   'Python', 'SQL', 'MongoDB', 'Git', 'REST APIs',
                   'Docker', 'Bootstrap', 'TypeScript'],
        'description': 'Develop both frontend and backend of web applications.',
        'icon': '🌐'
    },
    'Frontend Developer': {
        'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript',
                   'Bootstrap', 'Tailwind CSS', 'Vue.js', 'Angular',
                   'Git', 'Figma', 'Next.js'],
        'description': 'Create beautiful, interactive user interfaces.',
        'icon': '🎨'
    },
    'DevOps Engineer': {
        'skills': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
                   'Jenkins', 'CI/CD', 'Linux', 'Terraform', 'Git',
                   'Ansible', 'Python', 'Shell Scripting'],
        'description': 'Automate deployment pipelines and manage cloud infrastructure.',
        'icon': '🚀'
    },
    'Business Analyst': {
        'skills': ['Excel', 'SQL', 'Tableau', 'Power BI', 'Python',
                   'Data Analysis', 'Statistics', 'Jira', 'Agile',
                   'Data Visualization'],
        'description': 'Bridge business needs with technical solutions.',
        'icon': '📈'
    },
    'Cloud Engineer': {
        'skills': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
                   'Terraform', 'Linux', 'Python', 'CI/CD', 'Networking',
                   'Jenkins', 'Ansible'],
        'description': 'Design and manage cloud computing infrastructure.',
        'icon': '☁️'
    },
    'Cybersecurity Analyst': {
        'skills': ['Cybersecurity', 'Network Security', 'Linux', 'Python',
                   'Penetration Testing', 'Ethical Hacking', 'Cryptography',
                   'OWASP', 'Firewalls'],
        'description': 'Protect systems and networks from security threats.',
        'icon': '🔒'
    },
}


def recommend_jobs(resume_skills):
    """
    Recommend job roles based on the user's skills.
    
    Algorithm:
    1. For each job role, count how many required skills the user has
    2. Calculate fit percentage = (matched / total_required) × 100
    3. Only include roles with fit ≥ 20%
    4. Sort by fit percentage (highest first)
    5. Return top 5 recommendations
    
    Parameters:
        resume_skills (list): Skills extracted from the user's resume
    
    Returns:
        list: List of recommendation dicts, each containing:
            - 'role': str (job title)
            - 'fit_percentage': float
            - 'matched_skills': list (skills the user already has)
            - 'skills_to_learn': list (skills the user is missing)
            - 'description': str
            - 'icon': str
    """
    if not resume_skills:
        return []
    
    # Normalize to lowercase for comparison
    user_skills_lower = set(skill.lower() for skill in resume_skills)
    
    recommendations = []
    
    for role, role_data in JOB_ROLES.items():
        role_skills = role_data['skills']
        role_skills_lower = set(skill.lower() for skill in role_skills)
        
        # Find matched and missing skills
        matched_lower = user_skills_lower & role_skills_lower
        missing_lower = role_skills_lower - user_skills_lower
        
        # Map back to original casing
        matched = [s for s in role_skills if s.lower() in matched_lower]
        missing = [s for s in role_skills if s.lower() in missing_lower]
        
        # Calculate fit percentage
        fit = (len(matched) / len(role_skills)) * 100 if role_skills else 0
        
        # Only include roles where the user has at least 20% match
        if fit >= 20:
            recommendations.append({
                'role': role,
                'fit_percentage': round(fit, 1),
                'matched_skills': matched,
                'skills_to_learn': missing,
                'description': role_data['description'],
                'icon': role_data['icon']
            })
    
    # Sort by fit percentage (highest first)
    recommendations.sort(key=lambda x: x['fit_percentage'], reverse=True)
    
    # Return top 5
    return recommendations[:5]
