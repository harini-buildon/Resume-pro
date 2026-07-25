import sys
sys.path.insert(0, '.')
from utils.job_analyzer import analyze_job_match
from utils.resume_parser import parse_resume

resume = (
    "Python Flask Docker AWS CI/CD PostgreSQL Redis "
    "Machine Learning Scikit-learn Jenkins Agile Scrum "
    "System Design Unit Testing GitHub Actions Microservices"
)
jd = (
    "We are hiring a Python Backend Engineer. "
    "Requirements: Python, Flask, Docker, Kubernetes, AWS, CI/CD, "
    "PostgreSQL, Redis, Microservices, Agile, Scrum, Unit Testing, "
    "System Design, GitHub Actions, Scikit-learn."
)

parsed = parse_resume(resume)
result = analyze_job_match(resume, parsed.get('skills', []), jd)

print("=== KEYWORD MATCHING RESULT (After Fix) ===")
print(f"Keyword Match %  : {result['match_percentage']}")
print(f"Similarity Score : {result['similarity_score']}")
print(f"Matched ({len(result['matched_skills'])}):", result['matched_skills'])
print(f"Missing ({len(result['missing_skills'])}):", result['missing_skills'])
print()

# Verify no noise / duplicates
noise_in_missing = [k for k in result['missing_skills']
                    if ',' in k or k.lower() in {'backend engineer', 'ci', 'ci cd', 'ci/cd engineer'}]
if noise_in_missing:
    print("NOISE STILL IN MISSING:", noise_in_missing)
else:
    print("No noise or duplicates in missing keywords.")
