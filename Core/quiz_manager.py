
try:
    from Core.quiz_history import QuizHistory
    from Core.gemini_service import GeminiService
    from Core.quiz_engine import QuizEngine
except ModuleNotFoundError:
    # Supports running this file directly from the Core folder.
    from quiz_history import QuizHistory
    from gemini_service import GeminiService
    from quiz_engine import QuizEngine


class QuizManager:
    """Manages AI-generated quizzes."""

    def __init__(self):
        self.ai_service = GeminiService()
        self.last_error = None

    def generate_quiz(self, subject, topic, number_of_questions=5):

        self.last_error = None

        result = self.ai_service.generate_quiz(
            subject=subject,
            topic=topic,
            number_of_questions=number_of_questions
        )

        if not result["success"]:
            self.last_error = result["message"]
            print(f"\nQuiz generation failed: {self.last_error}")
            return None

        return result["quiz"]


def main():

    try:
        from Core.quiz_engine import QuizEngine
    except ModuleNotFoundError:
        from quiz_engine import QuizEngine
        
    print("=" * 60)
    print("              AI QUIZ GENERATOR TEST")
    print("=" * 60)

    user_email = input("\nEnter student email: ").strip()

    if not user_email:
        print("Student email is required.")
        return

    subject = input("Enter subject: ").strip()
    topic = input("Enter topic: ").strip()

    while True:
        try:
            number_of_questions = int(
                input("Enter number of questions: ").strip()
            )

            if number_of_questions > 0:
                break

            print("Please enter a number greater than 0.")

        except ValueError:
            print("Please enter a valid number.")

    manager = QuizManager()

    print("\nGenerating quiz...\n")

    quiz = manager.generate_quiz(
        subject,
        topic,
        number_of_questions
    )

    if quiz:
        print("Quiz generated successfully.")

        engine = QuizEngine(quiz)
        result = engine.start_quiz()

        if result:
            history = QuizHistory()
            history.save_result(result, user_email)


if __name__ == "__main__":
    main()
