# quiz/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import QuizSession, UserAnswer, QuizQuestion
from django.db.models import Count, Q
import json
import logging

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = SignUpForm()
    return render(request, 'quiz/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'quiz/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def home(request):
    user = request.user
    total_sessions = QuizSession.objects.filter(user=user).count()
    total_correct = UserAnswer.objects.filter(quiz_session__user=user, is_correct=True).count()
    total_incorrect = UserAnswer.objects.filter(quiz_session__user=user, is_correct=False).count()

    # Data for visualization
    sessions = QuizSession.objects.filter(user=user).annotate(
        correct=Count('answers', filter=Q(answers__is_correct=True)),
        incorrect=Count('answers', filter=Q(answers__is_correct=False))
    )

    chart_data = {
        'labels': [f"Session {session.id}" for session in sessions],
        'correct': [session.correct for session in sessions],
        'incorrect': [session.incorrect for session in sessions],
    }

    context = {
        'total_sessions': total_sessions,
        'total_correct': total_correct,
        'total_incorrect': total_incorrect,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'quiz/home.html', context)

@login_required
def start_quiz(request):
    # Check if the user already has an active session
    active_session = QuizSession.objects.filter(user=request.user, completed=False).first()
    if active_session:
        return redirect('take_quiz', session_id=active_session.id)
    
    # Start a new quiz session
    session = QuizSession.objects.create(user=request.user)
    return redirect('take_quiz', session_id=session.id)

@login_required
def take_quiz(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user, completed=False)
    answered_questions = session.answers.values_list('question_id', flat=True)
    total_answered = session.answers.count()

    # Check if the session has already answered 10 questions
    if total_answered >= 10:
        session.completed = True
        session.save()
        return redirect('submit_quiz', session_id=session.id)

    # Get a random unanswered question
    question = QuizQuestion.objects.exclude(id__in=answered_questions).order_by('?').first()

    if not question:
        # No more questions available, mark session as completed
        session.completed = True
        session.save()
        return redirect('submit_quiz', session_id=session.id)

    # Determine the current question number
    question_number = total_answered + 1

    return render(request, 'quiz/take_quiz.html', {
        'question': question,
        'session': session,
        'question_number': question_number
    })

@login_required
def submit_answer(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(QuizSession, id=session_id, user=request.user, completed=False)
        question_id = request.POST.get('question_id')
        selected_option = request.POST.get('selected_option')  # 'A', 'B', etc.

        question = get_object_or_404(QuizQuestion, id=question_id)

        # Normalize comparison for correctness
        correct_option = question.correct_answer.strip().upper()  # Letter (e.g., 'A', 'B')
        selected_option = selected_option.strip().upper()  # Letter (e.g., 'A', 'B')

        is_correct = selected_option == correct_option

        # Save the user's answer
        UserAnswer.objects.create(
            quiz_session=session,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        )

        # Check if we've answered 10 questions
        total_answered = session.answers.count()
        if total_answered >= 10:
            session.completed = True
            session.save()
            return redirect('submit_quiz', session_id=session.id)

        # Continue to next question
        return redirect('take_quiz', session_id=session.id)
    else:
        return redirect('home')

@login_required
def submit_quiz(request, session_id):
    # Now that we are submitting the quiz, the session should be completed
    # So do not filter by completed=False here
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    # If you haven't set it to completed yet, do it here if needed:
    if not session.completed:
        session.completed = True
        session.save()

    total_correct = session.answers.filter(is_correct=True).count()
    total_incorrect = session.answers.filter(is_correct=False).count()

    return render(request, 'quiz/submit_quiz.html', {
        'total_correct': total_correct,
        'total_incorrect': total_incorrect
    })


@login_required
def history(request):
    sessions = QuizSession.objects.filter(user=request.user).order_by('-start_time').annotate(
        correct_answers=Count('answers', filter=Q(answers__is_correct=True)),
        incorrect_answers=Count('answers', filter=Q(answers__is_correct=False))
    )
    return render(request, 'quiz/history.html', {'sessions': sessions})

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    answers = session.answers.select_related('question')
    return render(request, 'quiz/session_detail.html', {'session': session, 'answers': answers})
