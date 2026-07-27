"""
utils/nlp_processor.py – spaCy NLP Processor & Keyword Matcher
================================================================
This module handles NLP processing using spaCy:
1. Model loading & caching (en_core_web_sm) at module load
2. Text pre-processing: split comma/semicolon-separated lists BEFORE NLP
3. Text normalization (lemmatization, stop-words, punctuation removal)
4. Synonym canonicalization (e.g. JS -> JavaScript, sklearn -> Scikit-learn)
5. NOISE_WORDS filter: removes job-titles and generic non-skill phrases
6. Post-extraction deduplication: drops subset forms (CI dropped if CI/CD present)
7. Hard skill (2x) vs Soft skill (1x) weighted overlap calculation

BUGS FIXED vs previous version:
- "Docker, Kubernetes, AWS" was extracted as ONE noun chunk → now split first
- "Ci Cd" wrong casing from .title() on slash-terms → SYNONYM_MAP checked first
- "CI", "Ci Cd", "CI/CD" all appeared as separate missing keywords → deduped
- "Backend Engineer" treated as a skill → blocked by NOISE_WORDS
"""

import re
try:
    import spacy
except ImportError:
    spacy = None

from utils.skills_db import SKILLS_DATABASE, get_all_skills

# ─── Global spaCy model cache ────────────────────────────────────────────────
_NLP_MODEL = False  # False = uninitialized; None = failed to load


def get_spacy_nlp():
    """
    Load and cache spaCy 'en_core_web_sm' if available.
    Returns None if spaCy is not installed or model cannot be loaded.
    """
    global _NLP_MODEL
    if _NLP_MODEL is False:
        if spacy is None:
            _NLP_MODEL = None
            return None
        try:
            _NLP_MODEL = spacy.load("en_core_web_sm")
        except Exception:
            # Fall back to pure-Python regex NLP processor on serverless runtimes
            _NLP_MODEL = None
    return _NLP_MODEL


