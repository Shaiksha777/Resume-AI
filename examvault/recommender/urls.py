from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommend, name='recommend'),  # /recommend/ → resume_rd page
    path("job/<str:role>/", views.job_listings, name="job_listings"),
]
