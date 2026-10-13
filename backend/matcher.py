import io
import re
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Loaded once when the server starts, not on every request
model = SentenceTransformer("all-MiniLM-L6-v2")

SKILLS = {
    "python": ["python"],
    "fastapi": ["fastapi"],
    "mysql": ["mysql"],
    "sql": ["sql"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "machine learning": ["machine learning", "ml"],
    "docker": ["docker"],
    "git": ["git"],
    "react": ["react", "reactjs"],
    "javascript": ["javascript", "js"],
    "node.js": ["node.js", "nodejs"],
    "html": ["html"],
    "css": ["css"],
}


def extract_text(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


def find_skills(text: str) -> set:
    text = text.lower()
    found = set()
    for skill, variants in SKILLS.items():
        for v in variants:
            pattern = r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])"
            if re.search(pattern, text):
                found.add(skill)
                break
    return found


def rank_resumes(job_description: str, resumes: list) -> dict:
    """resumes is a list of (filename, text) pairs."""
    required = find_skills(job_description)
    job_vec = model.encode([job_description])
    resume_vecs = model.encode([text for _, text in resumes])
    embed_scores = cosine_similarity(job_vec, resume_vecs)[0]

    results = []
    for (name, text), embed in zip(resumes, embed_scores):
        have = find_skills(text)
        matched = required & have
        missing = required - have
        skill_score = len(matched) / len(required) if required else 0.0
        final = 0.6 * float(embed) + 0.4 * skill_score
        results.append({
            "file": name,
            "final_score": round(final * 100, 1),
            "meaning_score": round(float(embed) * 100, 1),
            "skill_score": round(skill_score * 100, 1),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
        })

    results.sort(key=lambda r: r["final_score"], reverse=True)
    return {"required_skills": sorted(required), "results": results}