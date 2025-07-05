import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Same skills list as resume_parser.py
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "power bi", "tableau",
    "tensorflow", "pytorch", "nlp", "opencv", "machine learning",
    "deep learning", "data analysis", "data science", "html", "css",
    "javascript", "flask", "django", "aws", "azure", "git"
]

def extract_keywords_from_jd(jd_text):
    """
    Extracts skill-related keywords from a job description.
    """
    jd_text = jd_text.lower()
    doc = nlp(jd_text)

    tokens = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    chunks = [chunk.text.lower() for chunk in doc.noun_chunks]

    # Combine token and phrase-level matches
    keywords = set(tokens + chunks)

    found_skills = []
    for skill in COMMON_SKILLS:
        if skill.lower() in keywords or re.search(rf"\b{re.escape(skill)}\b", jd_text):
            found_skills.append(skill.lower())

    return list(set(found_skills))

def compare_resume_to_jd(resume_skills, jd_skills):
    """
    Compare skills from resume and job description.

    Args:
        resume_skills (list): Skills extracted from resume
        jd_skills (list): Skills extracted from JD

    Returns:
        dict: matched, missing, suggestions
    """
    resume_set = set([s.lower() for s in resume_skills])
    jd_set = set([s.lower() for s in jd_skills])

    matched = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))

    suggestions = []
    if missing:
        suggestions.append("You may consider learning or adding projects using: " + ", ".join(missing))

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions
    }
