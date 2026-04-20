"""
=============================================================
 SMART RESUME ANALYZER — NLP SKILL EXTRACTOR
=============================================================

"""

import re
import spacy
from typing import List, Set, Dict

# ─────────────────────────────────────────────────────────────
# MASTER SKILL TAXONOMY
# ─────────────────────────────────────────────────────────────
# Organized by category so we can return structured results.
# In production: load this from a database and keep it updated.

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "dart", "perl",
        "bash", "shell", "powershell", "sql", "plsql", "cobol", "fortran"
    ],
    "web_frameworks": [
        "react", "angular", "vue", "nextjs", "nuxt", "svelte", "django", "flask",
        "fastapi", "spring", "springboot", "express", "nodejs", "nestjs", "rails",
        "laravel", "asp.net", "blazor", "gatsby", "remix", "htmx"
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
        "dynamodb", "sqlite", "oracle", "mssql", "mariadb", "neo4j", "firebase",
        "supabase", "cockroachdb", "influxdb", "clickhouse", "bigquery", "snowflake"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "circleci", "gitlab ci", "prometheus", "grafana",
        "nginx", "apache", "linux", "unix", "helm", "istio", "vault", "consul"
    ],
    "ai_ml": [
        "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
        "pytorch", "keras", "scikit-learn", "pandas", "numpy", "hugging face",
        "transformers", "bert", "gpt", "llm", "rag", "langchain", "openai",
        "reinforcement learning", "xgboost", "lightgbm", "opencv", "yolo",
        "stable diffusion", "vector database", "pinecone", "weaviate", "mlflow"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving", "agile",
        "scrum", "kanban", "project management", "mentoring", "collaboration",
        "critical thinking", "time management", "presentation", "negotiation"
    ],
    "tools": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
        "figma", "postman", "vscode", "intellij", "vim", "excel", "tableau",
        "power bi", "looker", "dbt", "airflow", "spark", "kafka", "rabbitmq"
    ],
    "methodologies": [
        "rest api", "graphql", "grpc", "microservices", "event driven", "tdd",
        "bdd", "ci/cd", "devops", "devsecops", "system design", "design patterns",
        "clean code", "solid principles", "oauth", "jwt", "websocket"
    ]
}

# Flatten all skills into a single set for fast lookup
ALL_SKILLS: Set[str] = {
    skill.lower()
    for skills in SKILL_TAXONOMY.values()
    for skill in skills
}

# ─────────────────────────────────────────────────────────────
# INITIALIZE spaCy
# ─────────────────────────────────────────────────────────────
# We use a blank English model (no download needed).
# If en_core_web_sm is installed, it gives better NER and POS.
# The blank model still gives us tokenization and noun chunks.

try:
    nlp = spacy.load("en_core_web_sm")
    NLP_MODEL = "en_core_web_sm (full NER + POS)"
except OSError:
    nlp = spacy.blank("en")
    # Add sentencizer so we can use noun chunks
    nlp.add_pipe("sentencizer")
    NLP_MODEL = "en_core_web_blank (keyword mode)"

print(f"  NLP model: {NLP_MODEL}")


