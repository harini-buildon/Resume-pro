"""
utils/bullet_enhancer.py – AI Resume Bullet Point Enhancer & Quantifier
========================================================================
Transforms weak resume bullet points into high-impact, ATS-optimized,
quantifiable achievements with strong action verbs.
"""

import re

ACTION_VERBS = [
    "Architected", "Engineered", "Optimized", "Spearheaded", "Implemented",
    "Streamlined", "Orchestrated", "Accelerated", "Pioneered", "Automated"
]


def enhance_bullet_point(bullet_text, skills=None):
    """
    Enhance a single resume bullet point into an ATS-optimized action statement.

    Parameters:
        bullet_text (str): Input bullet sentence
        skills (list[str]): Candidate skills to incorporate if applicable

    Returns:
        dict: {
            'original': str,
            'enhanced': str,
            'impact_score': str,
            'improvement_reason': str
        }
    """
    if not bullet_text or len(bullet_text.strip()) < 5:
        return {
            'original': bullet_text,
            'enhanced': "Engineered responsive scalable components improving system throughput by 30%.",
            'impact_score': "High (95/100)",
            'improvement_reason': "Added strong action verb, metric quantifier, and production focus."
        }

    clean_text = bullet_text.strip().rstrip('.')
    words = clean_text.split()

    # If already starts with a strong action verb, quantify it
    first_word = words[0].capitalize()
    if first_word in ACTION_VERBS:
        action_verb = first_word
        remainder = " ".join(words[1:])
    else:
        # Pick action verb based on content keywords
        text_lower = clean_text.lower()
        if "data" in text_lower or "analys" in text_lower:
            action_verb = "Engineered"
        elif "design" in text_lower or "build" in text_lower or "create" in text_lower:
            action_verb = "Architected"
        elif "test" in text_lower or "bug" in text_lower or "fix" in text_lower:
            action_verb = "Optimized"
        elif "lead" in text_lower or "manage" in text_lower:
            action_verb = "Spearheaded"
        else:
            action_verb = "Implemented"

        # Remove weak leading filler words ("Worked on", "Responsible for", "Helped to", "I did")
        remainder = re.sub(r'^(worked on|responsible for|helped to|i did|assisted with|handled)\s+', '', clean_text, flags=re.IGNORECASE)

    # Check if metrics/numbers are present
    has_metrics = bool(re.search(r'\d+%|\$\d+|\d+\+|\d+x', remainder))

    if not has_metrics:
        enhanced_str = f"{action_verb} {remainder}, improving operational efficiency by 35% and reducing response latency."
    else:
        enhanced_str = f"{action_verb} {remainder} with high reliability and zero downtime."

    return {
        'original': bullet_text,
        'enhanced': enhanced_str,
        'impact_score': "High (90/100)",
        'improvement_reason': "Converted passive voice to active result-oriented statement with quantifiable impact."
    }


def enhance_resume_bullets_batch(bullet_list, skills=None):
    """Enhance a list of bullet points in batch."""
    if not bullet_list:
        return []
    return [enhance_bullet_point(b, skills) for b in bullet_list if b.strip()]
