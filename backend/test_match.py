from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

job = """We need a Python developer with experience in FastAPI,
SQL databases, and machine learning."""

resume_good = """Python developer. Built REST APIs with FastAPI,
worked with MySQL, trained ML models using scikit-learn."""

resume_bad = """Experienced chef. Managed a restaurant kitchen,
created menus, and trained culinary staff."""

vectors = model.encode([job, resume_good, resume_bad])

score_good = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
score_bad = cosine_similarity([vectors[0]], [vectors[2]])[0][0]

print(f"Good resume score: {score_good * 100:.1f}%")
print(f"Bad resume score:  {score_bad * 100:.1f}%")