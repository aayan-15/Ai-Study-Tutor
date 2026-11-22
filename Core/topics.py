import json
import uuid

from pathlib import Path
from datetime import datetime

from Core.activity import ActivityManager
from Core.subject_manager import SubjectManager


class TopicManager:

    def __init__(self):

        self.data_file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "topics.json"
        )

        self.data_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.data_file.exists():
            self.save_topics([])

        self.activity_manager = ActivityManager()
        self.subject_manager = SubjectManager()

    # Load topics from JSON
    def load_topics(self):

        try:
            with open(self.data_file, "r") as file:
                topics = json.load(file)

                # Add completed field to older topics
                # that don't have it yet
                changed = False

                for topic in topics:
                    if "completed" not in topic:
                        topic["completed"] = False
                        changed = True

                if changed:
                    self.save_topics(topics)

                return topics

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    # Save topics to JSON
    def save_topics(self, topics):

        with open(self.data_file, "w") as file:
            json.dump(topics, file, indent=4)

    # Get topics for a specific subject and user
    def get_topics(self, subject_id, user_email):

        topics = self.load_topics()

        return [
            topic for topic in topics
            if (
                topic["subject_id"] == subject_id
                and topic["user_email"] == user_email
            )
        ]

    # Get subject name
    def get_subject_name(self, subject_id, user_email):

        subjects = self.subject_manager.get_subjects(
            user_email
        )

        for subject in subjects:

            if subject["id"] == subject_id:
                return subject["name"]

        return "Unknown subject"

    # Add a new topic
    def add_topic(
        self,
        subject_id,
        user_email,
        name,
        description=""
    ):

        name = name.strip()
        description = description.strip()

        if not name:
            return False, "Topic name is required."

        topics = self.load_topics()

        # Prevent duplicate topic names
        for topic in topics:

            if (
                topic["subject_id"] == subject_id
                and topic["user_email"] == user_email
                and topic["name"].lower() == name.lower()
            ):
                return False, "This topic already exists in this subject."

        subject_name = self.get_subject_name(
            subject_id,
            user_email
        )

        new_topic = {
            "id": str(uuid.uuid4()),
            "subject_id": subject_id,
            "user_email": user_email,
            "name": name,
            "description": description,
            "completed": False,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        topics.append(new_topic)
        self.save_topics(topics)

        self.activity_manager.add_activity(
            user_email,
            "Added topic",
            "Topic",
            name,
            f"Subject: {subject_name}"
        )

        return True, "Topic added successfully."

    # Update an existing topic
    def update_topic(
        self,
        topic_id,
        subject_id,
        user_email,
        new_name,
        new_description=""
    ):

        new_name = new_name.strip()
        new_description = new_description.strip()

        if not new_name:
            return False, "Topic name is required."

        topics = self.load_topics()

        # Check duplicate names
        for topic in topics:

            if (
                topic["subject_id"] == subject_id
                and topic["user_email"] == user_email
                and topic["name"].lower() == new_name.lower()
                and topic["id"] != topic_id
            ):
                return False, "This topic already exists in this subject."

        subject_name = self.get_subject_name(
            subject_id,
            user_email
        )

        # Find and update topic
        for topic in topics:

            if (
                topic["id"] == topic_id
                and topic["subject_id"] == subject_id
                and topic["user_email"] == user_email
            ):

                old_name = topic["name"]

                topic["name"] = new_name
                topic["description"] = new_description

                # Preserve existing completion status
                if "completed" not in topic:
                    topic["completed"] = False

                self.save_topics(topics)

                self.activity_manager.add_activity(
                    user_email,
                    "Updated topic",
                    "Topic",
                    new_name,
                    f"Subject: {subject_name} | Previous name: {old_name}"
                )

                return True, "Topic updated successfully."

        return False, "Topic not found."

    # Toggle topic completion
    def toggle_completion(
        self,
        topic_id,
        subject_id,
        user_email
    ):

        topics = self.load_topics()

        subject_name = self.get_subject_name(
            subject_id,
            user_email
        )

        for topic in topics:

            if (
                topic["id"] == topic_id
                and topic["subject_id"] == subject_id
                and topic["user_email"] == user_email
            ):

                current_status = topic.get(
                    "completed",
                    False
                )

                topic["completed"] = not current_status

                self.save_topics(topics)

                if topic["completed"]:
                    action = "Completed topic"
                else:
                    action = "Marked topic as pending"

                self.activity_manager.add_activity(
                    user_email,
                    action,
                    "Topic",
                    topic["name"],
                    f"Subject: {subject_name}"
                )

                return True, topic["completed"]

        return False, "Topic not found."

    # Delete a topic
    def delete_topic(
        self,
        topic_id,
        subject_id,
        user_email
    ):

        topics = self.load_topics()

        topic_to_delete = next(
            (
                topic for topic in topics
                if (
                    topic["id"] == topic_id
                    and topic["subject_id"] == subject_id
                    and topic["user_email"] == user_email
                )
            ),
            None
        )

        if topic_to_delete is None:
            return False, "Topic not found."

        subject_name = self.get_subject_name(
            subject_id,
            user_email
        )

        updated_topics = [
            topic for topic in topics
            if not (
                topic["id"] == topic_id
                and topic["subject_id"] == subject_id
                and topic["user_email"] == user_email
            )
        ]

        self.save_topics(updated_topics)

        self.activity_manager.add_activity(
            user_email,
            "Deleted topic",
            "Topic",
            topic_to_delete["name"],
            f"Subject: {subject_name}"
        )

        return True, "Topic deleted successfully."

    # Get completion statistics for a subject
    def get_subject_progress(
        self,
        subject_id,
        user_email
    ):

        topics = self.get_topics(
            subject_id,
            user_email
        )

        total_topics = len(topics)

        completed_topics = sum(
            1 for topic in topics
            if topic.get("completed", False)
        )

        if total_topics == 0:
            percentage = 0
        else:
            percentage = round(
                (completed_topics / total_topics) * 100
            )

        return {
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "percentage": percentage
        }

    def get_pending_topics(self, user_email):

        topics = self.load_topics()
        subjects = self.subject_manager.get_subjects(user_email)

        pending_topics = []

        for subject in subjects:

            subject_topics = [
                topic for topic in topics
                if topic["subject_id"] == subject["id"]
                and topic["user_email"] == user_email
                and not topic.get("completed", False)
            ]

            for topic in subject_topics:

                pending_topics.append({
                    "id": topic["id"],
                    "name": topic["name"],
                    "description": topic.get("description", ""),
                    "subject_id": subject["id"],
                    "subject_name": subject["name"],
                    "created_at": topic.get("created_at", "")
                })

        return pending_topics