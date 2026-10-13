import glob
import re
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

JOB_DESCRIPTION = """We are hiring a Python backend developer for an AI team.
Required: Python, FastAPI, MySQL, machine learning with scikit-learn,
and experience deploying services with Docker."""

# skill name -> list of ways it can be written
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


def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


def find_skills(text):
    text = text.lower()
    found = set()
    for skill, variants in SKILLS.items():
        for v in variants:
            pattern = r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])"
            if re.search(pattern, text):
                found.add(skill)
                break
    return found


model = SentenceTransformer("all-MiniLM-L6-v2")

files = sorted(glob.glob("resume_*.pdf"))
texts = [extract_text(f) for f in files]

job_vector = model.encode([JOB_DESCRIPTION])
resume_vectors = model.encode(texts)
embed_scores = cosine_similarity(job_vector, resume_vectors)[0]

required = find_skills(JOB_DESCRIPTION)
print("Required skills:", ", ".join(sorted(required)))

results = []
for name, text, embed in zip(files, texts, embed_scores):
    have = find_skills(text)
    matched = required & have
    missing = required - have
    skill_score = len(matched) / len(required) if required else 0
    final = 0.6 * embed + 0.4 * skill_score
    results.append((name, final, embed, skill_score, matched, missing))

results.sort(key=lambda r: r[1], reverse=True)

print("\nRanking:")
for i, (name, final, embed, skill, matched, missing) in enumerate(results, 1):
    print(f"\n{i}. {name}  ->  FINAL {final * 100:.1f}%")
    print(f"   meaning score: {embed * 100:.1f}%   skill score: {skill * 100:.1f}%")
    print(f"   matched: {', '.join(sorted(matched)) or 'none'}")
    print(f"   missing: {', '.join(sorted(missing)) or 'none'}")