# ─────────────────────────────────────────────────────────────
# CORE EXTRACTION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Clean raw PDF text before NLP processing.
    PDF extraction often has weird spacing, bullets, line breaks.
    """
    # Replace bullets and special chars with space
    text = re.sub(r'[•·▪▸►●◦◆★]', ' ', text)
    # Collapse multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove non-ASCII but keep common chars like / + # @
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()


def extract_skills_by_keyword(text: str) -> Dict[str, List[str]]:
    """
    STRATEGY 1: Keyword matching
    
    INTERVIEW EXPLANATION:
    We look for every skill from our taxonomy in the resume text.
    We check multi-word skills (e.g. "machine learning") by sliding a
    window across the text. This is O(n * k) where n = text length,
    k = number of skills — fast enough for resume-length documents.
    
    We also handle common aliases:
    - "node" → matches "nodejs"
    - "react.js" → matches "react"
    - "k8s" → matches "kubernetes"
    """
    text_lower = text.lower()
    
    # Normalize common aliases before matching
    aliases = {
        "node.js": "nodejs", "node js": "nodejs",
        "react.js": "react", "reactjs": "react",
        "vue.js": "vue", "vuejs": "vue",
        "angular.js": "angular", "angularjs": "angular",
        "next.js": "nextjs", "nuxt.js": "nuxt",
        "k8s": "kubernetes", "k8": "kubernetes",
        "tf": "tensorflow", "pytorch": "pytorch",
        "postgres": "postgresql", "mongo": "mongodb",
        "gpt-4": "gpt", "chatgpt": "gpt",
        "hf": "hugging face", "sklearn": "scikit-learn",
        "aws lambda": "aws", "aws s3": "aws", "aws ec2": "aws",
        "ml": "machine learning", "dl": "deep learning",
        "nlp": "nlp", "cv": "computer vision",
        "ci/cd": "ci/cd", "cicd": "ci/cd",
    }
    for alias, canonical in aliases.items():
        text_lower = text_lower.replace(alias, canonical)
    
    found_by_category: Dict[str, List[str]] = {cat: [] for cat in SKILL_TAXONOMY}
    
    for category, skills in SKILL_TAXONOMY.items():
        for skill in skills:
            # Use word-boundary regex for short skills to avoid partial matches
            # e.g. "r" should not match inside "framework"
            if len(skill) <= 2:
                pattern = rf'\b{re.escape(skill)}\b'
                if re.search(pattern, text_lower):
                    found_by_category[category].append(skill)
            else:
                if skill in text_lower:
                    found_by_category[category].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in found_by_category.items() if v}


def extract_skills_by_nlp(text: str) -> List[str]:
    """
    STRATEGY 2: spaCy NLP extraction
    
    """
    doc = nlp(text[:100000])  # spaCy has a text length limit
    
    candidates = set()
    
    # Extract named entities (works with full model only)
    if hasattr(doc, 'ents'):
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "GPE", "WORK_OF_ART"):
                candidates.add(ent.text.lower().strip())
    
    # Extract noun chunks (works with both models after sentencizer)
    try:
        for chunk in doc.noun_chunks:
            candidates.add(chunk.text.lower().strip())
    except Exception:
        pass
    
    # Match candidates against our skill taxonomy
    matched = []
    for candidate in candidates:
        for skill in ALL_SKILLS:
            if skill in candidate or candidate in skill:
                if skill not in matched:
                    matched.append(skill)
    
    return matched


def extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extract basic contact info using regex patterns.
    Used to validate that the uploaded file is actually a resume.
    """
    info = {}
    
    # Email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        info["email"] = email_match.group()
    
    # Phone (multiple formats)
    phone_match = re.search(
        r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text
    )
    if phone_match:
        info["phone"] = phone_match.group().strip()
    
    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    if linkedin_match:
        info["linkedin"] = linkedin_match.group()
    
    # GitHub
    github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
    if github_match:
        info["github"] = github_match.group()
    
    return info


def extract_experience_years(text: str) -> int:
    """
    Estimate years of experience mentioned in resume text.
    Looks for patterns like "5 years of experience", "3+ years", etc.
    """
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
    ]
    years_found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        years_found.extend([int(m) for m in matches])
    
    return max(years_found) if years_found else 0


# ─────────────────────────────────────────────────────────────
# MAIN EXTRACTION PIPELINE
# ─────────────────────────────────────────────────────────────

def extract_all_skills(text: str) -> Dict:
    """
    Run both NLP strategies and merge results.
    Returns structured output ready for the API response.
    """
    cleaned = clean_text(text)
    
    # Strategy 1: keyword matching (categorized)
    categorized = extract_skills_by_keyword(cleaned)
    
    # Strategy 2: NLP extraction
    nlp_skills = extract_skills_by_nlp(cleaned)
    
    # Merge: add NLP-found skills that keyword matching missed
    all_found_flat = {
        skill
        for skills in categorized.values()
        for skill in skills
    }
    additional = [s for s in nlp_skills if s not in all_found_flat]
    if additional:
        categorized["nlp_extracted"] = additional
    
    # Flat list of all skills for easy comparison
    all_skills_flat = list(all_found_flat) + additional
    
    # Extract supplementary info
    contact = extract_contact_info(cleaned)
    years_exp = extract_experience_years(cleaned)
    
    return {
        "skills_by_category": categorized,
        "all_skills": sorted(set(all_skills_flat)),
        "total_skills_found": len(set(all_skills_flat)),
        "contact_info": contact,
        "estimated_experience_years": years_exp,
        "nlp_model_used": NLP_MODEL,
    }