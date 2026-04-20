"""
=============================================================
 SMART RESUME ANALYZER — JOB MATCHING ENGINE
=============================================================
 
"""

import re
from typing import List, Dict, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from utils.skill_extractor import extract_all_skills, clean_text, ALL_SKILLS


# ─────────────────────────────────────────────────────────────
# JOB ROLE PROFILES
# ─────────────────────────────────────────────────────────────
# Curated skill sets for common roles.
# Used when no job description is provided — we match against
# these profiles to suggest the best-fit role.

JOB_ROLE_PROFILES: Dict[str, Dict] = {
    "backend_engineer": {
        "title": "Backend Engineer",
        "required_skills": ["python", "java", "go", "nodejs", "rest api", "sql",
                           "postgresql", "mongodb", "docker", "git"],
        "nice_to_have": ["kubernetes", "redis", "kafka", "microservices", "aws"],
        "weight": 1.0,
    },
    "frontend_engineer": {
        "title": "Frontend Engineer",
        "required_skills": ["javascript", "typescript", "react", "html", "css",
                           "git", "rest api"],
        "nice_to_have": ["nextjs", "vue", "angular", "webpack", "figma", "testing"],
        "weight": 1.0,
    },
    "fullstack_engineer": {
        "title": "Full Stack Engineer",
        "required_skills": ["javascript", "python", "react", "nodejs", "sql",
                           "mongodb", "git", "rest api", "docker"],
        "nice_to_have": ["typescript", "aws", "redis", "graphql", "ci/cd"],
        "weight": 1.0,
    },
    "data_scientist": {
        "title": "Data Scientist",
        "required_skills": ["python", "machine learning", "pandas", "numpy",
                           "scikit-learn", "sql", "statistics"],
        "nice_to_have": ["deep learning", "tensorflow", "pytorch", "spark",
                        "tableau", "power bi", "r"],
        "weight": 1.0,
    },
    "ml_engineer": {
        "title": "ML Engineer",
        "required_skills": ["python", "machine learning", "deep learning",
                           "tensorflow", "pytorch", "docker", "aws", "mlflow"],
        "nice_to_have": ["kubernetes", "spark", "kafka", "cuda", "onnx",
                        "hugging face", "vector database"],
        "weight": 1.0,
    },
    "devops_engineer": {
        "title": "DevOps / Cloud Engineer",
        "required_skills": ["docker", "kubernetes", "aws", "terraform", "linux",
                           "ci/cd", "git", "jenkins", "bash"],
        "nice_to_have": ["ansible", "helm", "prometheus", "grafana", "azure", "gcp"],
        "weight": 1.0,
    },
    "data_engineer": {
        "title": "Data Engineer",
        "required_skills": ["python", "sql", "spark", "kafka", "airflow",
                           "aws", "postgresql", "bigquery"],
        "nice_to_have": ["dbt", "snowflake", "databricks", "docker", "kubernetes"],
        "weight": 1.0,
    },
}


# ─────────────────────────────────────────────────────────────
# ALGORITHM 1: JACCARD SIMILARITY
# ─────────────────────────────────────────────────────────────

def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


# ─────────────────────────────────────────────────────────────
# ALGORITHM 2: TF-IDF COSINE SIMILARITY
# ─────────────────────────────────────────────────────────────

def tfidf_cosine_similarity(text_a: str, text_b: str) -> float:
  
    if not text_a.strip() or not text_b.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',  # ignore "the", "and", etc.
            ngram_range=(1, 2),    # include 1-word and 2-word phrases
            min_df=1,
            max_features=5000,
        )
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(score)
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────
# SKILL GAP ANALYSIS
# ─────────────────────────────────────────────────────────────

def analyze_skill_gap(
    resume_skills: Set[str],
    jd_skills: Set[str]
) -> Dict:
   
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills
    
    return {
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "extra_skills": sorted(extra),
        "match_count": len(matched),
        "total_jd_skills": len(jd_skills),
    }


# ─────────────────────────────────────────────────────────────
# SUGGESTIONS ENGINE
# ─────────────────────────────────────────────────────────────

SUGGESTION_TEMPLATES = {
    "missing_core": (
        "Add '{skill}' to your skills section. This is listed as a core requirement "
        "in the job description and will directly improve your ATS match score."
    ),
    "missing_cloud": (
        "The job requires cloud experience ('{skill}'). If you've used it even "
        "briefly (e.g., in a project or course), add it with context like "
        "'Deployed application on {skill}'."
    ),
    "missing_framework": (
        "'{skill}' is expected. If you know similar frameworks, mention transferable "
        "experience. E.g., 'Familiar with {skill} — experienced with [similar tech]'."
    ),
    "low_score": (
        "Your overall match is below 50%. Rewrite your resume bullets to mirror the "
        "exact language in the job description — ATS systems do exact-phrase matching."
    ),
    "medium_score": (
        "You're at a good baseline. Quantify your achievements: "
        "'Improved API response time by 40%' beats 'Worked on APIs'."
    ),
    "high_score": (
        "Strong match! Focus on your intro/summary section — make it a "
        "2-3 sentence pitch that directly mirrors the job title and key requirements."
    ),
    "no_github": (
        "Add a GitHub profile link. Recruiters in tech always check GitHub — "
        "even 2-3 public projects significantly boost your profile."
    ),
    "no_quantification": (
        "None of your bullet points contain numbers. Quantify impact wherever "
        "possible: team size, % improvement, users served, systems scaled."
    ),
    "experience_gap": (
        "The role likely expects {years}+ years of experience. "
        "Emphasize project complexity and scope over tenure."
    ),
}

CLOUD_SKILLS = {"aws", "azure", "gcp", "docker", "kubernetes", "terraform"}
FRAMEWORK_SKILLS = {"react", "angular", "vue", "django", "flask", "fastapi",
                    "spring", "nodejs", "nextjs"}


