import customtkinter as ctk

from Core.subject_manager import SubjectManager
from Core.topics import TopicManager
from Core.progress_planner import ProgressPlanner
from Gui import theme as t


def pct(value):
    """One format for every percentage on the page: 67%, not 66.67%."""
    try:
        return f"{round(float(value))}%"
    except (TypeError, ValueError):
        return "–"


class ProgressFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, corner_radius=0, fg_color=t.BG)

        self.user = user
        self.user_email = user["email"]

        self.subject_manager = SubjectManager()
        self.topic_manager = TopicManager()
        self.progress_planner = ProgressPlanner()

        self.build_interface()

    # Shared pieces

    def _section_title(self, text, top=32):
        t.label(self, text, "heading").pack(
            anchor="w", padx=t.PAGE_X, pady=(top, 12))

    def _empty(self, parent, text):
        t.label(parent, text, "small", t.MUTED).pack(
            anchor="w", padx=t.CARD_PAD, pady=t.CARD_PAD)

    def create_stat_item(self, parent, column, title, value, caption=""):
        """Quiet stat: label, figure, optional caption. No accent."""
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=column, sticky="w")
        t.label(box, title, "small", t.TEXT_2).pack(anchor="w")
        t.label(box, str(value), "figure").pack(anchor="w", pady=(8, 0))
        if caption:
            t.label(box, caption, "meta", t.MUTED).pack(anchor="w",
                                                        pady=(8, 0))

    # Page

    def build_interface(self):
        data = self.progress_planner.get_dashboard_progress(self.user_email)

        progress = data["learning_progress"]
        quiz_summary = data["quiz_summary"]
        topic_performance = data["topic_performance"]
        weak_topics = data["weak_topics"]
        pending_topics = data["pending_topics"]

        subjects = self.subject_manager.get_subjects(self.user_email)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.PAGE_X, pady=(40, t.GAP))
        t.label(header, "Progress", "title").pack(anchor="w")
        count = progress["total_subjects"]
        t.label(
            header,
            f"Topics completed and quiz results across your {count} "
            f"{'subject' if count == 1 else 'subjects'}",
            "small", t.TEXT_2
        ).pack(anchor="w", pady=(4, 0))

        self._build_syllabus(progress, subjects)
        self._build_quiz_summary(quiz_summary)
        self._build_topic_table(topic_performance)
        self._build_attention(weak_topics, pending_topics)

    # Syllabus: overall figure plus one row per subject (the moment)

    def _build_syllabus(self, progress, subjects):
        card = t.card(self)
        card.pack(fill="x", padx=t.PAGE_X)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=t.CARD_PAD, pady=(t.CARD_PAD, 0))

        t.label(top, "Syllabus", "heading").pack(anchor="w",
                                                 pady=(0, 12))

        figures = ctk.CTkFrame(top, fg_color="transparent")
        figures.pack(fill="x")
        t.label(figures, pct(progress["percentage"]), "hero",
                t.ACCENT).pack(side="left")
        t.label(
            figures,
            f"{progress['completed_topics']} of {progress['total_topics']} "
            f"topics completed",
            "body", t.TEXT_2
        ).pack(side="left", padx=(16, 0), pady=(16, 0))

        t.tick_bar(top, progress["completed_topics"],
                   progress["total_topics"]).pack(fill="x", pady=(16, 0))

        t.divider(card, padx=t.CARD_PAD, pady=(t.GAP, 0))

        if not subjects:
            self._empty(card, "No subjects yet. Add one on the Subjects "
                              "page to start tracking")
            return

        rows = ctk.CTkFrame(card, fg_color="transparent")
        rows.pack(fill="x", padx=t.CARD_PAD, pady=(8, 16))
        rows.grid_columnconfigure(0, minsize=220)
        rows.grid_columnconfigure(1, weight=1)
        rows.grid_columnconfigure((2, 3), minsize=72)

        for index, subject in enumerate(subjects):
            sp = self.topic_manager.get_subject_progress(
                subject["id"], self.user_email)
            done, total = sp["completed_topics"], sp["total_topics"]

            t.label(rows, subject["name"], "body").grid(
                row=index, column=0, sticky="w", pady=8, padx=(0, 24))
            bar = t.tick_bar(rows, done, total, height=8)
            bar.grid(row=index, column=1, sticky="ew")
            t.label(rows, f"{done} of {total}" if total else "No topics",
                    "meta", t.MUTED,
                    anchor="e").grid(row=index, column=2, sticky="e")
            t.label(rows, pct(sp["percentage"]) if total else "–", "body",
                    anchor="e").grid(row=index, column=3, sticky="e")

    # Quizzes

    def _build_quiz_summary(self, summary):
        self._section_title("Quizzes")

        card = t.card(self)
        card.pack(fill="x", padx=t.PAGE_X)

        attempts = summary["total_attempts"]
        if not attempts:
            self._empty(card, "No quizzes taken yet. Results show up here "
                              "after your first one")
            return

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=t.CARD_PAD, pady=20)
        row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="quiz")

        stats = [
            ("Attempts", f"{attempts:,}"),
            ("Average score", pct(summary["average_score"])),
            ("Best score", pct(summary["best_score"])),
            ("Latest score", pct(summary["latest_score"])),
        ]
        for column, (title, value) in enumerate(stats):
            self.create_stat_item(row, column, title, value)

    def _build_topic_table(self, topic_performance):
        self._section_title("By topic", top=24)

        card = t.card(self)
        card.pack(fill="x", padx=t.PAGE_X)

        if not topic_performance:
            self._empty(card, "Take a quiz to see scores per topic")
            return

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=t.CARD_PAD, pady=(16, 8))
        table.grid_columnconfigure(0, weight=1)
        table.grid_columnconfigure((1, 2, 3), minsize=96)

        for column, title in enumerate(
                ["Topic", "Average", "Latest", "Attempts"]):
            t.label(table, title, "small_bold", t.MUTED,
                    anchor="w" if column == 0 else "e").grid(
                row=0, column=column, sticky="w" if column == 0 else "e",
                pady=(0, 8))

        for index, item in enumerate(topic_performance, start=1):
            line = tk_line(table)
            line.grid(row=index * 2 - 1, column=0, columnspan=4,
                      sticky="ew")

            name = ctk.CTkFrame(table, fg_color="transparent")
            name.grid(row=index * 2, column=0, sticky="w", pady=12)
            t.label(name, item["topic"], "body").pack(anchor="w")
            t.label(name, item["subject"], "small", t.MUTED).pack(
                anchor="w", pady=(2, 0))

            values = [pct(item["average_score"]), pct(item["latest_score"]),
                      f"{item['total_attempts']:,}"]
            for column, value in enumerate(values, start=1):
                t.label(table, value, "meta" if column == 3 else "body",
                        t.TEXT_2 if column == 3 else t.TEXT,
                        anchor="e").grid(row=index * 2, column=column,
                                         sticky="e")

    # What to work on next

    def _build_attention(self, weak_topics, pending_topics):
        self._section_title("Work on next")

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=t.PAGE_X, pady=(0, 40))
        row.grid_columnconfigure((0, 2), weight=1, uniform="next")
        row.grid_columnconfigure(1, minsize=t.GAP)

        # Weak quiz topics
        weak = t.card(row)
        weak.grid(row=0, column=0, sticky="nsew")
        t.label(weak, "Low quiz scores", "small_bold", t.TEXT_2).pack(
            anchor="w", padx=t.CARD_PAD, pady=(20, 4))

        if weak_topics:
            for index, item in enumerate(weak_topics):
                if index:
                    t.divider(weak, padx=t.CARD_PAD)
                self._attention_row(weak, item["topic"], item["subject"],
                                    pct(item["average_score"]), t.NEGATIVE,
                                    last=index == len(weak_topics) - 1)
        else:
            self._empty(weak, "No weak topics right now")

        # Topics not completed yet
        pending = t.card(row)
        pending.grid(row=0, column=2, sticky="nsew")
        t.label(pending, "Not completed yet", "small_bold", t.TEXT_2).pack(
            anchor="w", padx=t.CARD_PAD, pady=(20, 4))

        if pending_topics:
            for index, topic in enumerate(pending_topics):
                if index:
                    t.divider(pending, padx=t.CARD_PAD)
                self._attention_row(pending, topic["name"],
                                    topic["subject_name"],
                                    last=index == len(pending_topics) - 1)
        else:
            self._empty(pending, "Every topic is complete")

    def _attention_row(self, parent, title, subject, value=None,
                       value_color=t.TEXT, last=False):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", padx=t.CARD_PAD, pady=(12, 20 if last else 12))
        item.grid_columnconfigure(0, weight=1)

        t.label(item, title, "body").grid(row=0, column=0, sticky="w")
        t.label(item, subject, "small", t.MUTED).grid(
            row=1, column=0, sticky="w", pady=(2, 0))
        if value is not None:
            t.label(item, value, "body", value_color, anchor="e").grid(
                row=0, column=1, rowspan=2, sticky="e", padx=(16, 0))


def tk_line(parent):
    """1px divider that can be gridded (theme.divider packs)."""
    import tkinter
    return tkinter.Frame(parent, height=1, bg=t.HAIRLINE, bd=0,
                         highlightthickness=0)