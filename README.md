# 🚀 Smart Resume Analyzer
 
![Python](https://img.shields.io/badge/Python-3.10-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green) ![Railway](https://img.shields.io/badge/Deployed-Railway-purple) ![License](https://img.shields.io/badge/License-MIT-yellow)
 
## 🌐 Live Demo
 
| Service | URL |
|---------|-----|
| 🔗 Frontend | [smart-resume-analyzer frontend](https://sayna21.github.io/smart-resume-analyzer/frontend.html) |
| ⚡ API (Live) | [smart-resume-analyzer-production-6f26.up.railway.app](https://smart-resume-analyzer-production-6f26.up.railway.app) |
| 📖 API Docs | [/docs](https://smart-resume-analyzer-production-6f26.up.railway.app/docs) |
 
---
 
## 📌 Overview
 
Smart Resume Analyzer is an AI-powered backend system that analyzes resumes (PDF format) and extracts key information such as skills, experience, and job role fit.
 
It compares resumes with job descriptions using machine learning techniques to provide **match scores and improvement suggestions**.
 
---
 
## ✨ Features
 
- 📄 PDF Resume Parsing (pdfplumber)
- 🧠 Skill Extraction using NLP (spaCy + keyword matching)
- 📊 Resume–Job Matching (TF-IDF + Cosine + Jaccard)
- 📈 Match Percentage & Recommendation System
- ⚠️ Skill Gap Analysis
- 💡 Personalized Suggestions
- 🗂️ Categorized Skills (Programming, Web, Database, etc.)
- ⚡ FastAPI backend with Swagger UI
---
 
## 🧠 Algorithms Used
 
| Algorithm | Purpose | Weight |
|----------|---------|--------|
| TF-IDF + Cosine Similarity | Semantic matching | 70% |
| Jaccard Similarity | Skill overlap | 30% |
| spaCy NLP | Entity & skill extraction | Supplementary |
 
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|-------|-----------|
| Backend | FastAPI |
| Language | Python 3.10 |
| NLP | spaCy (en_core_web_sm) |
| ML | Scikit-learn |
| PDF Processing | pdfplumber |
| Database | MongoDB (optional) |
| Server | Uvicorn |
| Deployment | Railway |
| Frontend Hosting | GitHub Pages |
 
---
 
## 📁 Project Structure
 
```
smart-resume-analyzer/
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── utils/
│   ├── __init__.py
│   ├── skill_extractor.py
│   ├── job_matcher.py
│   ├── pdf_reader.py
│   └── database.py
│
├── frontend.html
├── requirements.txt
├── runtime.txt
├── Procfile
├── .env.example
├── .gitignore
└── README.md
```
 
---
 
## ⚙️ Local Setup
 
### 1. Clone the repository
```bash
git clone https://github.com/sayna21/smart-resume-analyzer.git
cd smart-resume-analyzer
```
 
### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```
 
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
 
### 4. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```
 
### 5. Run the server
```bash
uvicorn app.main:app --reload
```
 
### 6. Open frontend
Open `frontend.html` in your browser. Make sure backend is running on `http://127.0.0.1:8000`
 
---
 
## 🌐 API Endpoints
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Upload PDF → returns extracted skills & analysis |
| POST | `/analyze/match` | Upload PDF + job description → returns match score |
| GET | `/roles` | List of supported roles |
| GET | `/analysis/{id}` | Fetch a previous result by ID |
| GET | `/health` | Server health check |
| GET | `/stats` | Analytics & usage stats |
 
Full interactive docs: [https://smart-resume-analyzer-production-6f26.up.railway.app/docs](https://smart-resume-analyzer-production-6f26.up.railway.app/docs)
 
---
 
## 🚀 Deployment
 
This project is deployed using:
- **Backend:** [Railway](https://railway.app) — auto-deploys on every GitHub push
- **Frontend:** [GitHub Pages](https://pages.github.com) — serves `frontend.html` as a static site
---
 
## 💼 Use Cases
 
- Students preparing for internships
- Resume screening automation
- HR tech platforms
---
 
## 👨‍💻 Author
 
**Sayna Kumari**  
[GitHub](https://github.com/sayna21)
 