from typing import List
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from matcher import extract_text, rank_resumes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/match")
async def match(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    resumes, skipped = [], []

    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            skipped.append({"file": f.filename, "reason": "not a PDF"})
            continue
        try:
            text = extract_text(await f.read())
        except Exception:
            skipped.append({"file": f.filename, "reason": "could not read PDF"})
            continue
        if not text:
            skipped.append({"file": f.filename, "reason": "no text found (scanned image?)"})
            continue
        resumes.append((f.filename, text))

    if not resumes:
        raise HTTPException(status_code=400, detail="No readable PDF resumes uploaded")

    output = rank_resumes(job_description, resumes)

    job = models.Job(
        title=job_description.strip()[:60],
        description=job_description,
        required_skills=output["required_skills"],
    )
    db.add(job)
    db.flush()

    text_by_name = dict(resumes)
    for r in output["results"]:
        resume = models.Resume(
            job_id=job.id,
            file_name=r["file"],
            extracted_text=text_by_name[r["file"]],
        )
        db.add(resume)
        db.flush()
        db.add(models.Result(
            job_id=job.id,
            resume_id=resume.id,
            final_score=r["final_score"],
            meaning_score=r["meaning_score"],
            skill_score=r["skill_score"],
            matched_skills=r["matched_skills"],
            missing_skills=r["missing_skills"],
        ))
    db.commit()

    output["job_id"] = job.id
    output["skipped"] = skipped
    return output


@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).order_by(models.Job.id.desc()).limit(50).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "created_at": j.created_at,
            "required_skills": j.required_skills,
        }
        for j in jobs
    ]


@app.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = (
        db.query(models.Result, models.Resume)
        .join(models.Resume, models.Result.resume_id == models.Resume.id)
        .filter(models.Result.job_id == job_id)
        .order_by(models.Result.final_score.desc())
        .all()
    )
    return {
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "required_skills": job.required_skills,
        "results": [
            {
                "file": resume.file_name,
                "final_score": r.final_score,
                "meaning_score": r.meaning_score,
                "skill_score": r.skill_score,
                "matched_skills": r.matched_skills,
                "missing_skills": r.missing_skills,
            }
            for r, resume in rows
        ],
    }