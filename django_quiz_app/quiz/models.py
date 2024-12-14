from django.db import models
from django.contrib.auth.models import User

class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.id} by {self.user.username}"

class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
    ]

    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES)
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=1)  # Should store 'A', 'B', 'C', 'D', 'T', 'F'

    def __str__(self):
        return self.question_text

class UserAnswer(models.Model):
    quiz_session = models.ForeignKey(QuizSession, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # 'A', 'B', 'C', 'D', 'T', 'F'
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Answer to {self.question.id} by {self.quiz_session.user.username}"

from django.contrib.auth.models import User

class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.id} by {self.user.username}"

class UserAnswer(models.Model):
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    def __str__(self):
        return f"{self.question} - {self.selected_option} ({'Correct' if self.is_correct else 'Incorrect'})"
