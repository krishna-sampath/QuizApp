import re
from quiz.models import QuizQuestion

def parse_dataset(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split questions by blank lines
    questions = content.strip().split("\n\n")
    for question in questions:
        lines = question.strip().split("\n")
        
        # Parse question text (remove the "Q " prefix)
        question_text_match = re.match(r"^#Q (.+)$", lines[0])
        if not question_text_match:
            continue
        question_text = question_text_match.group(1).strip()  # Removes "Q " prefix

        # Parse correct answer (raw text)
        correct_answer_match = re.match(r"^\^ (.+)$", lines[1])
        if not correct_answer_match:
            continue
        correct_answer_text = correct_answer_match.group(1).strip().upper()  # Normalize to uppercase

        # Parse answer options
        options = {}
        for line in lines[2:]:
            option_match = re.match(r"^([A-D]) (.+)$", line)
            if option_match:
                option_letter = option_match.group(1)
                option_text = option_match.group(2).strip()
                options[option_letter] = option_text

        # Determine which option matches the correct answer
        correct_option = None
        for letter, text in options.items():
            if text.strip().upper() == correct_answer_text:  # Normalize for comparison
                correct_option = letter
                break

        if correct_option is None:
            # No match found; skip this question
            print(f"Skipping question: {question_text}")
            continue

        # Save the question in the database
        QuizQuestion.objects.create(
            question_text=question_text,
            question_type="MCQ",  # Assume all are MCQs for simplicity
            option_a=options.get('A', ''),
            option_b=options.get('B', ''),
            option_c=options.get('C', ''),
            option_d=options.get('D', ''),
            correct_answer=correct_option  # Store only the letter ('A', 'B', etc.)
        )

    print("Dataset import complete!")

# Example function call for testing (replace the path to your dataset)
if __name__ == "__main__":
    parse_dataset("/home/sam/Documents/QuizApp/django_quiz_app/dataset/dataset.txt")
