
import customtkinter as ctk

from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date
from Core.task_manager import TaskManager
from Core.subject_manager import SubjectManager


class PlannerFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color="#F4F6FA"
        )

        self.user = user
        self.user_email = user["email"]

        self.task_manager = TaskManager()
        self.subject_manager = SubjectManager()

        self.subjects = self.subject_manager.get_subjects(
            self.user_email
        )

        self.subject_map = {
            subject["name"]: subject["id"]
            for subject in self.subjects
        }

        self.build_interface()
        self.load_tasks()

    def build_interface(self):

        # Header
        ctk.CTkLabel(
            self,
            text="Study Planner",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=35, pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="Organize your study tasks and stay on track.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(anchor="w", padx=35, pady=(0, 20))

        # Add task form
        self.form = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        self.form.pack(
            fill="x",
            padx=35,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            self.form,
            text="Add Study Task",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        self.title_entry = ctk.CTkEntry(
            self.form,
            placeholder_text="Task title",
            height=40
        )
        self.title_entry.pack(fill="x", padx=20, pady=6)

        self.description_entry = ctk.CTkEntry(
            self.form,
            placeholder_text="Description (optional)",
            height=40
        )
        self.description_entry.pack(fill="x", padx=20, pady=6)

        subject_names = list(self.subject_map.keys())

        self.subject_menu = ctk.CTkOptionMenu(
            self.form,
            values=subject_names if subject_names else ["No subjects available"],
            height=38
        )
        self.subject_menu.pack(fill="x", padx=20, pady=6)

        # Due date label
        ctk.CTkLabel(
            self.form,
            text="Select Due Date",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#657087"
        ).pack(
            anchor="w",
            padx=20,
            pady=(10, 4)
        )

# Calendar date picker
        self.date_entry = DateEntry(
            self.form,
            width=25,
            date_pattern="yyyy-mm-dd",
            background="#3157D5",
            foreground="white",
            borderwidth=2,
            headersbackground="#3157D5",
            headersforeground="white",
            selectbackground="#3157D5",
            selectforeground="white",
            normalbackground="white",
            normalforeground="#202938",
            weekendbackground="#F4F6FA",
            weekendforeground="#3157D5"
        )

        self.date_entry.pack(
            fill="x",
            padx=20,
            pady=6,
            ipady=5
        )

        self.priority_menu = ctk.CTkOptionMenu(
            self.form,
            values=["Low", "Medium", "High"],
            height=38
        )
        self.priority_menu.pack(fill="x", padx=20, pady=6)

        self.message_label = ctk.CTkLabel(
            self.form,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#D9534F"
        )
        self.message_label.pack(anchor="w", padx=20, pady=(5, 0))

        ctk.CTkButton(
            self.form,
            text="Add Task",
            height=38,
            width=130,
            command=self.add_task
        ).pack(anchor="w", padx=20, pady=(8, 18))

        # Task list heading
        ctk.CTkLabel(
            self,
            text="Your Study Tasks",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=35, pady=(5, 10))

        self.tasks_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.tasks_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

    def add_task(self):

        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        due_date = self.date_entry.get().strip()
        priority = self.priority_menu.get()

        selected_subject = self.subject_menu.get()

        subject_id = self.subject_map.get(
            selected_subject
        )

        success, message = self.task_manager.add_task(
            self.user_email,
            title,
            subject_id,
            due_date,
            priority,
            description
        )

        self.message_label.configure(
            text=message,
            text_color="#238636" if success else "#D9534F"
        )

        if success:

            self.title_entry.delete(0, "end")
            self.description_entry.delete(0, "end")
            self.date_entry.delete(0, "end")

            self.load_tasks()

    def load_tasks(self):

        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        tasks = self.task_manager.get_tasks(
            self.user_email
        )

        pending_tasks = [
            task for task in tasks
            if not task.get("completed", False)
        ]

        completed_tasks = [
            task for task in tasks
            if task.get("completed", False)
        ]

        # Pending tasks
        ctk.CTkLabel(
            self.tasks_container,
            text=f"Pending Tasks ({len(pending_tasks)})",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=10, pady=(5, 10))

        if pending_tasks:

            for task in pending_tasks:
                self.create_task_card(task)

        else:

            ctk.CTkLabel(
                self.tasks_container,
                text="No pending tasks.",
                font=ctk.CTkFont(size=13),
                text_color="#8993A5"
            ).pack(anchor="w", padx=15, pady=10)

        # Completed tasks
        ctk.CTkLabel(
            self.tasks_container,
            text=f"Completed Tasks ({len(completed_tasks)})",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=10, pady=(20, 10))

        if completed_tasks:

            for task in completed_tasks:
                self.create_task_card(task)

        else:

            ctk.CTkLabel(
                self.tasks_container,
                text="No completed tasks yet.",
                font=ctk.CTkFont(size=13),
                text_color="#8993A5"
            ).pack(anchor="w", padx=15, pady=10)

    def create_task_card(self, task):

        card = ctk.CTkFrame(
            self.tasks_container,
            fg_color="#FFFFFF",
            corner_radius=10,
            border_width=1,
            border_color="#E5E9F0"
        )

        card.pack(
            fill="x",
            padx=10,
            pady=6
        )

        details = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        details.pack(
            side="left",
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        title_color = (
            "#8993A5"
            if task.get("completed", False)
            else "#202938"
        )

        ctk.CTkLabel(
            details,
            text=task["title"],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=title_color
        ).pack(anchor="w")

        subject_name = next(
            (
                subject["name"]
                for subject in self.subjects
                if subject["id"] == task["subject_id"]
            ),
            "Unknown subject"
        )

        ctk.CTkLabel(
            details,
            text=(
                f"Subject: {subject_name}  |  "
                f"Due: {task['due_date']}  |  "
                f"Priority: {task['priority']}"
            ),
            font=ctk.CTkFont(size=11),
            text_color="#778195"
        ).pack(anchor="w", pady=(5, 0))

        if task.get("description"):

            ctk.CTkLabel(
                details,
                text=task["description"],
                font=ctk.CTkFont(size=12),
                text_color="#8993A5"
            ).pack(anchor="w", pady=(4, 0))

        actions = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        actions.pack(side="right", padx=12)

        status_text = (
            "Mark Pending"
            if task.get("completed", False)
            else "Complete"
        )

        ctk.CTkButton(
            actions,
            text=status_text,
            width=105,
            height=32,
            command=lambda t=task: self.toggle_completion(t)
        ).pack(pady=3)

        ctk.CTkButton(
            actions,
            text="Delete",
            width=105,
            height=32,
            fg_color="#D9534F",
            hover_color="#B83B37",
            command=lambda t=task: self.delete_task(t)
        ).pack(pady=3)

    def toggle_completion(self, task):

        self.task_manager.toggle_task_completion(
            task["id"],
            self.user_email
        )

        self.load_tasks()

    def delete_task(self, task):

        confirmed = messagebox.askyesno(
            "Delete Task",
            f'Are you sure you want to delete "{task["title"]}"?'
        )

        if confirmed:

            self.task_manager.delete_task(
                task["id"],
                self.user_email
            )

            self.load_tasks()