def generate_suggestions(
    resume_text: str,
    resume_skills: Set[str],
    skill_gap: Dict,
    match_score: float,
    contact_info: Dict,
    years_exp: int,
) -> List[str]:
    
    suggestions = []
    
    # 1. Missing skills — top 5 most impactful
    missing = skill_gap.get("missing_skills", [])
    for skill in missing[:5]:
        if skill in CLOUD_SKILLS:
            suggestions.append(SUGGESTION_TEMPLATES["missing_cloud"].format(skill=skill))
        elif skill in FRAMEWORK_SKILLS:
            suggestions.append(SUGGESTION_TEMPLATES["missing_framework"].format(skill=skill))
        else:
            suggestions.append(SUGGESTION_TEMPLATES["missing_core"].format(skill=skill))
    
    # 2. Score-based advice
    if match_score < 0.40:
        suggestions.append(SUGGESTION_TEMPLATES["low_score"])
    elif match_score < 0.70:
        suggestions.append(SUGGESTION_TEMPLATES["medium_score"])
    else:
        suggestions.append(SUGGESTION_TEMPLATES["high_score"])
    
    # 3. Missing GitHub profile
    if "github" not in contact_info:
        suggestions.append(SUGGESTION_TEMPLATES["no_github"])
    
    # 4. Check for numbers/quantification in resume
    has_numbers = bool(re.search(r'\d+[%x]|\d+\+?\s*(users|clients|team|projects|systems|ms|seconds|hours)', resume_text, re.IGNORECASE))
    if not has_numbers:
        suggestions.append(SUGGESTION_TEMPLATES["no_quantification"])
    
    return suggestions


# ─────────────────────────────────────────────────────────────
# ROLE MATCHING (no JD provided)
# ─────────────────────────────────────────────────────────────

def match_job_roles(resume_skills: Set[str]) -> List[Dict]:
    """
    When no JD is given, match resume against all our role profiles.
    Returns ranked list of best-fitting roles.
    
    """
    role_scores = []
    
    for role_key, profile in JOB_ROLE_PROFILES.items():
        required = set(profile["required_skills"])
        nice = set(profile.get("nice_to_have", []))
        
        # Weighted match
        required_matched = len(resume_skills & required)
        nice_matched = len(resume_skills & nice)
        
        required_score = required_matched / len(required) if required else 0
        nice_score = nice_matched / len(nice) if nice else 0
        
        # Blend: required skills count 70%, nice-to-have 30%
        final_score = (required_score * 0.7 + nice_score * 0.3) * 100
        
        role_scores.append({
            "role": profile["title"],
            "match_percentage": round(final_score, 1),
            "matched_required": sorted(resume_skills & required),
            "missing_required": sorted(required - resume_skills),
        })
    
    # Sort by score descending
    role_scores.sort(key=lambda x: x["match_percentage"], reverse=True)
    return role_scores[:5]  # top 5


# ─────────────────────────────────────────────────────────────
# MAIN MATCHING PIPELINE
# ─────────────────────────────────────────────────────────────

def match_resume_to_jd(
    resume_text: str,
    job_description: str,
    resume_analysis: Dict,
) -> Dict:
    """
    Full matching pipeline:
    1. Extract skills from JD
    2. Compute Jaccard + TF-IDF scores
    3. Compute skill gap
    4. Generate suggestions
    5. Return complete analysis
    """
    # Extract skills from JD
    jd_analysis = extract_all_skills(job_description)
    jd_skills = set(jd_analysis["all_skills"])
    resume_skills = set(resume_analysis["all_skills"])
    
    # ALGORITHM 1: Jaccard on skill sets
    jaccard_score = jaccard_similarity(resume_skills, jd_skills)
    
    # ALGORITHM 2: TF-IDF on full texts
    tfidf_score = tfidf_cosine_similarity(
        clean_text(resume_text),
        clean_text(job_description)
    )
    
    # BLENDED SCORE: 70% TF-IDF + 30% Jaccard
    # TF-IDF weighted higher because it captures context and phrasing
    blended_score = (tfidf_score * 0.7) + (jaccard_score * 0.3)
    match_percentage = round(blended_score * 100, 1)
    
    # Skill gap
    gap = analyze_skill_gap(resume_skills, jd_skills)
    
    # Suggestions
    suggestions = generate_suggestions(
        resume_text=resume_text,
        resume_skills=resume_skills,
        skill_gap=gap,
        match_score=blended_score,
        contact_info=resume_analysis.get("contact_info", {}),
        years_exp=resume_analysis.get("estimated_experience_years", 0),
    )
    
    # Risk assessment
    if match_percentage >= 75:
        recommendation = "Strong Match — Apply confidently"
        recommendation_level = "strong"
    elif match_percentage >= 50:
        recommendation = "Good Match — Apply with tailored resume"
        recommendation_level = "good"
    elif match_percentage >= 30:
        recommendation = "Partial Match — Address skill gaps before applying"
        recommendation_level = "partial"
    else:
        recommendation = "Low Match — Significant upskilling needed"
        recommendation_level = "low"
    
    return {
        "match_percentage": match_percentage,
        "jaccard_score": round(jaccard_score * 100, 1),
        "tfidf_score": round(tfidf_score * 100, 1),
        "recommendation": recommendation,
        "recommendation_level": recommendation_level,
        "skill_gap": gap,
        "jd_skills_extracted": sorted(jd_skills),
        "suggestions": suggestions,
        "scoring_breakdown": {
            "algorithm": "70% TF-IDF Cosine + 30% Jaccard Similarity",
            "tfidf_weight": 0.7,
            "jaccard_weight": 0.3,
        }
    }