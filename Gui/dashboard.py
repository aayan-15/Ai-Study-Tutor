from datetime import datetime, timedelta
import tkinter.font as tkfont

import customtkinter as ctk

from Core.task_manager import TaskManager
from Core.subject_manager import SubjectManager
from Core.activity import ActivityManager
from Core.quiz_history import QuizHistory
from Gui.planner import PlannerFrame
from Gui.progress import ProgressFrame
from Gui.sidebar import Sidebar
from Gui.subjects import SubjectsFrame
from Gui.activity import ActivityFrame
from Gui.ai_tutor import AITutorFrame
from Gui.pdf_assistant import PDFAssistantFrame
from Gui.quiz import QuizFrame


COLORS = {
    "bg": "#F5F7FA",
    "surface": "#FFFFFF",
    "border": "#DDE2EA",
    "text": "#1B2333",
    "muted": "#566074",          # 6:1 on white
    "accent": "#2F55D4",         # 6.5:1 on white
    "accent_hover": "#2546B5",
    "hover": "#EEF1F6",
    "row": "#F8F9FC",
    "danger": "#B42318",
    "danger_bg": "#FEF3F2",
    "danger_border": "#FDA29B",
    "track": "#E3E8F0",
}

SPACE = {1: 4, 2: 8, 3: 12, 4: 16, 6: 24, 8: 32}

RADIUS = 10

FONT = {
    "caption": 12,
    "body": 14,
    "title": 16,
    "heading": 20,
    "display": 28,
}

CONTROL_HEIGHT = 36
RECENT_ACTIVITY_LIMIT = 7


# Theme
# One neutral ramp, three text roles, one accent (fountain pen ink).
# Move this block to Gui/theme.py and import it in the sidebar and other
# pages so the whole app shares one palette.
BG = "#FAFAFA"           # page
CARD = "#FFFFFF"         # raised surface
RAISED = "#F4F4F5"       # hover, active row
HAIRLINE = "#EBEBEB"     # borders and dividers
TRACK = "#E7E7E9"        # empty part of the syllabus bar

TEXT = "#171717"         # primary
TEXT_2 = "#525252"       # secondary
MUTED = "#737373"        # meta, captions

ACCENT = "#0F766E"       # ink teal, 5.4:1 with white text
ACCENT_HOVER = "#115E59"

PAGE_X = 32              # page side padding
GAP = 24                 # space between sections and between cards
CARD_PAD = 24            # padding inside cards
RADIUS = 12              # card radius

UI_FONTS = ["Inter", "Segoe UI Variable Text", "Segoe UI",
            "SF Pro Text", "Helvetica Neue", "DejaVu Sans"]
MONO_FONTS = ["JetBrains Mono", "Cascadia Mono", "Consolas",
              "SF Mono", "Menlo", "DejaVu Sans Mono"]


def _pick_family(candidates):
    available = set(tkfont.families())
    return next((name for name in candidates if name in available),
                "TkDefaultFont")


def _format_time(value):
    """Turn a stored timestamp into 'Today, 14:05' or '24 Nov, 09:30'."""
    if not value:
        return ""
    try:
        moment = datetime.fromisoformat(str(value))
    except ValueError:
        return str(value)

    today = datetime.now().date()
    clock = moment.strftime("%H:%M")
    if moment.date() == today:
        return f"Today, {clock}"
    if moment.date() == today - timedelta(days=1):
        return f"Yesterday, {clock}"
    return f"{moment.day} {moment.strftime('%b')}, {clock}"