# ─── Synonym Canonical Mapping ────────────────────────────────────────────────
# Keys are LOWER-CASE. Values are the display/canonical form.
# ALWAYS look this up BEFORE applying any title/upper casing.
SYNONYM_MAP = {
    # JavaScript / TypeScript
    "js":                       "JavaScript",
    "javascript":               "JavaScript",
    "ts":                       "TypeScript",
    "typescript":               "TypeScript",
    # Python
    "py":                       "Python",
    "python":                   "Python",
    # React / Vue / Node
    "react":                    "React",
    "reactjs":                  "React",
    "react.js":                 "React",
    "node":                     "Node.js",
    "nodejs":                   "Node.js",
    "node.js":                  "Node.js",
    "vue":                      "Vue.js",
    "vuejs":                    "Vue.js",
    "vue.js":                   "Vue.js",
    # ML / AI
    "ml":                       "Machine Learning",
    "machine learning":         "Machine Learning",
    "dl":                       "Deep Learning",
    "deep learning":            "Deep Learning",
    "nlp":                      "NLP",
    "natural language processing": "NLP",
    "ai":                       "AI",
    "artificial intelligence":  "AI",
    "llm":                      "LLM",
    "large language model":     "LLM",
    "large language models":    "LLM",
    "llms":                     "LLM",
    # Scikit-learn variations
    "scikit-learn":             "Scikit-learn",
    "scikit learn":             "Scikit-learn",
    "sklearn":                  "Scikit-learn",
    # Cloud
    "aws":                      "AWS",
    "amazon web services":      "AWS",
    "gcp":                      "GCP",
    "google cloud":             "GCP",
    "google cloud platform":    "GCP",
    "azure":                    "Azure",
    "microsoft azure":          "Azure",
    # DevOps
    "k8s":                      "Kubernetes",
    "kubernetes":               "Kubernetes",
    "ci/cd":                    "CI/CD",
    "ci cd":                    "CI/CD",
    "cicd":                     "CI/CD",
    "continuous integration":   "CI/CD",
    "continuous delivery":      "CI/CD",
    "github actions":           "GitHub Actions",
    "docker":                   "Docker",
    "jenkins":                  "Jenkins",
    "terraform":                "Terraform",
    "ansible":                  "Ansible",
    # Databases
    "postgres":                 "PostgreSQL",
    "postgresql":               "PostgreSQL",
    "mongo":                    "MongoDB",
    "mongodb":                  "MongoDB",
    "sql":                      "SQL",
    "mysql":                    "MySQL",
    "redis":                    "Redis",
    "sqlite":                   "SQLite",
    "elasticsearch":            "Elasticsearch",
    # REST APIs
    "rest api":                 "REST APIs",
    "rest apis":                "REST APIs",
    "restful":                  "REST APIs",
    "restful api":              "REST APIs",
    "restful apis":             "REST APIs",
    "graphql":                  "GraphQL",
    # Microservices
    "microservice":             "Microservices",
    "microservices":            "Microservices",
    "microservice architecture": "Microservices",
    # Agile
    "agile":                    "Agile",
    "agile methodology":        "Agile",
    "scrum":                    "Scrum",
    # Testing
    "unit test":                "Unit Testing",
    "unit testing":             "Unit Testing",
    "tdd":                      "TDD",
    "test driven development":  "TDD",
    # OOP / Design
    "oop":                      "OOP",
    "object oriented":          "OOP",
    "object-oriented":          "OOP",
    "object oriented programming": "OOP",
    "system design":            "System Design",
    "design pattern":           "Design Patterns",
    "design patterns":          "Design Patterns",
    # DSA
    "dsa":                      "Data Structures & Algorithms",
    "data structures":          "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    # Misc
    "sdlc":                     "SDLC",
    "software development life cycle": "SDLC",
    "qa":                       "QA",
    "quality assurance":        "QA",
    "linux":                    "Linux",
    "git":                      "Git",
    "github":                   "GitHub",
    "gitlab":                   "GitLab",
    "flask":                    "Flask",
    "django":                   "Django",
    "fastapi":                  "FastAPI",
    "spring boot":              "Spring Boot",
    "tensorflow":               "TensorFlow",
    "pytorch":                  "PyTorch",
    "pandas":                   "Pandas",
    "numpy":                    "NumPy",
    "apache spark":             "Apache Spark",
    "apache airflow":           "Apache Airflow",
    "airflow":                  "Apache Airflow",
}

# ─── Soft Skills (weight = 1x; everything else = 2x) ─────────────────────────
SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "analytical skills", "work ethic", "interpersonal skills",
    "project management", "organization", "agile", "scrum", "mentorship",
    "attention to detail", "presentation", "negotiation",
}

# ─── Noise words — job titles & generic phrases that are NOT skills ───────────
NOISE_WORDS = {
    # Role/title words
    "engineer", "developer", "backend engineer", "software engineer",
    "frontend engineer", "full stack engineer", "data engineer",
    "machine learning engineer", "devops engineer", "cloud engineer",
    "senior engineer", "junior engineer", "lead engineer",
    # Generic JD language
    "experience", "candidate", "role", "description", "requirement",
    "ability", "work", "job", "team", "year", "knowledge", "understanding",
    "familiarity", "bonus", "environment", "solution", "application",
    "skill", "proficiency", "expertise", "background", "responsibility",
    "strong", "good", "excellent", "plus", "preferred", "required",
    "minimum", "ideally", "ideally", "related", "relevant", "various",
    "following", "including", "etc", "eg", "ie",
}

# ─── Separator pattern for pre-processing ────────────────────────────────────
# Splits "Docker, Kubernetes, and AWS" → ["Docker", "Kubernetes", "AWS"]
_LIST_SPLIT_RE = re.compile(r'[,;|•\n]|\band\b', re.IGNORECASE)


def _preprocess_text(text):
    """
    Split list-like text on commas/semicolons/bullets so that
    'Docker, Kubernetes, AWS' doesn't get captured as one noun chunk.
    Returns the original text (unchanged for NLP) and a list of individual tokens.
    """
    parts = [p.strip() for p in _LIST_SPLIT_RE.split(text) if p.strip()]
    return parts


