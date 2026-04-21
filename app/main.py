"""
=============================================================
 SMART RESUME ANALYZER — FastAPI MAIN APPLICATION
=============================================================
 
"""

import uuid
import time
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from utils.pdf_reader import (
    extract_text_from_pdf, validate_file_size, validate_file_type
)
from utils.skill_extractor import extract_all_skills
from utils.job_matcher import match_resume_to_jd, match_job_roles, JOB_ROLE_PROFILES
from utils.database import save_analysis, get_analysis, get_recent_analyses, get_stats

# ─────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Smart Resume Analyzer API",
    description="""
##  AI-Powered Resume Analysis System

Upload your resume PDF and get:
- **Skill extraction** using NLP (spaCy + keyword matching)
- **Job-role matching score** using TF-IDF Cosine + Jaccard Similarity
- **Gap analysis** showing exactly what skills are missing
- **Personalized suggestions** to improve your resume

### Algorithms Used
| Algorithm | Purpose | Weight |
|-----------|---------|--------|
| TF-IDF Cosine Similarity | Full-text semantic matching | 70% |
| Jaccard Similarity | Skill set overlap | 30% |
| spaCy NLP | Entity & noun-chunk extraction | Supplementary |

### Match Score Guide
| Score | Meaning |
|-------|---------|
| 75%+ | Strong Match — Apply confidently |
| 50-74% | Good Match — Tailor resume first |
| 30-49% | Partial Match — Address skill gaps |
| <30% | Low Match — Significant upskilling needed |
    """,
    version="1.0.0",
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def serve_frontend():
    return FileResponse("frontend.html")


# ─────────────────────────────────────────────────────────────
# ENDPOINT 1: ANALYZE RESUME ONLY
# ─────────────────────────────────────────────────────────────

