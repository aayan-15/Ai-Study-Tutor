
import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4


class QuizHistory:
    """Stores and retrieves user-specific quiz attempts."""

    def __init__(self):
        self.data_dir = Path(__file__).resolve().parent.parent / "data"
        self.file_path = self.data_dir / "quiz_history.json"

        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self._save_data([])

    def _load_data(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, list) else []

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_data(self, history):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)

    def save_result(self, result, user_email):
        if not user_email:
            raise ValueError("User email is required to save quiz history.")

        history = self._load_data()

        attempt = {
            "attempt_id": str(uuid4()),
            "user_email": user_email,
            "date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "subject": result["subject"],
            "topic": result["topic"],
            "total_questions": result["total_questions"],
            "correct": result["correct"],
            "wrong": result["wrong"],
            "percentage": result["percentage"],
            "weak_topics": result["weak_topics"]
        }

        history.append(attempt)
        self._save_data(history)

        print("\nQuiz attempt saved successfully.")

        return attempt

    def get_history(self, user_email):
        if not user_email:
            return []

        history = self._load_data()

        return [
            attempt for attempt in history
            if attempt.get("user_email", "").lower() == user_email.lower()
        ]

    def get_topic_history(self, topic, user_email):
        history = self.get_history(user_email)

        return [
            attempt for attempt in history
            if attempt["topic"].lower() == topic.lower()
        ]

    def get_topic_statistics(self, topic, user_email):
        attempts = self.get_topic_history(topic, user_email)

        if not attempts:
            return None

        scores = [attempt["percentage"] for attempt in attempts]

        return {
            "topic": topic,
            "total_attempts": len(attempts),
            "average_score": round(sum(scores) / len(scores), 2),
            "best_score": max(scores),
            "latest_score": scores[-1],
            "improvement": round(scores[-1] - scores[0], 2)
        }
