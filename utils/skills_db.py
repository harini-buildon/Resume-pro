"""
utils/skills_db.py – Predefined Skills Database
=================================================
This module contains a curated database of technical and professional skills
organized by category. It's used to:
1. Match skills found in resumes
2. Extract skills from job descriptions
3. Identify missing skills for improvement suggestions

WHY A PREDEFINED DATABASE?
──────────────────────────
Instead of trying to detect any possible skill (which is error-prone),
we match against a known list. This gives us:
- Consistent skill names (e.g., "Machine Learning" not "ML" or "machine learning")
- Categorized skills for better analysis
- Easy to expand by adding new skills to the dictionary

The matching is case-insensitive using word boundaries to avoid
false positives (e.g., "R" shouldn't match every word containing "r").
"""

import re


# ──────────────────────────────────────────────────────────
# Skills Database – Organized by Category
# ──────────────────────────────────────────────────────────
SKILLS_DATABASE = {
    'Programming Languages': [
        'Python', 'Java', 'C++', 'C', 'JavaScript', 'TypeScript',
        'R', 'Go', 'Rust', 'Kotlin', 'Swift', 'PHP', 'Ruby',
        'Scala', 'MATLAB', 'Perl', 'Shell Scripting', 'Bash'
    ],
    
    'Web Technologies': [
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js',
        'Express.js', 'Flask', 'Django', 'Spring Boot', 'Bootstrap',
        'Tailwind CSS', 'jQuery', 'Next.js', 'REST APIs', 'GraphQL',
        'FastAPI', 'Svelte'
    ],
    
    'Databases': [
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Redis',
        'Oracle', 'Cassandra', 'Firebase', 'DynamoDB', 'Neo4j',
        'Elasticsearch'
    ],
    
    'Cloud & DevOps': [
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
        'CI/CD', 'Terraform', 'Ansible', 'Linux', 'Nginx', 'Apache',
        'Heroku', 'Vercel', 'Netlify', 'GitHub Actions'
    ],
    
    'AI & Machine Learning': [
        'Machine Learning', 'Deep Learning', 'NLP',
        'Natural Language Processing', 'Computer Vision',
        'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
        'OpenCV', 'Hugging Face', 'NLTK', 'SpaCy',
        'Reinforcement Learning', 'GANs', 'Transformers',
        'Large Language Models', 'LLM'
    ],
    
    'Data Science & Analytics': [
        'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Plotly',
        'Tableau', 'Power BI', 'Excel', 'Jupyter',
        'Data Analysis', 'Data Visualization', 'Statistics',
        'Data Mining', 'ETL', 'Data Warehousing', 'Apache Spark',
        'Hadoop', 'Snowflake', 'Airflow'
    ],
    
    'Tools & Version Control': [
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira',
        'Confluence', 'Slack', 'VS Code', 'IntelliJ',
        'Postman', 'Swagger', 'Figma'
    ],
    
    'Software Engineering': [
        'Data Structures', 'Algorithms', 'Data Structures and Algorithms',
        'Object-Oriented Programming', 'OOP', 'Design Patterns',
        'System Design', 'Microservices', 'Agile', 'Scrum',
        'Test-Driven Development', 'TDD', 'Unit Testing',
        'API Development', 'Software Development Life Cycle', 'SDLC'
    ],
    
    'Cybersecurity': [
        'Cybersecurity', 'Penetration Testing', 'Ethical Hacking',
        'Network Security', 'Cryptography', 'OWASP', 'Firewalls'
    ],
    
    'Other Technical Skills': [
        'Blockchain', 'IoT', 'Internet of Things', 'Embedded Systems',
        'Arduino', 'Raspberry Pi', 'ROS', 'MATLAB', 'Simulink',
        'AutoCAD', 'SolidWorks', 'Unity', 'Unreal Engine',
        'Mobile Development', 'Android', 'iOS', 'Flutter', 'React Native'
    ]
}


def get_all_skills():
    """
    Returns a flat list of all skills from every category.
    
    Example output: ['Python', 'Java', 'C++', ..., 'React Native']
    """
    all_skills = []
    for category_skills in SKILLS_DATABASE.values():
        all_skills.extend(category_skills)
    return all_skills


def get_skills_by_category():
    """
    Returns the full categorized skills dictionary.
    
    Useful for displaying skills organized by category on the dashboard.
    """
    return SKILLS_DATABASE


def match_skills(text):
    """
    Find all predefined skills that appear in the given text.
    
    How it works:
    1. Convert text to lowercase for case-insensitive matching
    2. For each skill in our database, check if it appears in the text
    3. Use word boundary regex to avoid partial matches
       (e.g., "C" shouldn't match "Company" or "Can")
    
    Parameters:
        text (str): The text to search for skills (resume or job description)
    
    Returns:
        list: List of matched skill names (original casing from our database)
    """
    if not text:
        return []
    
    text_lower = text.lower()
    matched = []
    
    for category, skills in SKILLS_DATABASE.items():
        for skill in skills:
            # Create a regex pattern with word boundaries
            # re.escape() handles special regex characters in skill names
            # (e.g., "C++" has special characters + that need escaping)
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            
            try:
                if re.search(pattern, text_lower):
                    if skill not in matched:  # Avoid duplicates
                        matched.append(skill)
            except re.error:
                # Fallback: simple substring check if regex fails
                if skill.lower() in text_lower:
                    if skill not in matched:
                        matched.append(skill)
    
    return matched


def get_skill_category(skill_name):
    """
    Find which category a skill belongs to.
    
    Parameters:
        skill_name (str): The skill to look up
    
    Returns:
        str: Category name, or 'Other' if not found
    """
    for category, skills in SKILLS_DATABASE.items():
        if skill_name in skills:
            return category
    return 'Other'


def categorize_skills(skill_list):
    """
    Organize a list of skills into categories.
    
    Parameters:
        skill_list (list): List of skill name strings
    
    Returns:
        dict: Skills grouped by category
              Example: {'Programming Languages': ['Python', 'Java'], ...}
    """
    categorized = {}
    for skill in skill_list:
        category = get_skill_category(skill)
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(skill)
    return categorized
