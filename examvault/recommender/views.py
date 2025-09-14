from django.shortcuts import render

# Create your views here.
# recommender/views.py
import re
import io
import faiss
from django.shortcuts import render
from django.http import HttpResponse
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
from .skills_DB import ALL_SKILLS
from .job_skills import JOB_ROLE_SKILLS
from .courses_db import COURSES_DB
from django.views.decorators.csrf import csrf_exempt
from serpapi import GoogleSearch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .skill_bank import SKILL_BANK


# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')
COURSES_PER_SKILL = 6
API_KEY = "ea803f1871b8d4abfaf9ce7afcda7a3cdda175cef188a19713259fd66fad5d34"




def extract_text_from_pdf_bytes(pdf_bytes):
    text = ""
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_skills_from_resume_semantic(resume_text, top_k=3, threshold=0.35):
    skill_embeddings = model.encode(ALL_SKILLS, convert_to_numpy=True, normalize_embeddings=True)
    d = skill_embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(skill_embeddings)

    sentences = re.split(r"[.\n]", resume_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    found_skills = set()
    for sent in sentences:
        sent_emb = model.encode([sent], convert_to_numpy=True, normalize_embeddings=True)
        scores, idx = index.search(sent_emb, k=top_k)
        for i, score in enumerate(scores[0]):
            if score >= threshold:
                found_skills.add(ALL_SKILLS[idx[0][i]])
    return list(found_skills)

def fetch_courses_for_skill(skill, max_results=COURSES_PER_SKILL):
    skill_key = skill.lower()
    if skill_key in COURSES_DB:
        return COURSES_DB[skill_key][:max_results]
    return []

def rank_courses_by_similarity(resume_text, course_list):
    if not course_list:
        return []
    course_texts = [ (c.get('title','') + '. ' + (c.get('description') or '')).strip() for c in course_list ]
    emb_courses = model.encode(course_texts, convert_to_tensor=True)
    emb_resume = model.encode(resume_text, convert_to_tensor=True)

   


    sims = util.cos_sim(emb_resume, emb_courses)[0].cpu().tolist()
    for c, s in zip(course_list, sims):
        c['score'] = float(s)
    return sorted(course_list, key=lambda x: x['score'], reverse=True)

@csrf_exempt
def recommend(request):
    roles = list(JOB_ROLE_SKILLS.keys())

    if request.method == "POST":
        recommendation_type = request.POST.get("recommendation_type")
        
        
        role = request.POST.get("role")
        resume_text = request.POST.get("resume_text", "")

        if 'resume_file' in request.FILES and request.FILES['resume_file'].name != "":
            f = request.FILES['resume_file']
            resume_text = extract_text_from_pdf_bytes(f.read())
        

        resume_skills = extract_skills_from_resume_semantic(resume_text)

        if recommendation_type == "job":
            return job_listings(request, role, resume_skills)
        required = [s.lower() for s in JOB_ROLE_SKILLS[role]]
        matched = [s for s in required if s in resume_skills]
        missing = [s for s in required if s not in resume_skills]
        coverage = round(len(matched)/len(required)*100, 2)

        recommendations = []
        for skill in missing:
            courses = fetch_courses_for_skill(skill)
            ranked = rank_courses_by_similarity(resume_text + ' ' + role, courses)
            recommendations.append({'skill': skill, 'courses': ranked})
        print(recommendations)
        return render(request, "results.html", {
            "role": role,
            "coverage": coverage,
            "resume_skills": resume_skills,
            "matched": matched,
            "missing": missing,
            "recommendations": recommendations,
        })

    return render(request, "resume_rd.html", {"roles": roles})




def fetch_jobs(role, location="India", num_results=10):
    params = {
        "engine": "google_jobs",
        "q": role,
        "location": location,
        "hl": "en",
        "api_key": API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("jobs_results", [])[:num_results]

def extract_relevant_skills(job_description, skill_bank=SKILL_BANK):
    job_description_lower = job_description.lower()
    return [skill for skill in skill_bank if skill.lower() in job_description_lower]

def rank_jobs(jobs, skills):
    ranked = []
    skills_text = " ".join(skills)

    for job in jobs:
        desc = job.get("description", "")
        required_skills = extract_relevant_skills(desc)
        required_skills = ' '.join(required_skills)
        print(skills_text,required_skills)
        title = job.get("title", "")
        company = job.get("company_name", "Unknown")
        apply_link = job.get("apply_options", [{}])[0].get("link", job.get("share_link", "#"))
        logo = job.get("thumbnail")

        # Compute similarity
        vectorizer = TfidfVectorizer().fit_transform([skills_text, required_skills])
        similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]

        # Assign color
        if similarity < 0.6:
            color = "success"  # green
        elif similarity > 0.3:
            color = "warning"  # yellow
        else:
            color = "danger"   # red

        ranked.append({
            "title": title,
            "company": company,
            "logo": logo,
            "similarity": round(similarity, 3),
            "color": color,
            "apply_link": apply_link
        })
    return sorted(ranked, key=lambda x: x["similarity"], reverse=True)

def job_listings(request, role, resume_skills):
    jobs = fetch_jobs(role)
    ranked_jobs = rank_jobs(jobs, resume_skills)
    return render(request, "jobs.html", {
        "role": role,
        "ranked_jobs": ranked_jobs,
        "skills": resume_skills
    })

