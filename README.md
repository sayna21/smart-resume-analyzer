🚀 Smart Resume Analyzer
📌 Overview

Smart Resume Analyzer is an AI-powered web backend system that analyzes resumes (PDF format) and extracts key information such as skills, experience, and job role fit. It also compares resumes with job descriptions using machine learning techniques to provide match scores and improvement suggestions.

✨ Features
📄 PDF Resume Parsing (using pdfplumber)
🧠 Skill Extraction using NLP (spaCy + keyword matching)
📊 Resume–Job Matching (TF-IDF + Cosine Similarity + Jaccard Similarity)
📈 Match Percentage & Recommendation System
⚠️ Skill Gap Analysis
💡 Personalized Suggestions for improvement
🗂️ Categorized Skills (Programming, Web, Database, etc.)
⚡ FastAPI backend with interactive Swagger UI
🧠 Algorithms Used
Algorithm	Purpose	Weight
TF-IDF + Cosine Similarity	Semantic matching of resume & job description	70%
Jaccard Similarity	Skill overlap comparison	30%
spaCy NLP	Entity & skill extraction	Supplementary
🛠️ Tech Stack
Backend: FastAPI
Language: Python
NLP: spaCy
ML: Scikit-learn
PDF Processing: pdfplumber
Database: MongoDB (optional)
Server: Uvicorn
📁 Project Structure
resume_analyzer/
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
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

⚙️ Installation & Setup
1️⃣ Clone the repository
git clone <your-repo-link>
cd resume_analyzer

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Install spaCy model
python -m spacy download en_core_web_sm

5️⃣ Run the server
uvicorn app.main:app --reload

🌐 API Endpoints
🔹 Analyze Resume

POST /analyze

Upload PDF
Returns extracted skills, categories, experience
🔹 Match Resume with Job Description

POST /analyze/match

Upload PDF + job description
Returns match score, recommendation, skill gap

🔹 Get Roles
GET /roles
Returns supported job roles

🔹 Get Analysis by ID
GET /analysis/{analysis_id}

🔹 Health Check
GET /health

🔹 Stats
GET /stats

🚀 Future Improvements
🌐 Frontend UI (React)
☁️ Deployment (Render / AWS)
🤖 Advanced ML models for better matching
📊 Dashboard analytics

💼 Use Case
Students preparing for internships
Resume screening automation
HR tech applications

👨‍💻 Author
Sayna Kumari