try:
    from Core.quiz_result import QuizResult
except ModuleNotFoundError:
    from quiz_result import QuizResult


class QuizEngine:
    """Handles quiz attempts and student interaction."""

    def __init__(self, quiz):
        self.quiz = quiz
        self.questions = quiz["questions"]
        self.user_answers = []

    def start_quiz(self):

        print("\n" + "=" * 60)
        print("                  STARTING QUIZ")
        print("=" * 60)

        print(f"\nSubject: {self.quiz['subject']}")
        print(f"Topic: {self.quiz['topic']}")
        print(f"Total Questions: {len(self.questions)}")

        input("\nPress Enter to start...")

        for index, question in enumerate(self.questions, start=1):

            print("\n" + "-" * 60)
            print(f"Question {index}/{len(self.questions)}")
            print("-" * 60)

            print("\n" + question["question"])

            for key, option in question["options"].items():
                print(f"{key}. {option}")

            while True:

                answer = input("\nYour answer (A/B/C/D): ").strip().upper()

                if answer in ["A", "B", "C", "D"]:
                    break

                print("Invalid choice. Please enter A, B, C, or D.")

            self.user_answers.append(answer)

        result = QuizResult.calculate(
            self.quiz,
            self.user_answers
        )

        self.display_result(result)

        return result

    def display_result(self, result):

        print("\n" + "=" * 60)
        print("                    QUIZ RESULTS")
        print("=" * 60)

        print(f"\nTotal Questions: {result['total_questions']}")
        print(f"Correct Answers: {result['correct']}")
        print(f"Wrong Answers:   {result['wrong']}")
        print(f"Percentage:      {result['percentage']}%")

        print(f"\n{result['remark']}")

        print("\n" + "-" * 60)
        print("                 ANSWER REVIEW")
        print("-" * 60)

        for index, item in enumerate(result["review"], start=1):

            print(f"\nQuestion {index}: {item['status']}")
            print(f"Your Answer: {item['user_answer']}")
            print(f"Correct Answer: {item['correct_answer']}")
            print(f"Explanation: {item['explanation']}")

        if result["weak_topics"]:

            print("\nWeak Topics:")

            for topic in result["weak_topics"]:
                print(f"- {topic}")

        print("\n" + "=" * 60)
        print("                  QUIZ COMPLETED")
        print("=" * 60)
