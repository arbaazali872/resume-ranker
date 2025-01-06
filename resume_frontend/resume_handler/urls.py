from django.urls import path
from . import views

urlpatterns = [
    path('', views.handle_uploads, name='upload_resume'),  # The page where users upload resumes and job descriptions
    path('rank_results/<str:jd_id>/', views.rank_results, name='rank_results'),  # Page showing the ranking results for a session
]
