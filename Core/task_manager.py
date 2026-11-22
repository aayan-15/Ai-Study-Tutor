
import json
import uuid

from pathlib import Path
from datetime import datetime

from Core.activity import ActivityManager


class TaskManager:

    def __init__(self):

        self.data_file = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "task.json"
        )

        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.data_file.exists():
            self.save_tasks([])

        self.activity_manager = ActivityManager()

    def load_tasks(self):

        try:
            with open(self.data_file, "r") as file:
                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self, tasks):

        with open(self.data_file, "w") as file:
            json.dump(tasks, file, indent=4)

    def get_tasks(self, user_email):

        tasks = self.load_tasks()

        user_tasks = [
            task for task in tasks
            if task["user_email"] == user_email
        ]

        return sorted(
            user_tasks,
            key=lambda task: task.get("due_date", "")
        )

    def add_task(
        self,
        user_email,
        title,
        subject_id,
        due_date,
        priority,
        description=""
    ):

        title = title.strip()
        description = description.strip()

        if not title:
            return False, "Task title is required."

        if not subject_id:
            return False, "Please select a subject."

        if not due_date:
            return False, "Due date is required."

        if priority not in ["Low", "Medium", "High"]:
            return False, "Invalid task priority."

        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid due date format."

        tasks = self.load_tasks()

        new_task = {
            "id": str(uuid.uuid4()),
            "user_email": user_email,
            "title": title,
            "description": description,
            "subject_id": subject_id,
            "due_date": due_date,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        tasks.append(new_task)
        self.save_tasks(tasks)

        self.activity_manager.add_activity(
            user_email,
            "Added study task",
            "Task",
            title,
            f"Due date: {due_date} | Priority: {priority}"
        )

        return True, "Study task added successfully."

    def toggle_task_completion(self, task_id, user_email):

        tasks = self.load_tasks()

        for task in tasks:

            if (
                task["id"] == task_id
                and task["user_email"] == user_email
            ):

                task["completed"] = not task.get(
                    "completed",
                    False
                )

                self.save_tasks(tasks)

                action = (
                    "Completed study task"
                    if task["completed"]
                    else "Marked study task as pending"
                )

                self.activity_manager.add_activity(
                    user_email,
                    action,
                    "Task",
                    task["title"]
                )

                return True, task["completed"]

        return False, "Task not found."

    def delete_task(self, task_id, user_email):

        tasks = self.load_tasks()

        task_to_delete = next(
            (
                task for task in tasks
                if task["id"] == task_id
                and task["user_email"] == user_email
            ),
            None
        )

        if task_to_delete is None:
            return False, "Task not found."

        updated_tasks = [
            task for task in tasks
            if not (
                task["id"] == task_id
                and task["user_email"] == user_email
            )
        ]

        self.save_tasks(updated_tasks)

        self.activity_manager.add_activity(
            user_email,
            "Deleted study task",
            "Task",
            task_to_delete["title"]
        )

        return True, "Study task deleted successfully."

    def get_task_statistics(self, user_email):

        tasks = self.get_tasks(user_email)

        total_tasks = len(tasks)

        completed_tasks = sum(
            1 for task in tasks
            if task.get("completed", False)
        )

        pending_tasks = total_tasks - completed_tasks

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks
        }