@app.post("/analyze", summary="Analyze resume and extract skills")
async def analyze_resume(
    file: UploadFile = File(..., description="PDF resume file"),
):
    """
    Upload a PDF resume → extract skills, contact info, and experience.
    Also matches against all built-in job role profiles automatically.

    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())[:8].upper()  # e.g. "A3F9C12B"

    # --- Validate file ---
    try:
        file_bytes = await file.read()
        validate_file_size(file_bytes, max_mb=5)
        validate_file_type(file.filename or "file.pdf", file.content_type or "application/pdf")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # --- Extract text from PDF ---
    try:
        resume_text, page_count = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # --- NLP skill extraction ---
    analysis = extract_all_skills(resume_text)

    # --- Role matching (auto, no JD needed) ---
    resume_skills = set(analysis["all_skills"])
    role_matches = match_job_roles(resume_skills)

    # --- Build response ---
    elapsed_ms = round((time.time() - start_time) * 1000, 1)
    result = {
        "analysis_id": analysis_id,
        "filename": file.filename,
        "pages": page_count,
        "processing_time_ms": elapsed_ms,
        # Skills
        "skills_by_category": analysis["skills_by_category"],
        "all_skills": analysis["all_skills"],
        "total_skills_found": analysis["total_skills_found"],
        # Profile info
        "contact_info": analysis["contact_info"],
        "estimated_experience_years": analysis["estimated_experience_years"],
        # Role fit
        "top_role_matches": role_matches,
        "best_fit_role": role_matches[0]["role"] if role_matches else "Generalist",
        # Meta
        "nlp_model": analysis["nlp_model_used"],
        "resume_text_preview": resume_text[:300] + "..." if len(resume_text) > 300 else resume_text,
    }

    # --- Save to DB (non-blocking) ---
    await save_analysis(analysis_id, result)

    return result


# ─────────────────────────────────────────────────────────────
# ENDPOINT 2: ANALYZE + MATCH AGAINST JOB DESCRIPTION
# ─────────────────────────────────────────────────────────────

@app.post("/analyze/match", summary="Analyze resume and match against a job description")
async def analyze_and_match(
    file: UploadFile = File(..., description="PDF resume file"),
    job_description: str = Form(..., description="Paste the full job description text here"),
):
    """
    Upload resume PDF + paste job description text →
    get match %, missing skills, and personalized improvement suggestions.

    """
    start_time = time.time()
    analysis_id = str(uuid.uuid4())[:8].upper()

    if not job_description.strip() or len(job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please paste the full JD (at least 50 characters)."
        )

    # --- Validate + read file ---
    try:
        file_bytes = await file.read()
        validate_file_size(file_bytes, max_mb=5)
        validate_file_type(file.filename or "file.pdf", file.content_type or "application/pdf")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # --- Extract PDF text ---
    try:
        resume_text, page_count = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # --- NLP on resume ---
    resume_analysis = extract_all_skills(resume_text)

    # --- Match against JD ---
    match_result = match_resume_to_jd(
        resume_text=resume_text,
        job_description=job_description,
        resume_analysis=resume_analysis,
    )

    # --- Role matching too ---
    resume_skills = set(resume_analysis["all_skills"])
    role_matches = match_job_roles(resume_skills)

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    result = {
        "analysis_id": analysis_id,
        "filename": file.filename,
        "pages": page_count,
        "processing_time_ms": elapsed_ms,
        # Core match result
        "match_percentage": match_result["match_percentage"],
        "jaccard_score": match_result["jaccard_score"],
        "tfidf_score": match_result["tfidf_score"],
        "recommendation": match_result["recommendation"],
        "recommendation_level": match_result["recommendation_level"],
        "scoring_breakdown": match_result["scoring_breakdown"],
        # Skills
        "resume_skills": resume_analysis["all_skills"],
        "jd_skills_extracted": match_result["jd_skills_extracted"],
        "skills_by_category": resume_analysis["skills_by_category"],
        # Gap analysis
        "skill_gap": match_result["skill_gap"],
        # Suggestions
        "suggestions": match_result["suggestions"],
        # Profile
        "contact_info": resume_analysis["contact_info"],
        "estimated_experience_years": resume_analysis["estimated_experience_years"],
        "top_role_matches": role_matches[:3],
        # Meta
        "nlp_model": resume_analysis["nlp_model_used"],
    }

    await save_analysis(analysis_id, result)
    return result


# ─────────────────────────────────────────────────────────────
# ENDPOINT 3: LIST ALL SUPPORTED JOB ROLES
# ─────────────────────────────────────────────────────────────

@app.get("/roles", summary="List all supported job role profiles")
def list_roles():
    """
    Returns all built-in role profiles with their required and
    nice-to-have skills. Useful for showing users what roles
    the system can match against.
    """
    return {
        "total_roles": len(JOB_ROLE_PROFILES),
        "roles": [
            {
                "key": key,
                "title": profile["title"],
                "required_skills": profile["required_skills"],
                "nice_to_have": profile.get("nice_to_have", []),
                "total_skills": len(profile["required_skills"]) + len(profile.get("nice_to_have", [])),
            }
            for key, profile in JOB_ROLE_PROFILES.items()
        ]
    }


# ─────────────────────────────────────────────────────────────
# ENDPOINT 4: RETRIEVE SAVED ANALYSIS
# ─────────────────────────────────────────────────────────────

@app.get("/analysis/{analysis_id}", summary="Retrieve a saved analysis by ID")
async def get_saved_analysis(analysis_id: str):
    """
    Retrieve a previously computed analysis using its ID.
    IDs are returned in every /analyze response.
    """
    result = await get_analysis(analysis_id.upper())
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis '{analysis_id}' not found. IDs expire after 24 hours."
        )
    return result


# ─────────────────────────────────────────────────────────────
# ENDPOINT 5: HEALTH CHECK
# ─────────────────────────────────────────────────────────────

@app.get("/health", summary="Service health check")
def health():
    return {
        "status": "ok",
        "api_version": "1.0.0",
        "endpoints": ["/analyze", "/analyze/match", "/roles", "/analysis/{id}", "/stats"],
    }


# ─────────────────────────────────────────────────────────────
# ENDPOINT 6: STATS
# ─────────────────────────────────────────────────────────────

@app.get("/stats", summary="Aggregate stats across all analyses")
async def stats():
    return await get_stats()