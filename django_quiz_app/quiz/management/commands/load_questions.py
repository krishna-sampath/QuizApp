import os
from django.core.management.base import BaseCommand
from quiz.models import QuizQuestion
from django.conf import settings

class Command(BaseCommand):
    help = 'Load quiz questions from dataset'

    def handle(self, *args, **kwargs):
        dataset_path = os.path.join(settings.BASE_DIR, 'dataset', 'dataset.txt') 
        if not os.path.exists(dataset_path):
            self.stdout.write(self.style.ERROR(f"Dataset file not found at {dataset_path}"))
            return

        with open(dataset_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('#'):
                question_text = line[1:].strip()
                i += 1
                answer_line = lines[i].strip()
                if answer_line.startswith('^'):
                    correct_answer = answer_line[1:].strip().upper()
                else:
                    self.stdout.write(self.style.ERROR(f"Expected '^' for correct answer at line {i+1}"))
                    break
                i += 1
                options = {}
                while i < len(lines) and lines[i].strip().startswith(tuple(['A', 'B', 'C', 'D'])):
                    option_line = lines[i].strip()
                    option_key = option_line[0]
                    option_text = option_line[1:].strip()
                    options[option_key] = option_text
                    i += 1
                # Determine question type
                if 'D' not in options:
                    question_type = 'TF'
                else:
                    question_type = 'MCQ'
                # Create QuizQuestion
                QuizQuestion.objects.create(
                    question_text=question_text,
                    question_type=question_type,
                    option_a=options.get('A', ''),
                    option_b=options.get('B', ''),
                    option_c=options.get('C', ''),
                    option_d=options.get('D', ''),
                    correct_answer=correct_answer
                )
                self.stdout.write(self.style.SUCCESS(f"Loaded question: {question_text}"))
            else:
                i += 1

        self.stdout.write(self.style.SUCCESS('Quiz questions loaded successfully.'))
