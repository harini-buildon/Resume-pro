"""
utils/interview_generator.py – AI Mock Interview Question Generator
======================================================================
Generates technical & behavioral interview questions tailored to the candidate's
missing skills and target role using the STAR method framework.
"""

INTERVIEW_QUESTION_BANK = {
    "Python": {
        "question": "How do Python's Global Interpreter Lock (GIL) and memory management affect concurrent processing?",
        "type": "Technical",
        "answer_framework": "Explain how GIL restricts execution to one native thread at a time per process. Contrast multi-threading (I/O bound) vs multi-processing / Celery (CPU bound)."
    },
    "Docker": {
        "question": "How do multi-stage Docker builds optimize image size and security in production?",
        "type": "Technical",
        "answer_framework": "Explain building in a compiler stage, copying only production artifacts to a lightweight alpine/distroless final image."
    },
    "Kubernetes": {
        "question": "Explain the difference between Kubernetes Liveness, Readiness, and Startup probes.",
        "type": "Technical",
        "answer_framework": "Liveness = restart container if frozen; Readiness = remove from service load balancer if busy; Startup = delay probes during boot."
    },
    "AWS": {
        "question": "How do you design a highly available, fault-tolerant infrastructure on AWS across multiple Availability Zones?",
        "type": "Technical",
        "answer_framework": "Mention Application Load Balancer (ALB), Multi-AZ RDS deployments, Auto Scaling Groups, and Route 53 DNS failover."
    },
    "React": {
        "question": "How do Virtual DOM diffing algorithms and React.memo optimize re-rendering performance?",
        "type": "Technical",
        "answer_framework": "Explain reconciliation key heuristics, memoization of props, and preventing unnecessary child component tree renders."
    },
    "REST APIs": {
        "question": "How do you enforce rate-limiting, authentication, and idempotency in RESTful API architectures?",
        "type": "Technical",
        "answer_framework": "Explain Token Bucket / Leaky Bucket algorithms with Redis, JWT bearer tokens, and Idempotency-Key HTTP headers for POST operations."
    },
    "SQL": {
        "question": "Explain SQL index structures (B-Tree vs Hash) and how EXPLAIN ANALYZE identifies slow query bottlenecks.",
        "type": "Technical",
        "answer_framework": "Detail B-Tree range scans, index selectivity, sequential scan penalties, and composite index column ordering."
    }
}

DEFAULT_BEHAVIORAL_QUESTIONS = [
    {
        "question": "Describe a time when you had to debug a critical production bug under time pressure. What steps did you take?",
        "type": "Behavioral (STAR Method)",
        "answer_framework": "Situation: Context of failure. Task: Your role. Action: Log inspection, root cause isolation, rollback/patch. Result: System restored & post-mortem."
    },
    {
        "question": "How do you handle technical disagreements regarding architecture or code reviews within your engineering team?",
        "type": "Behavioral (STAR Method)",
        "answer_framework": "Situation: Conflicting design proposals. Action: Benchmark performance, present data-driven tradeoffs. Result: Alignment on best solution."
    }
]


def generate_mock_interview(candidate_skills, missing_skills=None, target_role="Software Engineer"):
    """
    Generate mock interview questions tailored to candidate skills and missing skill gaps.

    Returns:
        list[dict]: List of question cards with STAR answer frameworks
    """
    questions = []

    # Priority 1: Pick questions addressing missing skills
    if missing_skills:
        for skill in missing_skills:
            if skill in INTERVIEW_QUESTION_BANK and len(questions) < 3:
                q_data = INTERVIEW_QUESTION_BANK[skill]
                questions.append({
                    "skill": skill,
                    "target_role": target_role,
                    "question": q_data["question"],
                    "type": q_data["type"],
                    "answer_framework": q_data["answer_framework"],
                    "category": "Skill Gap Focus"
                })

    # Priority 2: Pick questions for candidate's known skills
    if candidate_skills:
        for skill in candidate_skills:
            if skill in INTERVIEW_QUESTION_BANK and len(questions) < 4:
                q_data = INTERVIEW_QUESTION_BANK[skill]
                if not any(q['question'] == q_data['question'] for q in questions):
                    questions.append({
                        "skill": skill,
                        "target_role": target_role,
                        "question": q_data["question"],
                        "type": q_data["type"],
                        "answer_framework": q_data["answer_framework"],
                        "category": "Core Mastery Focus"
                    })

    # Fallback to default behavioral questions if list is short
    for beh_q in DEFAULT_BEHAVIORAL_QUESTIONS:
        if len(questions) < 5:
            questions.append({
                "skill": "Engineering Practices",
                "target_role": target_role,
                "question": beh_q["question"],
                "type": beh_q["type"],
                "answer_framework": beh_q["answer_framework"],
                "category": "Behavioral Leadership"
            })

    return questions
