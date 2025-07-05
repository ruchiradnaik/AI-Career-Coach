def calculate_resume_score(resume_skills, jd_skills):
    resume_set = set([s.lower() for s in resume_skills])
    jd_set = set([s.lower() for s in jd_skills])

    matched = resume_set & jd_set
    missing = jd_set - resume_set

    score = int((len(matched) / len(jd_set)) * 100) if jd_set else 0

    if score >= 80:
        fit_level = "High"
    elif score >= 50:
        fit_level = "Medium"
    else:
        fit_level = "Low"

    return {
        "score": score,
        "fit_level": fit_level,
        "matched": list(matched),
        "missing": list(missing)
    }
