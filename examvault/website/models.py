from django.db import models

class ExamPaper(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the upload
    subject = models.CharField(max_length=100)  # Subject name
    course = models.CharField(max_length=100)  # Course name
    semester = models.CharField(max_length=20)  # Semester of the exam
    year = models.IntegerField()  # Year of the exam paper
    department = models.CharField(max_length=100, default='')
    file = models.FileField(upload_to=r'C:\Users\Shaiksha\Desktop\FSD_project\FSD_project\examvault\media')  # Upload PDF files to the 'papers/' directory
    uploaded_by = models.CharField(max_length=100)  # Name/ID of the uploader

    def __str__(self):
        return f"{self.subject} ({self.course}) - {self.year} Semester {self.semester}"

class Resume(models.Model):
    name = models.CharField(max_length=255)
    resume_file = models.FileField(upload_to=r'C:\Users\Shaiksha\Desktop\FSD_project\FSD_project\examvault\media')  #resumes folder stores the uploaded files

    def __str__(self):
        return self.name
