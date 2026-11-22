
import json
import uuid

from pathlib import Path
from datetime import datetime

from Core.activity import ActivityManager


class SubjectManager:

    def __init__(self):
        self.data_file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "subjects.json"
        )

        self.data_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.data_file.exists():
            self.save_subjects([])

        self.activity_manager = ActivityManager()

    def load_subjects(self):
        try:
            with open(self.data_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_subjects(self, subjects):
        with open(self.data_file, "w") as file:
            json.dump(subjects, file, indent=4)

    def get_subjects(self, user_email):
        subjects = self.load_subjects()

        return [
            subject for subject in subjects
            if subject["user_email"] == user_email
        ]

    def add_subject(self, user_email, name, description=""):
        name = name.strip()
        description = description.strip()

        if not name:
            return False, "Subject name is required."

        subjects = self.load_subjects()

        for subject in subjects:
            if (
                subject["user_email"] == user_email
                and subject["name"].lower() == name.lower()
            ):
                return False, "This subject already exists."

        new_subject = {
            "id": str(uuid.uuid4()),
            "user_email": user_email,
            "name": name,
            "description": description,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        subjects.append(new_subject)
        self.save_subjects(subjects)

        self.activity_manager.add_activity(
            user_email,
            "Added subject",
            "Subject",
            name
        )

        return True, "Subject added successfully."

    def update_subject(
        self,
        subject_id,
        user_email,
        new_name,
        new_description=""
    ):
        new_name = new_name.strip()
        new_description = new_description.strip()

        if not new_name:
            return False, "Subject name is required."

        subjects = self.load_subjects()

        for subject in subjects:
            if (
                subject["user_email"] == user_email
                and subject["name"].lower() == new_name.lower()
                and subject["id"] != subject_id
            ):
                return False, "This subject already exists."

        for subject in subjects:
            if (
                subject["id"] == subject_id
                and subject["user_email"] == user_email
            ):
                old_name = subject["name"]

                subject["name"] = new_name
                subject["description"] = new_description

                self.save_subjects(subjects)

                self.activity_manager.add_activity(
                    user_email,
                    "Updated subject",
                    "Subject",
                    new_name,
                    f"Previous name: {old_name}"
                )

                return True, "Subject updated successfully."

        return False, "Subject not found."

    def delete_subject(self, subject_id, user_email):
        subjects = self.load_subjects()

        subject_to_delete = next(
            (
                subject for subject in subjects
                if (
                    subject["id"] == subject_id
                    and subject["user_email"] == user_email
                )
            ),
            None
        )

        if subject_to_delete is None:
            return False, "Subject not found."

        updated_subjects = [
            subject for subject in subjects
            if not (
                subject["id"] == subject_id
                and subject["user_email"] == user_email
            )
        ]

        self.save_subjects(updated_subjects)

        self.activity_manager.add_activity(
            user_email,
            "Deleted subject",
            "Subject",
            subject_to_delete["name"]
        )

        return True, "Subject deleted successfully."

    def get_overall_progress(self, user_email):
        from Core.topics import TopicManager

        subjects = self.get_subjects(user_email)
        topic_manager = TopicManager()

        total_topics = 0
        completed_topics = 0

        for subject in subjects:
            progress = topic_manager.get_subject_progress(
                subject["id"],
                user_email
            )

            total_topics += progress["total_topics"]
            completed_topics += progress["completed_topics"]

        if total_topics == 0:
            percentage = 0
        else:
            percentage = round(
                (completed_topics / total_topics) * 100
            )

        return {
            "total_subjects": len(subjects),
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "percentage": percentage
        }
