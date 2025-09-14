from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import ExamPaper
from .forms import ExamPaperForm, SignUpForm # You need to create this form
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import ExamPaper
import os
from django.conf import settings
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
import re
from django.http import JsonResponse
from .models import Resume
from .forms import ResumeForm
from django.http import FileResponse




# Create your views here.

def home(request):
    return render(request,'base.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        # Check for admin login (superuser)
        user = authenticate(request, username=username, password=password)
        if user is not None or user.is_superuser:
            login(request, user)
            return redirect('home')

        # Email verification for students
        if re.match(r'^ch\.en\.u4\d{8}@ch\.students\.amrita\.edu$', username):
            # Generate and send a verification code
            verification_code = send_verification_code(username)
            request.session['verification_code'] = verification_code
            request.session['email'] = username
            return render(request, 'verify_code.html', {'email': username})
        else:
            messages.error(request, 'Invalid email format')
            return render(request, 'login.html', {})
        
    return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    return render(request,'base.html',{})



def upload_paper(request):
    if request.method == 'POST':
        form = ExamPaperForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a success page after upload
    else:
        form = ExamPaperForm()
    return render(request, 'upload.html', {'form': form})

def download_page(request):
    papers = ExamPaper.objects.all()
    return render(request,'download.html',{'papers':papers})

def download_paper(request, paper_id):
    paper = get_object_or_404(ExamPaper, id=paper_id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(paper.file))
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return HttpResponse("File not found.", status=404)

def send_verification_code(email):
    verification_code = random.randint(100000, 999999)  # Generate 6-digit code
    subject = 'Your Verification Code'
    message = f'Your verification code is: {verification_code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

    return verification_code

def amrita_mail(request):
    return render(request,'amrita_mail.html')


def get_courses(request, department):
    courses = ExamPaper.objects.filter(department=department).values('course').distinct()
    course_list = [course['course'] for course in courses]
    return JsonResponse(course_list, safe=False)

def get_papers(request, department, course):
    papers = ExamPaper.objects.filter(department=department, course=course)
    paper_list = [{'id': paper.id, 'subject': paper.subject, 'semester': paper.semester, 'year': paper.year} for paper in papers]
    return JsonResponse(paper_list, safe=False)

def stats_view(request):
    total_papers = ExamPaper.objects.count()
    total_users = User.objects.count()
    return render(request, 'your_template.html', {
        'total_papers': total_papers,
        'total_users': total_users,
    })


def signup_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'base.html')
        else:
            # Debugging - print form errors in console
            print(form.errors)  # Log the form errors to help debug
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})
    
    
def resume_home(request):
    return render(request, 'resume_home.html')


# View to upload resume
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('list_resumes')
    else:
        form = ResumeForm()
    return render(request, 'upload_resume.html', {'form': form})

# View to list and download resumes
def list_resumes(request):
    resumes = Resume.objects.all()
    return render(request, 'list_resume.html', {'resumes': resumes})

# View to download resume
def download_resume(request, resume_id):
    resume = Resume.objects.get(id=resume_id)
    response = FileResponse(resume.resume_file)
    return response