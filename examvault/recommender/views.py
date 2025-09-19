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
API_KEY = ""




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

def fetch_courses_batch_serpapi(skills, max_results_per_skill=2):
    """Fetch courses for multiple skills using optimized SerpAPI searches"""
    all_courses = {}
    
    try:
        # Split skills into batches for efficient searching
        # We'll do 2 searches maximum: one for first half, one for second half
        skill_batches = []
        batch_size = max(1, len(skills) // 2) if len(skills) > 2 else len(skills)
        
        for i in range(0, len(skills), batch_size):
            skill_batches.append(skills[i:i + batch_size])
        
        for batch in skill_batches[:2]:  # Maximum 2 API calls
            # Create a combined search query for multiple skills
            search_terms = " OR ".join([f'"{skill} course"' for skill in batch])
            search_query = f"({search_terms}) online tutorial udemy coursera edx"
            
            params = {
                "engine": "google",
                "q": search_query,
                "hl": "en",
                "gl": "us",
                "api_key": API_KEY,
                "num": len(batch) * max_results_per_skill * 3  # Get more results to distribute among skills
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            # Initialize course lists for each skill in this batch
            for skill in batch:
                if skill not in all_courses:
                    all_courses[skill] = []
            
            # Distribute results among skills
            course_keywords = ["course", "tutorial", "learn", "training", "class", "bootcamp", "certification"]
            
            for result in organic_results:
                title = result.get("title", "").lower()
                link = result.get("link", "")
                snippet = result.get("snippet", "").lower()
                
                # Check if this result is course-related
                if any(keyword in title or keyword in snippet for keyword in course_keywords):
                    # Find which skill this result matches best
                    for skill in batch:
                        if (skill.lower() in title or skill.lower() in snippet) and len(all_courses[skill]) < max_results_per_skill:
                            # Determine platform from URL
                            platform = "Online"
                            if "udemy.com" in link:
                                platform = "Udemy"
                            elif "coursera.org" in link:
                                platform = "Coursera"
                            elif "edx.org" in link:
                                platform = "edX"
                            elif "youtube.com" in link:
                                platform = "YouTube"
                            elif "pluralsight.com" in link:
                                platform = "Pluralsight"
                            elif "linkedin.com/learning" in link:
                                platform = "LinkedIn Learning"
                            
                            all_courses[skill].append({
                                "title": result.get("title", ""),
                                "platform": platform,
                                "url": link,
                                "description": result.get("snippet", ""),
                                "name": result.get("title", "")
                            })
                            break
        
        # Fill any missing courses with fallback searches or static data
        for skill in skills:
            if skill not in all_courses or len(all_courses[skill]) == 0:
                all_courses[skill] = fetch_courses_from_static_db(skill, max_results_per_skill)
        
        return all_courses
        
    except Exception as e:
        print(f"Error in batch course search: {e}")
        # Fallback to individual static searches
        fallback_courses = {}
        for skill in skills:
            fallback_courses[skill] = fetch_courses_from_static_db(skill, max_results_per_skill)
        return fallback_courses

def fetch_courses_from_serpapi(skill, max_results=2):
    """Fetch courses dynamically using SerpAPI Google search (single skill)"""
    try:
        # Search for courses related to the skill
        search_query = f'"{skill} course" online tutorial udemy coursera edx'
        
        params = {
            "engine": "google",
            "q": search_query,
            "hl": "en",
            "gl": "us",
            "api_key": API_KEY,
            "num": max_results * 3  # Get more results to filter better ones
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        courses = []
        organic_results = results.get("organic_results", [])
        
        course_keywords = ["course", "tutorial", "learn", "training", "class", "bootcamp", "certification"]
        
        for result in organic_results:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            
            # Filter for course-related content
            if any(keyword in title.lower() or keyword in snippet.lower() for keyword in course_keywords):
                # Determine platform from URL
                platform = "Online"
                if "udemy.com" in link:
                    platform = "Udemy"
                elif "coursera.org" in link:
                    platform = "Coursera"
                elif "edx.org" in link:
                    platform = "edX"
                elif "youtube.com" in link:
                    platform = "YouTube"
                elif "pluralsight.com" in link:
                    platform = "Pluralsight"
                elif "linkedin.com/learning" in link:
                    platform = "LinkedIn Learning"
                
                courses.append({
                    "title": title,
                    "platform": platform,
                    "url": link,
                    "description": snippet,
                    "name": title  # For compatibility with existing code
                })
                
                if len(courses) >= max_results:
                    break
        
        return courses
        
    except Exception as e:
        print(f"Error fetching courses for {skill}: {e}")
        # Fallback to static database if API fails
        return fetch_courses_from_static_db(skill, max_results)

def fetch_courses_from_static_db(skill, max_results=COURSES_PER_SKILL):
    """Fallback function to use static database"""
    skill_key = skill.lower()
    if skill_key in COURSES_DB:
        # Convert static DB format to match dynamic format
        static_courses = COURSES_DB[skill_key][:max_results]
        return [{
            "title": course.get("name", ""),
            "platform": course.get("platform", ""),
            "url": course.get("url", ""),
            "description": f"Learn {skill} with this comprehensive course",
            "name": course.get("name", "")
        } for course in static_courses]
    return []

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

