from Core.subject_manager import SubjectManager
from Core.topics import TopicManager
from Core.quiz_history import QuizHistory


class ProgressPlanner:
    """Combines learning progress and quiz performance for a student."""

    def __init__(self):
        self.subject_manager = SubjectManager()
        self.topic_manager = TopicManager()
        self.quiz_history = QuizHistory()

    def get_quiz_summary(self, user_email):
        """Return overall quiz statistics for a student."""

        attempts = self.quiz_history.get_history(user_email)

        if not attempts:
            return {
                "total_attempts": 0,
                "average_score": 0,
                "best_score": 0,
                "latest_score": 0
            }

        scores = [float(attempt["percentage"]) for attempt in attempts]

        return {
            "total_attempts": len(attempts),
            "average_score": round(sum(scores) / len(scores), 2),
            "best_score": round(max(scores), 2),
            "latest_score": round(scores[-1], 2)
        }

    def get_topic_performance(self, user_email):
        """Group quiz attempts by subject and topic."""

        attempts = self.quiz_history.get_history(user_email)
        topic_data = {}

        for attempt in attempts:
            subject = attempt.get("subject", "Unknown Subject")
            topic = attempt.get("topic", "Unknown Topic")

            key = (subject.lower(), topic.lower())

            if key not in topic_data:
                topic_data[key] = {
                    "subject": subject,
                    "topic": topic,
                    "scores": []
                }

            topic_data[key]["scores"].append(
                float(attempt["percentage"])
            )

        performance = []

        for data in topic_data.values():
            scores = data["scores"]

            performance.append({
                "subject": data["subject"],
                "topic": data["topic"],
                "total_attempts": len(scores),
                "average_score": round(sum(scores) / len(scores), 2),
                "best_score": round(max(scores), 2),
                "latest_score": round(scores[-1], 2)
            })

        return sorted(
            performance,
            key=lambda item: item["average_score"]
        )

    def get_weak_topics(self, user_email, threshold=70, recent_attempts=3):
        """
        Identify topics whose average score across their latest
        attempts is below the given threshold.
        """

        performance = self.get_topic_performance(user_email)
        attempts = self.quiz_history.get_history(user_email)

        weak_topics = []

        for item in performance:
            matching_attempts = [
                attempt for attempt in attempts
                if attempt.get("subject", "").lower() == item["subject"].lower()
                and attempt.get("topic", "").lower() == item["topic"].lower()
            ]

            recent_scores = [
                float(attempt["percentage"])
                for attempt in matching_attempts[-recent_attempts:]
            ]

            average = sum(recent_scores) / len(recent_scores)

            if average < threshold:
                weak_topics.append({
                    "subject": item["subject"],
                    "topic": item["topic"],
                    "average_score": round(average, 2),
                    "latest_score": round(recent_scores[-1], 2),
                    "attempts_considered": len(recent_scores)
                })

        return weak_topics

    def get_dashboard_progress(self, user_email):
        """Combine learning progress and quiz performance."""

        learning_progress = self.subject_manager.get_overall_progress(
            user_email
        )

        quiz_summary = self.get_quiz_summary(user_email)

        return {
            "learning_progress": learning_progress,
            "quiz_summary": quiz_summary,
            "topic_performance": self.get_topic_performance(user_email),
            "weak_topics": self.get_weak_topics(user_email),
            "pending_topics": self.topic_manager.get_pending_topics(
                user_email
            )
        }


if __name__ == "__main__":

    print("=" * 60)
    print("           STUDENT PROGRESS PLANNER TEST")
    print("=" * 60)

    user_email = input("\nEnter student email: ").strip()

    if not user_email:
        print("Email is required.")
    else:
        planner = ProgressPlanner()
        progress = planner.get_dashboard_progress(user_email)

        print("\nLEARNING PROGRESS")
        print("-" * 40)

        for key, value in progress["learning_progress"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        print("\nQUIZ SUMMARY")
        print("-" * 40)

        for key, value in progress["quiz_summary"].items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        print("\nTOPIC PERFORMANCE")
        print("-" * 40)

        if progress["topic_performance"]:
            for item in progress["topic_performance"]:
                print(
                    f"{item['subject']} | {item['topic']} | "
                    f"Average: {item['average_score']}% | "
                    f"Latest: {item['latest_score']}%"
                )
        else:
            print("No quiz attempts found.")

        print("\nWEAK TOPICS")
        print("-" * 40)

        if progress["weak_topics"]:
            for item in progress["weak_topics"]:
                print(
                    f"{item['topic']} ({item['subject']}) - "
                    f"Average: {item['average_score']}%"
                )
        else:
            print("No weak topics found.")

        print("\nPENDING LEARNING TOPICS")
        print("-" * 40)

        if progress["pending_topics"]:
            for item in progress["pending_topics"]:
                print(item["name"])
        else:
            print("No pending topics.")

        print("\n" + "=" * 60)
