# ExamVault

**ExamVault** is an AI-powered platform for career intelligence, skill gap analysis, personalized course recommendations, and collaborative exam paper sharing. Built with Django, it leverages advanced NLP and search APIs to help users upskill, find jobs, and access or contribute academic resources.

---

## 🚀 Features

- **AI Skill Gap Analysis:**  
  Upload your resume or paste text to detect your skills using semantic search (Sentence Transformers + FAISS).

- **Personalized Course Recommendations:**  
  Get the best online courses (Udemy, Coursera, edX, YouTube, etc.) to close your skill gaps, powered by Google Search (SerpAPI) and a curated static database.

- **Job Recommender:**  
  Discover jobs that match your skills and see how well you fit each role.

- **Exam Paper Sharing:**  
  Upload and download previous years’ exam papers to help the academic community.

- **Modern UI:**  
  Responsive, clean, and user-friendly interface with clear navigation and actionable insights.

---

## 🏗️ Project Structure

```
FSD_project/
│
├── examvault/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── media/                # Uploaded files (resumes, exam papers)
│   └── recommender/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── courses_db.py     # Static course database
│       ├── job_skills.py     # Job roles and required skills
│       ├── models.py
│       ├── skill_bank.py     # List of all skills
│       ├── skills_DB.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py          # Core logic for recommendations
│       └── templates/
│           ├── base_new.html
│           ├── jobs.html
│           ├── results.html
│           └── resume_rd.html
│
├── website/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py             # ExamPaper and Resume models
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       ├── base.html
│       ├── home.html
│       ├── login.html
│       ├── signup.html
│       └── ... (other UI templates)
│
├── manage.py
├── requirements.txt
└── .gitignore
```

---

## 🧑‍💻 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ExamVault.git
cd ExamVault
```

### 2. Set Up Virtual Environment

```bash
python -m venv env
env\Scripts\activate   # On Windows
# or
source env/bin/activate  # On Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

- Set your SerpAPI key in `examvault/recommender/views.py` (`API_KEY` variable).
- Ensure `media/` directory exists for uploads.

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

### 7. Access the App

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📝 Usage

- **Skill Gap & Course Recommender:**  
  Go to "Course Recommender", upload your resume or paste your skills, select a job role, and get personalized recommendations.

- **Job Recommender:**  
  Find jobs matching your skills and see a similarity score for each.

- **Exam Papers:**  
  Upload or download previous years’ exam papers to help yourself and others.

---

## 🛠️ Tech Stack

- **Backend:** Django, Python
- **AI/NLP:** Sentence Transformers, FAISS, scikit-learn
- **Search API:** SerpAPI (Google Search)
- **Frontend:** HTML, CSS (custom, responsive), Django Templates
- **Database:** SQLite (default, can be changed)
- **PDF Parsing:** PyPDF2

---

## 📂 Key Files

- `recommender/views.py` — Core logic for skill extraction, course/job recommendations.
- `recommender/courses_db.py` — Static course database (fallback).
- `website/models.py` — Models for ExamPaper and Resume uploads.
- `requirements.txt` — All dependencies.

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
Please open an issue to discuss your ideas or report bugs.

---

## 📄 License

[MIT License](LICENSE) (add your license file if needed)

---

## 🙏 Acknowledgements

- [Sentence Transformers](https://www.sbert.net/)
- [SerpAPI](https://serpapi.com/)
- [Django](https://www.djangoproject.com/)
- [PyPDF2](https://pypdf2.readthedocs.io/)

---

**Empowering learners and job seekers with AI. Knowledge grows when shared!**