def normalize_keyword(kw):
    """
    Canonicalize a keyword string to its standard display form.

    Order of precedence:
    1. SYNONYM_MAP (exact lower-case lookup) → highest priority
    2. Skills DB (case-insensitive match)
    3. Short ALL-CAPS acronym heuristic (≤4 alpha chars)
    4. Title-case fallback

    Critically, SYNONYM_MAP is checked FIRST so that slash-terms like
    'ci/cd' are returned as 'CI/CD' and NOT as 'Ci/Cd' from .title().
    """
    if not kw:
        return kw
    kw_clean = kw.strip()
    kw_lower = kw_clean.lower()

    # 1. Synonym map (handles "ci/cd", "scikit-learn", "rest api", …)
    if kw_lower in SYNONYM_MAP:
        return SYNONYM_MAP[kw_lower]

    # 2. Skills DB (returns original casing from the database)
    for _cat, skills in SKILLS_DATABASE.items():
        for skill in skills:
            if skill.lower() == kw_lower:
                return skill

    # 3. Short acronyms → ALL CAPS (e.g. "sql", "css", "html")
    if len(kw_clean) <= 4 and kw_clean.replace('-', '').replace('/', '').isalpha():
        return kw_clean.upper()

    # 4. Title-case fallback
    return kw_clean.title()


def get_skill_weight(keyword):
    """
    Returns skill weight: 1.0 for soft skills, 2.0 for hard/technical skills.
    """
    if keyword.lower() in SOFT_SKILLS:
        return 1.0
    return 2.0


def _is_noise(kw_lower):
    """Return True if the keyword is a noise/job-title/generic phrase.

    Handles:
    - Single-word noise (e.g. 'engineer', 'candidate')
    - Multi-word phrases ending in a noise word (e.g. 'Python Backend Engineer')
    - Phrases that contain a comma (comma-list fragments that slipped through)
    """
    if len(kw_lower) <= 1:
        return True
    if ',' in kw_lower:
        return True
    if kw_lower in NOISE_WORDS:
        return True
    # Block multi-word phrases whose LAST word is a noise word
    # e.g. 'python backend engineer' → last word 'engineer' is noise
    last_word = kw_lower.split()[-1]
    if last_word in NOISE_WORDS:
        return True
    return False


def _remove_subset_duplicates(keyword_set):
    """
    Post-extraction deduplication.

    If both 'CI' and 'CI/CD' are extracted, drop 'CI' because 'CI/CD'
    is the more specific canonical form.  Likewise drops any keyword
    whose lower-case form is a WHOLE-WORD substring of a longer keyword.

    Algorithm: for each keyword A, if there exists another keyword B
    (A != B) such that A.lower() appears as a word inside B.lower(),
    discard A.
    """
    canonical = sorted(keyword_set, key=len, reverse=True)  # longest first
    keep = []
    for kw in canonical:
        kw_lower = kw.lower()
        # Check if this keyword is wholly contained in any already-kept longer one
        dominated = any(
            kw_lower != longer.lower() and
            re.search(r'\b' + re.escape(kw_lower) + r'\b', longer.lower())
            for longer in keep
        )
        if not dominated:
            keep.append(kw)
    return set(keep)


