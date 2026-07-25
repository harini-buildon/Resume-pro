"""
utils/interview_generator.py – AI Mock Interview Question Generator
======================================================================
Generates technical & behavioral interview questions tailored to the candidate's
missing skills and target role using the STAR method framework.
"""

from utils.llm_client import generate_json
import json

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
    }
}

DEFAULT_BEHAVIORAL_QUESTIONS = [
    {
        "question": "Describe a time when you had to debug a critical production bug under time pressure. What steps did you take?",
        "type": "Behavioral (STAR Method)",
        "answer_framework": "Situation: Context of failure. Task: Your role. Action: Log inspection, root cause isolation, rollback/patch. Result: System restored & post-mortem."
    }
]

def generate_mock_interview(candidate_skills, missing_skills=None, target_role="Software Engineer"):
    """
    Generate mock interview questions tailored to candidate skills and missing skill gaps.

    Returns:
        list[dict]: List of question cards with STAR answer frameworks
    """
    prompt = f"""
    Generate 5 highly technical and behavioral interview questions for a {target_role}.
    The candidate has these core skills: {candidate_skills[:5] if candidate_skills else 'General Software Engineering'}
    The candidate is MISSING these skills for the job: {missing_skills[:5] if missing_skills else 'None'}

    Return exactly 5 questions in the following JSON array format, nothing else:
    [
        {{
            "skill": "Name of the skill being tested",
            "target_role": "{target_role}",
            "question": "The interview question",
            "type": "Technical or Behavioral (STAR Method)",
            "answer_framework": "A short guide on how to answer it effectively",
            "category": "Skill Gap Focus OR Core Mastery Focus"
        }}
    ]
    """

    system_instruction = "You are a FAANG-level technical interviewer generating structured JSON interview questions."
    
    # Try Gemini API
    ai_questions = generate_json(prompt, system_instruction)
    
    if ai_questions and isinstance(ai_questions, list) and len(ai_questions) > 0:
        return ai_questions

    # Fallback to static rules if API fails
    questions = []
    if missing_skills:
        for skill in missing_skills:
            if skill in INTERVIEW_QUESTION_BANK and len(questions) < 2:
                q_data = INTERVIEW_QUESTION_BANK[skill]
                questions.append({
                    "skill": skill, "target_role": target_role,
                    "question": q_data["question"], "type": q_data["type"],
                    "answer_framework": q_data["answer_framework"], "category": "Skill Gap Focus"
                })

    if candidate_skills:
        for skill in candidate_skills:
            if skill in INTERVIEW_QUESTION_BANK and len(questions) < 4:
                q_data = INTERVIEW_QUESTION_BANK[skill]
                questions.append({
                    "skill": skill, "target_role": target_role,
                    "question": q_data["question"], "type": q_data["type"],
                    "answer_framework": q_data["answer_framework"], "category": "Core Mastery Focus"
                })

    for beh_q in DEFAULT_BEHAVIORAL_QUESTIONS:
        if len(questions) < 5:
            questions.append({
                "skill": "Engineering Practices", "target_role": target_role,
                "question": beh_q["question"], "type": beh_q["type"],
                "answer_framework": beh_q["answer_framework"], "category": "Behavioral Leadership"
            })

    return questions
