
import json

from pathlib import Path
from datetime import datetime


class ActivityManager:

    def __init__(self):
        self.data_file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "activities.json"
        )

        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            self.save_activities([])

    def load_activities(self):
        try:
            with open(self.data_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_activities(self, activities):
        with open(self.data_file, "w") as file:
            json.dump(activities, file, indent=4)

    def add_activity(
        self,
        user_email,
        action,
        item_type,
        item_name,
        details=""
    ):
        activities = self.load_activities()

        new_activity = {
            "user_email": user_email,
            "action": action,
            "item_type": item_type,
            "item_name": item_name,
            "details": details,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        activities.append(new_activity)
        self.save_activities(activities)

    def get_activities(self, user_email):
        activities = self.load_activities()

        user_activities = [
            activity for activity in activities
            if activity.get("user_email") == user_email
        ]

        return sorted(
            user_activities,
            key=lambda activity: activity.get("created_at", ""),
            reverse=True
        )

    def get_recent_activities(self, user_email, limit=10):
        return self.get_activities(user_email)[:limit]