def extract_keywords_nlp(text):
    """
    Extract normalized, deduplicated skill keywords from text.

    Pipeline:
    1. Pre-process: split on list separators so comma-lists don't form
       compound noun chunks.
    2. Skills DB regex match (word-boundary, case-insensitive).
    3. SYNONYM_MAP key match.
    4. spaCy NER (ORG, PRODUCT entities).
    5. spaCy noun-chunks filtered through NOISE_WORDS.
    6. Normalize each candidate via normalize_keyword().
    7. Post-dedup: remove subset forms.

    Returns:
        list[str]: Sorted, deduplicated canonical keyword strings.
    """
    if not text:
        return []

    nlp = get_spacy_nlp()
    text_lower = text.lower()
    extracted = set()

    # ── Step 1: Skills DB – regex word-boundary match ────────────────────────
    for _cat, skills in SKILLS_DATABASE.items():
        for skill in skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                extracted.add(normalize_keyword(skill))

    # ── Step 2: SYNONYM_MAP key match ────────────────────────────────────────
    for syn_key, canonical in SYNONYM_MAP.items():
        pattern = r'\b' + re.escape(syn_key) + r'\b'
        if re.search(pattern, text_lower):
            extracted.add(canonical)

    # ── Step 3 & 4: spaCy NLP on pre-split SEGMENTS (if available) ───────────
    if nlp is not None:
        segments = _preprocess_text(text)
        for segment in segments:
            seg_doc = nlp(segment)

            # Named entities
            for ent in seg_doc.ents:
                if ent.label_ in {"ORG", "PRODUCT", "WORK_OF_ART"}:
                    clean_ent = ent.text.strip()
                    ent_lower = clean_ent.lower()
                    if (len(clean_ent) > 1
                            and not ent.root.is_stop
                            and not ent.root.is_punct
                            and not _is_noise(ent_lower)):
                        extracted.add(normalize_keyword(clean_ent))

            # Noun chunks — use token.TEXT (not lemma) for proper nouns
            # so 'Kubernetes' stays 'Kubernetes', not 'Kubernete'
            for chunk in seg_doc.noun_chunks:
                chunk_words = [
                    token.text.lower()         # ← text, not lemma_
                    for token in chunk
                    if not token.is_stop and not token.is_punct and token.is_alpha
                ]
                if 1 <= len(chunk_words) <= 3:
                    chunk_str = " ".join(chunk_words)
                    if (len(chunk_str) > 2
                            and not _is_noise(chunk_str)):
                        normalized = normalize_keyword(chunk_str)
                        # Only keep if it resolves to a known synonym or skills DB entry
                        norm_lower = normalized.lower()
                        is_known = (
                            norm_lower in SYNONYM_MAP
                            or any(
                                skill.lower() == norm_lower
                                for skills in SKILLS_DATABASE.values()
                                for skill in skills
                            )
                        )
                        if is_known:
                            extracted.add(normalized)

    # ── Step 6: Post-dedup — remove subset forms ─────────────────────────────
    extracted = _remove_subset_duplicates(extracted)

    return sorted(list(extracted))


def calculate_weighted_match(resume_keywords, jd_keywords):
    """
    Calculate weighted keyword match percentage and matched/missing lists.

    Hard skills (technical) = 2.0x weight
    Soft skills             = 1.0x weight

    Matching is case-insensitive on canonical forms so 'Python' == 'python'.

    Returns:
        dict: {
            'matched': list of matched canonical keywords,
            'missing': list of missing canonical keywords,
            'match_percentage': float (0.0–100.0),
            'total_jd_weight': float,
            'matched_weight': float
        }
    """
    # Normalize every keyword to its canonical form
    resume_set = {normalize_keyword(k) for k in resume_keywords}
    jd_set     = {normalize_keyword(k) for k in jd_keywords}

    # Build lower-case → canonical maps for reliable intersection
    resume_map = {k.lower(): k for k in resume_set}
    jd_map     = {k.lower(): k for k in jd_set}

    matched_lower = set(resume_map.keys()) & set(jd_map.keys())
    missing_lower = set(jd_map.keys()) - matched_lower

    matched = sorted([jd_map[k] for k in matched_lower])
    missing = sorted([jd_map[k] for k in missing_lower])

    total_jd_weight  = sum(get_skill_weight(k) for k in jd_set)
    matched_weight   = sum(get_skill_weight(k) for k in matched)

    match_percentage = (
        round((matched_weight / total_jd_weight) * 100, 1)
        if total_jd_weight > 0 else 0.0
    )

    return {
        'matched':          matched,
        'missing':          missing,
        'match_percentage': match_percentage,
        'total_jd_weight':  total_jd_weight,
        'matched_weight':   matched_weight,
    }
