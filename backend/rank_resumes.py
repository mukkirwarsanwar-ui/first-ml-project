import glob
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

JOB_DESCRIPTION = """We are hiring a Python backend developer for an AI team.
Required: Python, FastAPI, MySQL, machine learning with scikit-learn,
and experience deploying services with Docker."""


def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


model = SentenceTransformer("all-MiniLM-L6-v2")

# 1. Read every resume PDF in this folder
files = sorted(glob.glob("resume_*.pdf"))
texts = [extract_text(f) for f in files]

# 2. Convert job and resumes to embeddings
job_vector = model.encode([JOB_DESCRIPTION])
resume_vectors = model.encode(texts)

# 3. Score each resume against the job
scores = cosine_similarity(job_vector, resume_vectors)[0]

# 4. Rank from best to worst
ranking = sorted(zip(files, scores), key=lambda x: x[1], reverse=True)

print("\nRanking:")
for position, (name, score) in enumerate(ranking, start=1):
    print(f"{position}. {name:<22} {score * 100:.1f}%")