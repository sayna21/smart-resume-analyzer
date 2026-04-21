# 🚀 Smart Resume Analyzer

## 📌 Overview
Smart Resume Analyzer is an AI-powered backend system that analyzes resumes (PDF format) and extracts key information such as skills, experience, and job role fit.

It also compares resumes with job descriptions using machine learning techniques to provide **match scores and improvement suggestions**.

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
|----------|--------|--------|
| TF-IDF + Cosine Similarity | Semantic matching | 70% |
| Jaccard Similarity | Skill overlap | 30% |
| spaCy NLP | Entity & skill extraction | Supplementary |

---

## 🛠️ Tech Stack
- **Backend:** FastAPI  
- **Language:** Python  
- **NLP:** spaCy  
- **ML:** Scikit-learn  
- **PDF Processing:** pdfplumber  
- **Database:** MongoDB (optional)  
- **Server:** Uvicorn  

---

## 📁 Project Structure
resume_analyzer/
│
├── app/
│ ├── init.py
│ └── main.py
│
├── utils/
│ ├── init.py
│ ├── skill_extractor.py
│ ├── job_matcher.py
│ ├── pdf_reader.py
│ └── database.py
│
├── requirements.txt
├── .env.example
├── .gitignore
├── frontend.html
└── README.md


---

## ⚙️ Installation & Setup

### 1️⃣ Clone repository
```bash
git clone https://github.com/sayna21/smart-resume-analyzer.git
cd smart-resume-analyzer

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Install spaCy model
python -m spacy download en_core_web_sm

5️⃣ Run server
uvicorn app.main:app --reload

🖥️ Frontend UI
Open frontend.html in browser
Ensure backend is running on http://127.0.0.1:8000

🌐 API Endpoints
🔹 Analyze Resume

POST /analyze
Upload PDF → returns extracted skills & analysis

🔹 Match Resume with JD

POST /analyze/match
Upload PDF + job description → returns match score

🔹 Other APIs
GET /roles → supported roles
GET /analysis/{analysis_id} → fetch result
GET /health → server status
GET /stats → analytics

🚀 Future Improvements
🌐 React Frontend
☁️ Deployment (Render / AWS)
🤖 Advanced ML models
📊 Dashboard analytics


💼 Use Cases
Students preparing for internships
Resume screening automation
HR tech platforms

📖 API Docs

👉 http://localhost:8000/docs

👨‍💻 Author

Sayna Kumari