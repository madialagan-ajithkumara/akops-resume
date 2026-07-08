"""
JD vs CV matching -- pure local information-retrieval technique
(TF-IDF cosine similarity), no AI API needed. This is the same core
method real ATS systems and open-source resume matchers use.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .analyzer import detect_skills


def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([resume_text, jd_text])
    similarity = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
    match_percent = round(min(100, max(0, similarity * 100)))

    resume_skills = {s.lower() for s in detect_skills(resume_text)}
    jd_skills = detect_skills(jd_text)

    matched_skills = [s for s in jd_skills if s.lower() in resume_skills]
    missing_skills = [s for s in jd_skills if s.lower() not in resume_skills]

    # Blend keyword coverage into the score too, so a resume that shares the
    # JD's exact required skills scores higher than pure prose overlap alone.
    if jd_skills:
        coverage = len(matched_skills) / len(jd_skills)
        match_percent = round((match_percent * 0.5) + (coverage * 100 * 0.5))

    return {
        "match_percent": match_percent,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }
