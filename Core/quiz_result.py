
class QuizResult:
    """Evaluates quiz attempts and generates result data."""

    @staticmethod
    def calculate(quiz, user_answers):

        questions = quiz["questions"]

        correct = 0
        wrong = 0
        review = []

        for index, question in enumerate(questions):

            user_answer = user_answers[index]
            correct_answer = question["answer"]

            is_correct = user_answer == correct_answer

            if is_correct:
                correct += 1
                status = "Correct"
            else:
                wrong += 1
                status = "Wrong"

            review.append({
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "status": status,
                "explanation": question["explanation"]
            })

        total = len(questions)

        percentage = (correct / total) * 100 if total else 0

        if percentage >= 80:
            remark = "Excellent performance!"
        elif percentage >= 60:
            remark = "Good effort! Keep practicing."
        else:
            remark = "You need more practice on this topic."

        weak_topics = []

        if total > 0 and percentage < 60:
            weak_topics.append(quiz["topic"])

        return {
            "subject": quiz["subject"],
            "topic": quiz["topic"],
            "total_questions": total,
            "correct": correct,
            "wrong": wrong,
            "percentage": round(percentage, 2),
            "remark": remark,
            "weak_topics": weak_topics,
            "review": review
        }