class DashboardFrame(ctk.CTkFrame):

    def __init__(self, parent, user, on_logout):
        super().__init__(parent, corner_radius=0, fg_color=BG)

        self.user = user
        self.on_logout = on_logout

        self.subject_manager = SubjectManager()
        self.activity_manager = ActivityManager()
        self.task_manager = TaskManager()
        self.quiz_history = QuizHistory()

        ui = _pick_family(UI_FONTS)
        mono = _pick_family(MONO_FONTS)
        self.fonts = {
            "title": ctk.CTkFont(family=ui, size=28),
            "heading": ctk.CTkFont(family=ui, size=16, weight="bold"),
            "body": ctk.CTkFont(family=ui, size=14),
            "small": ctk.CTkFont(family=ui, size=13),
            "figure": ctk.CTkFont(family=ui, size=30),
            "hero": ctk.CTkFont(family=ui, size=48),
            "meta": ctk.CTkFont(family=mono, size=12),
        }

        self.sidebar = Sidebar(self, self.show_page, self.on_logout)
        self.sidebar.pack(side="left", fill="y")

        self.content = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color=BG,
            scrollbar_button_color="#D4D4D8",
            scrollbar_button_hover_color="#A1A1AA"
        )
        self.content.pack(side="right", fill="both", expand=True)

        self.show_page("Dashboard")

    # Navigation

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page):
        self.clear_content()

        pages = {
            "My Subjects": lambda: SubjectsFrame(self.content, self.user),
            "AI Tutor": lambda: AITutorFrame(self.content, self.user),
            "All Activity": lambda: ActivityFrame(
                self.content, self.user,
                lambda: self.show_page("Dashboard")
            ),
            "Progress": lambda: ProgressFrame(self.content, self.user),
            "Study Planner": lambda: PlannerFrame(self.content, self.user),
            "PDF Assistant": lambda: PDFAssistantFrame(self.content, self.user),
            "Quizzes": lambda: QuizFrame(self.content, self.user),
        }

        if page == "Dashboard":
            self.show_dashboard()
        elif page in pages:
            pages[page]().pack(fill="both", expand=True)
        else:
            self.show_placeholder(page)

    # Building blocks

    def _card(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=RADIUS,
            border_width=1,
            border_color=HAIRLINE
        )

    # CTkLabel pads every label to 28px tall. Fixed heights per style
    # keep two-line rows and stat cards tight.
    LINE_HEIGHTS = {"title": 36, "heading": 24, "body": 20, "small": 20,
                    "figure": 36, "hero": 56, "meta": 16}

    def _label(self, parent, text, font, color=TEXT, **kwargs):
        return ctk.CTkLabel(
            parent, text=text, font=self.fonts[font],
            height=self.LINE_HEIGHTS[font],
            text_color=color, anchor="w", justify="left", **kwargs
        )

    # Dashboard

    def show_dashboard(self):
        username = self.user.get("username", "Student")
        user_email = self.user["email"]

        subjects = self.subject_manager.get_subjects(user_email)
        quiz_attempts = self.quiz_history.get_history(user_email)
        progress = self.subject_manager.get_overall_progress(user_email)
        tasks = self.task_manager.get_task_statistics(user_email)
        recent = self.activity_manager.get_recent_activities(
            user_email, limit=10
        )

        self._build_header(username)
        self._build_stats(len(subjects), progress, tasks, len(quiz_attempts))
        self._build_progress(progress)
        self._build_activity(recent)

    def _build_header(self, username):
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", padx=PAGE_X, pady=(40, GAP))

        self._label(header, "Overview", "title").pack(anchor="w")

        today = datetime.now()
        date_line = f"{today.strftime('%A')} {today.day} {today.strftime('%B')}"
        self._label(
            header, f"{date_line}  ·  {username}", "small", TEXT_2
        ).pack(anchor="w", pady=(4, 0))

    def _build_stats(self, total_subjects, progress, tasks, total_quizzes):
        row = ctk.CTkFrame(self.content, fg_color="transparent")
        row.pack(fill="x", padx=PAGE_X)
        # Cards in columns 0, 2, 4 with fixed gutters between them, so all
        # three come out the same width.
        row.grid_columnconfigure((0, 2, 4), weight=1, uniform="stats")
        row.grid_columnconfigure((1, 3), minsize=GAP)

        pending = tasks["pending_tasks"]
        done = tasks["completed_tasks"]

        stats = [
            ("Subjects", total_subjects,
             f"{progress['total_topics']} topics in total"),
            ("Tasks to do", pending,
             f"{done} of {done + pending} done"),
            ("Quizzes taken", total_quizzes, "All attempts"),
        ]

        for column, (label, value, caption) in enumerate(stats):
            card = self._card(row)
            card.grid(row=0, column=column * 2, sticky="nsew")
            self._label(card, label, "small", TEXT_2).pack(
                anchor="w", padx=CARD_PAD, pady=(20, 8))
            self._label(card, f"{value:,}", "figure").pack(
                anchor="w", padx=CARD_PAD)
            self._label(card, caption, "meta", MUTED).pack(
                anchor="w", padx=CARD_PAD, pady=(8, 20))

    def _build_progress(self, progress):
        card = self._card(self.content)
        card.pack(fill="x", padx=PAGE_X, pady=(GAP, 0))

        completed = progress["completed_topics"]
        total = progress["total_topics"]
        percent = round(progress["percentage"])

        self._label(card, "Syllabus progress", "heading").pack(
            anchor="w", padx=CARD_PAD, pady=(CARD_PAD, 12))

        figures = ctk.CTkFrame(card, fg_color="transparent")
        figures.pack(fill="x", padx=CARD_PAD)

        self._label(figures, f"{percent}%", "hero", ACCENT).pack(side="left")

        caption = (
            f"{completed} of {total} topics completed" if total
            else "Add topics to a subject to track them here"
        )
        self._label(figures, caption, "body", TEXT_2).pack(
            side="left", padx=(16, 0), pady=(16, 0))

        bar = ctk.CTkCanvas(card, height=12, bg=CARD,
                            highlightthickness=0, bd=0)
        bar.pack(fill="x", padx=CARD_PAD, pady=(16, CARD_PAD))
        bar.bind(
            "<Configure>",
            lambda event: self._draw_syllabus(bar, event.width,
                                              completed, total)
        )

    def _draw_syllabus(self, canvas, width, completed, total):
        """One tick per topic, filled in ink as it gets done."""
        canvas.delete("all")
        height = 12

        # Too many topics to show one by one: fall back to a plain bar.
        if total == 0 or width / total < 6:
            share = completed / total if total else 0
            canvas.create_rectangle(0, 0, width, height,
                                    fill=TRACK, width=0)
            canvas.create_rectangle(0, 0, width * share, height,
                                    fill=ACCENT, width=0)
            return

        gap = 3 if width / total >= 10 else 2
        segment = (width - gap * (total - 1)) / total
        for index in range(total):
            x0 = index * (segment + gap)
            color = ACCENT if index < completed else TRACK
            canvas.create_rectangle(x0, 0, x0 + segment, height,
                                    fill=color, width=0)


    def _build_activity(self, activities):
        card = self._card(self.content)
        card.pack(fill="x", padx=PAGE_X, pady=(GAP, 40))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=CARD_PAD, pady=(20, 8))

        self._label(header, "Recent activity", "heading").pack(side="left")

        ctk.CTkButton(
            header,
            text="View all",
            font=self.fonts["small"],
            width=0,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            hover_color=RAISED,
            text_color=ACCENT,
            command=lambda: self.show_page("All Activity")
        ).pack(side="right")

        if not activities:
            self._label(card, "No activity yet", "body").pack(
                anchor="w", padx=CARD_PAD, pady=(8, 4))
            self._label(
                card, "Add a subject or a topic and it will show up here",
                "small", MUTED
            ).pack(anchor="w", padx=CARD_PAD, pady=(0, CARD_PAD))
            return

        for index, activity in enumerate(activities):
            if index:
                ctk.CTkFrame(card, height=1, corner_radius=0,
                             fg_color=HAIRLINE).pack(
                    fill="x", padx=CARD_PAD)

            row = ctk.CTkFrame(card, fg_color="transparent")
            last = index == len(activities) - 1
            row.pack(fill="x", padx=CARD_PAD, pady=(12, 20 if last else 12))
            row.grid_columnconfigure(0, weight=1)

            self._label(row, activity["item_name"], "body").grid(
                row=0, column=0, sticky="w")

            secondary = activity["action"]
            if activity.get("details"):
                secondary += f"  ·  {activity['details']}"
            self._label(row, secondary, "small", TEXT_2).grid(
                row=1, column=0, sticky="w", pady=(4, 0))

            self._label(
                row, _format_time(activity.get("created_at")), "meta", MUTED
            ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(16, 0))


    # Pages that are not built yet

    def show_placeholder(self, page):
        self._label(self.content, page, "title").pack(pady=(160, 8))
        self._label(
            self.content, "Not available yet", "body", MUTED
        ).pack()