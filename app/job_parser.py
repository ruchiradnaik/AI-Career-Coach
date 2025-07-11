import spacy
from spacy.cli import download
import re

def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "power bi", "tableau",
    "tensorflow", "pytorch", "nlp", "opencv", "machine learning",
    "deep learning", "data analysis", "data science", "html", "css",
    "javascript", "flask", "django", "aws", "azure", "git"
]

def extract_keywords_from_jd(jd_text):
    jd_text = jd_text.lower()
    doc = nlp(jd_text)

    tokens = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    chunks = [chunk.text.lower() for chunk in doc.noun_chunks]

    keywords = set(tokens + chunks)

    found_skills = []
    for skill in COMMON_SKILLS:
        if skill.lower() in keywords or re.search(rf"\b{re.escape(skill)}\b", jd_text):
            found_skills.append(skill.lower())

    return list(set(found_skills))

def compare_resume_to_jd(resume_skills, jd_skills):
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
