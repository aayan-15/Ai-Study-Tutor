import customtkinter as ctk

from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import date

from Core.task_manager import TaskManager
from Core.subject_manager import SubjectManager
from Gui import theme


# Only the urgent priority gets a color. Everything else stays muted.
PRIORITY_COLORS = {"High": theme.NEGATIVE}


class PlannerFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color=theme.BG
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

        self.subject_names = {
            subject["id"]: subject["name"]
            for subject in self.subjects
        }

        self.build_interface()
        self.load_tasks()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def build_interface(self):

        # Header: title and live count on the left, tick bar on the right
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(
            fill="x",
            padx=theme.PAGE_X,
            pady=(32, theme.GAP)
        )

        heading = ctk.CTkFrame(header, fg_color="transparent")
        heading.pack(side="left")

        theme.label(
            heading, "Study planner", "title"
        ).pack(anchor="w")

        self.summary_label = theme.label(
            heading, "", "meta", color=theme.MUTED
        )
        self.summary_label.pack(anchor="w", pady=(4, 0))

        self.progress_slot = ctk.CTkFrame(
            header, fg_color="transparent"
        )
        self.progress_slot.pack(side="right", anchor="s", pady=(0, 4))

        # Add task form
        self.form = theme.card(self)
        self.form.pack(
            fill="x",
            padx=theme.PAGE_X,
            pady=(0, theme.GAP)
        )

        fields = ctk.CTkFrame(self.form, fg_color="transparent")
        fields.pack(
            fill="x",
            padx=theme.CARD_PAD,
            pady=theme.CARD_PAD
        )

        for column in range(3):
            fields.grid_columnconfigure(
                column, weight=1, uniform="field"
            )

        theme.label(
            fields, "New task", "heading"
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        self.title_entry = theme.entry(fields, "Task title")
        self.title_entry.grid(
            row=1, column=0, columnspan=3,
            sticky="ew", pady=(12, 8)
        )

        self.description_entry = theme.entry(
            fields, "Description (optional)"
        )
        self.description_entry.grid(
            row=2, column=0, columnspan=3,
            sticky="ew", pady=(0, 16)
        )

        column_pads = [(0, 8), (8, 8), (8, 0)]

        for column, text in enumerate(
            ["Subject", "Due date", "Priority"]
        ):
            theme.label(
                fields, text, "small", color=theme.TEXT_2
            ).grid(
                row=3, column=column, sticky="w",
                padx=column_pads[column], pady=(0, 4)
            )

        subject_names = list(self.subject_map.keys())

        self.subject_menu = self._select(
            fields,
            subject_names if subject_names else ["No subjects available"]
        )
        self.subject_menu.grid(
            row=4, column=0, sticky="ew", padx=column_pads[0]
        )

        self.date_entry = DateEntry(
            fields,
            date_pattern="yyyy-mm-dd",
            font=theme.fonts()["body"],
            borderwidth=1,
            bordercolor=theme.FIELD_BORDER,
            background=theme.ACCENT,
            foreground="white",
            headersbackground=theme.RAISED,
            headersforeground=theme.TEXT_2,
            selectbackground=theme.ACCENT,
            selectforeground="white",
            normalbackground=theme.CARD,
            normalforeground=theme.TEXT,
            weekendbackground=theme.CARD,
            weekendforeground=theme.TEXT_2,
            othermonthbackground=theme.CARD,
            othermonthforeground=theme.MUTED,
            othermonthwebackground=theme.CARD,
            othermonthweforeground=theme.MUTED
        )
        self.date_entry.grid(
            row=4, column=1, sticky="ew",
            padx=column_pads[1], ipady=8
        )

        self.priority_menu = self._select(
            fields, ["Low", "Medium", "High"]
        )
        self.priority_menu.grid(
            row=4, column=2, sticky="ew", padx=column_pads[2]
        )

        self.message_label = theme.label(
            fields, "", "small", color=theme.NEGATIVE
        )
        self.message_label.grid(
            row=5, column=0, columnspan=2,
            sticky="w", pady=(16, 0)
        )

        theme.primary_button(
            fields, "Add task", self.add_task, width=128
        ).grid(row=5, column=2, sticky="e", pady=(16, 0))

        # Task list
        self.tasks_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.FIELD_BORDER,
            scrollbar_button_hover_color=theme.MUTED
        )

        self.tasks_container.pack(
            fill="both",
            expand=True,
            padx=theme.PAGE_X,
            pady=(0, theme.GAP)
        )

    def _select(self, parent, values):
        """Read-only dropdown that matches the text fields."""
        return ctk.CTkComboBox(
            parent,
            values=values,
            state="readonly",
            height=40,
            corner_radius=theme.CONTROL_RADIUS,
            border_width=1,
            border_color=theme.FIELD_BORDER,
            fg_color=theme.CARD,
            button_color=theme.CARD,
            button_hover_color=theme.RAISED,
            text_color=theme.TEXT,
            dropdown_fg_color=theme.CARD,
            dropdown_hover_color=theme.RAISED,
            dropdown_text_color=theme.TEXT,
            font=theme.fonts()["body"],
            dropdown_font=theme.fonts()["body"]
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

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
            text_color=theme.POSITIVE if success else theme.NEGATIVE
        )

        if success:

            self.title_entry.delete(0, "end")
            self.description_entry.delete(0, "end")
            self.date_entry.set_date(date.today())

            self.load_tasks()

    def toggle_completion(self, task):

        self.task_manager.toggle_task_completion(
            task["id"],
            self.user_email
        )

        self.load_tasks()

    def delete_task(self, task):

        confirmed = messagebox.askyesno(
            "Delete task",
            f'Are you sure you want to delete "{task["title"]}"?'
        )

        if confirmed:

            self.task_manager.delete_task(
                task["id"],
                self.user_email
            )

            self.load_tasks()

    # ------------------------------------------------------------------
    # Task list
    # ------------------------------------------------------------------

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

        self.update_progress(len(completed_tasks), len(tasks))

        self.add_section(
            "Pending", pending_tasks,
            "No pending tasks", top=0
        )

        self.add_section(
            "Completed", completed_tasks,
            "Nothing completed yet", top=theme.GAP
        )

    def update_progress(self, completed, total):

        self.summary_label.configure(
            text=f"{completed} of {total} done" if total else "No tasks yet"
        )

        for widget in self.progress_slot.winfo_children():
            widget.destroy()

        # One tick per task, filled in ink when done
        bar = theme.tick_bar(self.progress_slot, completed, total)
        bar.configure(width=240, bg=theme.BG)
        bar.pack()

    def add_section(self, title, tasks, empty_text, top):

        row = ctk.CTkFrame(self.tasks_container, fg_color="transparent")
        row.pack(fill="x", pady=(top, 12))

        theme.label(row, title, "heading").pack(side="left")

        theme.label(
            row, str(len(tasks)), "meta", color=theme.MUTED
        ).pack(side="left", padx=(8, 0))

        if not tasks:
            theme.label(
                self.tasks_container, empty_text,
                "small", color=theme.MUTED
            ).pack(anchor="w", pady=(0, 12))
            return

        for task in tasks:
            self.create_task_card(task)

    def create_task_card(self, task):

        completed = task.get("completed", False)

        card = theme.card(self.tasks_container)
        card.pack(fill="x", pady=(0, 12))

        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(theme.CARD_PAD, 8),
            pady=16
        )

        theme.label(
            details,
            task["title"],
            "body",
            color=theme.MUTED if completed else theme.TEXT
        ).pack(anchor="w")

        subject_name = self.subject_names.get(
            task["subject_id"], "Unknown subject"
        )

        meta = ctk.CTkFrame(details, fg_color="transparent")
        meta.pack(anchor="w", pady=(4, 0))

        theme.label(
            meta,
            f"{subject_name}  ·  due {task['due_date']}  ·",
            "meta",
            color=theme.MUTED
        ).pack(side="left")

        priority = task["priority"]

        theme.label(
            meta,
            f" {priority.lower()} priority",
            "meta",
            color=PRIORITY_COLORS.get(priority, theme.MUTED)
        ).pack(side="left")

        if task.get("description"):

            theme.label(
                details,
                task["description"],
                "small",
                color=theme.TEXT_2,
                wraplength=560,
                height=0
            ).pack(anchor="w", pady=(8, 0))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="right", padx=(8, 16))

        theme.text_button(
            actions,
            "Mark pending" if completed else "Complete",
            lambda task=task: self.toggle_completion(task)
        ).pack(side="left")

        theme.text_button(
            actions,
            "Delete",
            lambda task=task: self.delete_task(task),
            color=theme.NEGATIVE
        ).pack(side="left", padx=(4, 0))