# quiz/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),  # Root URL mapped to 'home' view
    path('start_quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:session_id>/', views.take_quiz, name='take_quiz'),
    path('submit_answer/<int:session_id>/', views.submit_answer, name='submit_answer'),
    path('submit_quiz/<int:session_id>/', views.submit_quiz, name='submit_quiz'),
    path('history/', views.history, name='history'),
    path('history/<int:session_id>/', views.session_detail, name='session_detail'),
]
