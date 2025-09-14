from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup_user, name='signup'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='log'),
    path('upload', views.upload_paper, name='upload'),
    path('download', views.download_page, name='download'),  # Rename to 'download' for the page # Ensure this points to download_paper view
    path('amrita',views.amrita_mail,name='amrita'),
    path('get_courses/<str:department>/', views.get_courses, name='get_courses'),
    path('get_papers/<str:department>/<str:course>/', views.get_papers, name='get_papers'),
    path('download_paper/<int:paper_id>/', views.download_paper, name='download_paper'),
    path('stats/', views.stats_view, name='stats'),
    path('resumes/', views.resume_home, name='resumes'),  
    path('upload_resume', views.upload_resume, name='upload_resume'),
    path('list_resumes', views.list_resumes, name='list_resumes'),
    path('download/<int:resume_id>/', views.download_resume, name='download_resume'),
    
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
