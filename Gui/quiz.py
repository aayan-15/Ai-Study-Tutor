import threading

import customtkinter as ctk

from Core.quiz_manager import QuizManager
from Core.quiz_result import QuizResult
from Core.quiz_history import QuizHistory
from Core.subject_manager import SubjectManager
from Core.topics import TopicManager
from Gui import theme as t


WRAP = 760  # wrap width for questions, options and explanations


class QuizFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, corner_radius=0, fg_color=t.BG)

        self.user = user
        self.user_email = user["email"]

        self.quiz_manager = QuizManager()
        self.history_manager = QuizHistory()
        self.subject_manager = SubjectManager()
        self.topic_manager = TopicManager()

        self.quiz = None
        self.user_answers = []
        self.current_question = 0
        self.selected_answer = None
        self.answer_var = None
        self.option_rows = {}

        self.subjects = []
        self.topics = []

        self.show_setup()

    # Shared pieces

    def clear_interface(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_heading(self, title, description, description_color=None):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.PAGE_X, pady=(40, t.GAP))

        t.label(header, title, "title").pack(anchor="w")
        self.heading_note = t.label(header, description, "small",
                                    description_color or t.TEXT_2)
        self.heading_note.pack(anchor="w", pady=(4, 0))
        return header

    def _field(self, parent, column, caption, widget_factory, pad_right=12):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=column, sticky="ew", padx=(0, pad_right))
        t.label(box, caption, "small", t.TEXT_2).pack(anchor="w",
                                                      pady=(0, 8))
        widget = widget_factory(box)
        widget.pack(fill="x")
        return widget

    def _combo(self, parent, values, command=None):
        return ctk.CTkComboBox(
            parent,
            values=values,
            height=40,
            corner_radius=t.CONTROL_RADIUS,
            border_width=1,
            border_color=t.FIELD_BORDER,
            button_color=t.FIELD_BORDER,
            button_hover_color="#D4D4D8",
            fg_color=t.CARD,
            text_color=t.TEXT,
            dropdown_fg_color=t.CARD,
            dropdown_hover_color=t.RAISED,
            dropdown_text_color=t.TEXT,
            font=t.fonts()["body"],
            dropdown_font=t.fonts()["body"],
            state="readonly",
            command=command
        )

    def _show_message(self, label, text, color=t.NEGATIVE, **pack):
        """Status line that is hidden while empty."""
        text = (text or "").strip().rstrip("!.")
        if not text:
            label.pack_forget()
            return
        label.configure(text=text, text_color=color)
        label.pack(anchor="w", **pack)

    # Setup screen

    def show_setup(self):
        self.clear_interface()

        self.create_heading(
            "Quizzes",
            "Multiple choice practice generated from your own subjects "
            "and topics"
        )

        self.subjects = self.subject_manager.get_subjects(self.user_email)

        setup_card = t.card(self)
        setup_card.pack(fill="x", padx=t.PAGE_X)

        t.label(setup_card, "New quiz", "heading").pack(
            anchor="w", padx=t.CARD_PAD, pady=(t.CARD_PAD, 16))

        fields = ctk.CTkFrame(setup_card, fg_color="transparent")
        fields.pack(fill="x", padx=t.CARD_PAD, pady=(0, t.CARD_PAD))
        fields.grid_columnconfigure((0, 1), weight=1, uniform="pick")

        subject_names = [subject["name"] for subject in self.subjects]
        if not subject_names:
            subject_names = ["No subjects yet"]

        self.subject_combo = self._field(
            fields, 0, "Subject",
            lambda box: self._combo(box, subject_names,
                                    self.on_subject_change)
        )
        self.subject_combo.set(subject_names[0])

        self.topic_combo = self._field(
            fields, 1, "Topic",
            lambda box: self._combo(box, ["Choose a subject first"])
        )
        self.topic_combo.set("Choose a subject first")

        self.question_count_var = ctk.StringVar(value="5")
        self.question_count_entry = self._field(
            fields, 2, "Questions",
            lambda box: t.entry(box, "5", width=96,
                                textvariable=self.question_count_var)
        )
        self.question_count_entry.bind("<Return>",
                                       lambda event: self.generate_quiz())

        # Button lines up with the inputs, under an empty caption row
        button_box = ctk.CTkFrame(fields, fg_color="transparent")
        button_box.grid(row=0, column=3, sticky="s")
        self.generate_button = t.primary_button(
            button_box, "Generate quiz", self.generate_quiz, width=144)
        self.generate_button.pack()

        self.message_label = t.label(setup_card, "", "small",
                                     wraplength=WRAP)

        if self.subjects:
            self.on_subject_change(subject_names[0])
        else:
            self.subject_combo.configure(state="disabled")
            self.topic_combo.configure(state="disabled")
            t.set_primary_enabled(self.generate_button, False)
            self._show_message(
                self.message_label,
                "Add a subject and a few topics on the Subjects page first",
                t.TEXT_2, padx=t.CARD_PAD, pady=(0, t.CARD_PAD)
            )

    def on_subject_change(self, selected_subject):
        subject = next(
            (item for item in self.subjects
             if item["name"] == selected_subject),
            None
        )

        self.topics = (
            self.topic_manager.get_topics(subject["id"], self.user_email)
            if subject else []
        )
        topic_names = [topic["name"] for topic in self.topics]

        if topic_names:
            self.topic_combo.configure(values=topic_names, state="readonly")
            self.topic_combo.set(topic_names[0])
            t.set_primary_enabled(self.generate_button, True)
            self._show_message(self.message_label, "")
        else:
            self.topic_combo.configure(values=["No topics yet"],
                                       state="disabled")
            self.topic_combo.set("No topics yet")
            t.set_primary_enabled(self.generate_button, False)
            self._show_message(
                self.message_label,
                f"{selected_subject} has no topics yet. Add some on the "
                f"Subjects page",
                t.TEXT_2, padx=t.CARD_PAD, pady=(0, t.CARD_PAD)
            )

    def generate_quiz(self):
        def fail(text):
            self._show_message(self.message_label, text, t.NEGATIVE,
                               padx=t.CARD_PAD, pady=(0, t.CARD_PAD))

        if not self.subjects:
            fail("Add a subject before generating a quiz")
            return

        subject = next(
            (item for item in self.subjects
             if item["name"] == self.subject_combo.get()),
            None
        )
        if not subject:
            fail("Choose a subject")
            return

        topic = next(
            (item for item in self.topics
             if item["name"] == self.topic_combo.get()),
            None
        )
        if not topic:
            fail("Choose a topic")
            return

        try:
            number_of_questions = int(self.question_count_var.get().strip())
            if number_of_questions <= 0:
                raise ValueError
        except ValueError:
            fail("Questions needs a whole number, like 5 or 10")
            return

        self.generate_button.configure(text="Generating")
        t.set_primary_enabled(self.generate_button, False)
        self._show_message(
            self.message_label,
            f"Writing {number_of_questions} questions on {topic['name']}. "
            f"This takes a few seconds",
            t.TEXT_2, padx=t.CARD_PAD, pady=(0, t.CARD_PAD)
        )

        threading.Thread(
            target=self._generate_in_background,
            args=(subject["name"], topic["name"], number_of_questions),
            daemon=True
        ).start()

    def _generate_in_background(self, subject_name, topic_name, count):
        try:
            quiz = self.quiz_manager.generate_quiz(subject_name, topic_name,
                                                   count)
            error = None if quiz else (
                self.quiz_manager.last_error
                or "Couldn't generate the quiz. Try again"
            )
        except Exception as exc:
            quiz, error = None, f"Something went wrong: {exc}"

        self.after(0, lambda: self._finish_generation(quiz, error))

    def _finish_generation(self, quiz, error):
        if not self.winfo_exists() or not self.generate_button.winfo_exists():
            return

        if error:
            self.generate_button.configure(text="Generate quiz")
            t.set_primary_enabled(self.generate_button, True)
            self._show_message(self.message_label, error, t.NEGATIVE,
                               padx=t.CARD_PAD, pady=(0, t.CARD_PAD))
            return

        self.quiz = quiz
        self.user_answers = [None for _ in self.quiz["questions"]]
        self.current_question = 0
        self.show_question()

    # Question screen

    def show_question(self):
        self.clear_interface()

        questions = self.quiz["questions"]
        question = questions[self.current_question]
        total = len(questions)
        number = self.current_question + 1

        self.create_heading(
            self.quiz["topic"],
            f"{self.quiz['subject']}  ·  Question {number} of {total}"
        )

        card = t.card(self)
        card.pack(fill="x", padx=t.PAGE_X)

        # One tick per question, filled as you answer
        answered = sum(answer is not None for answer in self.user_answers)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=t.CARD_PAD, pady=(t.CARD_PAD, 0))
        t.tick_bar(top, answered, total, height=8).pack(fill="x")
        t.label(top, f"{answered} of {total} answered", "meta",
                t.MUTED).pack(anchor="w", pady=(8, 0))

        t.label(card, question["question"], "question",
                wraplength=WRAP, height=0).pack(
            anchor="w", padx=t.CARD_PAD, pady=(t.GAP, 20))

        # Options as full-width rows you can click anywhere on
        self.answer_var = ctk.StringVar(
            value=self.user_answers[self.current_question] or ""
        )
        self.option_rows = {}
        options = ctk.CTkFrame(card, fg_color="transparent")
        options.pack(fill="x", padx=t.CARD_PAD, pady=(0, t.CARD_PAD))
        for key, option in question["options"].items():
            self._option_row(options, key, option)
        self._style_options()

        # Navigation
        navigation = ctk.CTkFrame(self, fg_color="transparent")
        navigation.pack(fill="x", padx=t.PAGE_X, pady=(t.GAP, 40))

        if self.current_question > 0:
            t.secondary_button(navigation, "Previous",
                               self.previous_question,
                               width=112).pack(side="left")

        last = self.current_question == total - 1
        self.next_button = t.primary_button(
            navigation,
            "Submit quiz" if last else "Next",
            self.submit_quiz if last else self.next_question,
            width=128
        )
        self.next_button.pack(side="right")

        self.nav_message = t.label(navigation, "", "small")
        self._update_next_button()

    def _option_row(self, parent, key, text):
        row = ctk.CTkFrame(parent, fg_color=t.CARD,
                           corner_radius=t.CONTROL_RADIUS,
                           border_width=1, border_color=t.FIELD_BORDER,
                           cursor="hand2")
        row.pack(fill="x", pady=(0, 8))
        row.grid_columnconfigure(1, weight=1)

        key_label = t.label(row, key, "meta", t.MUTED, width=16,
                            cursor="hand2")
        key_label.grid(row=0, column=0, sticky="nw", padx=(16, 12),
                       pady=14)
        text_label = t.label(row, text, "body", wraplength=WRAP - 80,
                             height=0, cursor="hand2")
        text_label.grid(row=0, column=1, sticky="w", padx=(0, 16),
                        pady=12)

        for widget in (row, key_label, text_label):
            widget.bind("<Button-1>", lambda event, k=key: self._select(k))
            widget.bind("<Enter>", lambda event, k=key: self._hover(k, True))
            widget.bind("<Leave>", lambda event, k=key: self._hover(k, False))

        self.option_rows[key] = (row, key_label)

    def _select(self, key):
        self.answer_var.set(key)
        self.user_answers[self.current_question] = key
        self._style_options()
        self._update_next_button()
        self._show_message(self.nav_message, "")

    def _hover(self, key, inside):
        if key == self.answer_var.get():
            return
        row, _ = self.option_rows[key]
        row.configure(fg_color=t.RAISED if inside else t.CARD)

    def _style_options(self):
        selected = self.answer_var.get()
        for key, (row, key_label) in self.option_rows.items():
            chosen = key == selected
            row.configure(
                fg_color=t.ACCENT_SOFT if chosen else t.CARD,
                border_color=t.ACCENT if chosen else t.FIELD_BORDER
            )
            key_label.configure(text_color=t.ACCENT if chosen else t.MUTED)

    def _update_next_button(self):
        t.set_primary_enabled(self.next_button, bool(self.answer_var.get()))

    def save_current_answer(self):
        answer = self.answer_var.get().strip()
        if not answer:
            return False
        self.user_answers[self.current_question] = answer
        return True

    def next_question(self):
        if not self.save_current_answer():
            return
        self.current_question += 1
        self.show_question()

    def previous_question(self):
        if self.answer_var.get().strip():
            self.save_current_answer()
        self.current_question -= 1
        self.show_question()

    def submit_quiz(self):
        if not self.save_current_answer():
            self._show_message(self.nav_message, "Pick an answer first",
                               side="right", padx=(0, 16), pady=10)
            return

        missing = [str(index + 1)
                   for index, answer in enumerate(self.user_answers)
                   if answer is None]
        if missing:
            self._show_message(
                self.nav_message,
                f"Answer question {', '.join(missing)} before submitting",
                side="right", padx=(0, 16), pady=10
            )
            return

        result = QuizResult.calculate(self.quiz, self.user_answers)

        try:
            self.history_manager.save_result(result, self.user_email)
        except Exception:
            self.show_result_content(result, save_error=True)
            return

        self.show_result_content(result)

    # Results screen

    def show_result_content(self, result, save_error=False):
        self.clear_interface()

        if save_error:
            self.create_heading(
                result["topic"],
                f"{result['subject']}  ·  This result could not be saved "
                f"to your history",
                t.NEGATIVE
            )
        else:
            self.create_heading(
                result["topic"],
                f"{result['subject']}  ·  Saved to your quiz history"
            )

        # Summary: the score is the moment on this screen
        summary = t.card(self)
        summary.pack(fill="x", padx=t.PAGE_X)

        score = ctk.CTkFrame(summary, fg_color="transparent")
        score.pack(fill="x", padx=t.CARD_PAD, pady=(t.CARD_PAD, 0))

        percent = round(float(result["percentage"]))
        t.label(score, f"{percent}%", "hero", t.ACCENT).pack(side="left")

        words = ctk.CTkFrame(score, fg_color="transparent")
        words.pack(side="left", padx=(20, 0), pady=(8, 0))
        t.label(words, result["remark"].rstrip("!."), "body").pack(
            anchor="w")
        t.label(
            words,
            f"{result['correct']} of {result['total_questions']} correct"
            f"  ·  {result['wrong']} wrong",
            "meta", t.MUTED
        ).pack(anchor="w", pady=(4, 0))

        # One tick per question: ink for right, red for wrong
        colors = [t.ACCENT if item["status"] == "Correct" else t.NEGATIVE
                  for item in result["review"]]
        t.tick_bar(summary, 0, len(colors), height=8,
                   colors=colors).pack(fill="x", padx=t.CARD_PAD,
                                       pady=(16, 0))

        if result["weak_topics"]:
            t.divider(summary, padx=t.CARD_PAD, pady=(20, 16))
            t.label(summary, "Practice next", "small", t.TEXT_2).pack(
                anchor="w", padx=t.CARD_PAD)
            t.label(summary, ", ".join(result["weak_topics"]), "body",
                    wraplength=WRAP, height=0).pack(
                anchor="w", padx=t.CARD_PAD, pady=(4, t.CARD_PAD))
        else:
            ctk.CTkFrame(summary, height=t.CARD_PAD,
                         fg_color="transparent").pack()

        # Answer review
        t.label(self, "Answer review", "heading").pack(
            anchor="w", padx=t.PAGE_X, pady=(32, 12))

        review = t.card(self)
        review.pack(fill="x", padx=t.PAGE_X)

        for index, item in enumerate(result["review"], start=1):
            if index > 1:
                t.divider(review, padx=t.CARD_PAD)
            self._review_row(review, index, item)

        # Next step
        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=t.PAGE_X, pady=(t.GAP, 40))
        t.primary_button(buttons, "New quiz", self.show_setup,
                         width=128).pack(side="left")

    def _review_row(self, parent, index, item):
        correct = item["status"] == "Correct"
        question = self.quiz["questions"][index - 1]

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=t.CARD_PAD, pady=20)
        row.grid_columnconfigure(1, weight=1)

        t.label(row, f"{index:>2}", "meta", t.MUTED, width=24).grid(
            row=0, column=0, sticky="nw", pady=(2, 0))

        body = ctk.CTkFrame(row, fg_color="transparent")
        body.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        status = t.label(body, "Correct" if correct else "Wrong", "meta",
                         t.POSITIVE if correct else t.NEGATIVE)
        status.pack(anchor="w")

        t.label(body, item["question"], "body", wraplength=WRAP,
                height=0).pack(anchor="w", pady=(4, 8))

        user_answer = item["user_answer"]
        user_text = question["options"].get(user_answer, "Not answered")
        t.label(
            body, f"Your answer  {user_answer}. {user_text}", "small",
            t.TEXT_2 if correct else t.NEGATIVE, wraplength=WRAP, height=0
        ).pack(anchor="w")

        if not correct:
            correct_answer = item["correct_answer"]
            correct_text = question["options"].get(correct_answer, "")
            t.label(
                body, f"Correct answer  {correct_answer}. {correct_text}",
                "small", t.POSITIVE, wraplength=WRAP, height=0
            ).pack(anchor="w", pady=(4, 0))

        if item.get("explanation"):
            t.label(body, item["explanation"], "small", t.MUTED,
                    wraplength=WRAP, height=0).pack(anchor="w",
                                                    pady=(8, 0))