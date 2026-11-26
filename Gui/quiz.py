
import customtkinter as ctk

from Core.quiz_manager import QuizManager
from Core.quiz_result import QuizResult
from Core.quiz_history import QuizHistory
from Core.subject_manager import SubjectManager
from Core.topics import TopicManager


class QuizFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color="#F4F6FA"
        )

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

        self.subjects = []
        self.topics = []

        self.show_setup()

    # Clear existing interface
    def clear_interface(self):

        for widget in self.winfo_children():
            widget.destroy()

    # Page heading
    def create_heading(self, title, description):

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 5)
        )

        ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(
            anchor="w",
            padx=35,
            pady=(0, 20)
        )

    # Quiz setup screen
    def show_setup(self):

        self.clear_interface()

        self.create_heading(
            "AI Quiz Generator",
            "Test your knowledge with AI-generated quizzes."
        )

        self.subjects = self.subject_manager.get_subjects(
            self.user_email
        )

        setup_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        setup_card.pack(
            fill="x",
            padx=35,
            pady=10
        )

        ctk.CTkLabel(
            setup_card,
            text="Create a New Quiz",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=25,
            pady=(22, 18)
        )

        # Subject selection
        ctk.CTkLabel(
            setup_card,
            text="Select Subject",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=25,
            pady=(5, 7)
        )

        subject_names = [
            subject["name"] for subject in self.subjects
        ]

        if not subject_names:
            subject_names = ["No subjects available"]

        self.subject_combo = ctk.CTkComboBox(
            setup_card,
            values=subject_names,
            height=40,
            command=self.on_subject_change
        )

        self.subject_combo.pack(
            fill="x",
            padx=25,
            pady=(0, 18)
        )

        self.subject_combo.set(subject_names[0])

        if not self.subjects:
            self.subject_combo.configure(state="disabled")

        # Topic selection
        ctk.CTkLabel(
            setup_card,
            text="Select Topic",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 7)
        )

        self.topic_combo = ctk.CTkComboBox(
            setup_card,
            values=["Select a subject first"],
            height=40
        )

        self.topic_combo.pack(
            fill="x",
            padx=25,
            pady=(0, 18)
        )

        self.topic_combo.set("Select a subject first")

        # Load topics for initial subject
        if self.subjects:
            self.on_subject_change(subject_names[0])

        # Number of questions
        ctk.CTkLabel(
            setup_card,
            text="Number of MCQs",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 7)
        )

        self.question_count_var = ctk.StringVar(value="5")

        self.question_count_entry = ctk.CTkEntry(
            setup_card,
            textvariable=self.question_count_var,
            height=40,
            placeholder_text="Enter number of questions"
        )

        self.question_count_entry.pack(
            fill="x",
            padx=25,
            pady=(0, 18)
        )

        # Error / information message
        self.message_label = ctk.CTkLabel(
            setup_card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#D9534F",
            wraplength=650
        )

        self.message_label.pack(
            anchor="w",
            padx=25,
            pady=(0, 8)
        )

        # Generate button
        self.generate_button = ctk.CTkButton(
            setup_card,
            text="Generate Quiz",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.generate_quiz
        )

        self.generate_button.pack(
            anchor="w",
            padx=25,
            pady=(5, 25)
        )

    # Load topics when subject changes
    def on_subject_change(self, selected_subject):

        subject = next(
            (
                item for item in self.subjects
                if item["name"] == selected_subject
            ),
            None
        )

        if not subject:
            self.topics = []
            self.topic_combo.configure(
                values=["No topics available"]
            )
            self.topic_combo.set("No topics available")
            return

        self.topics = self.topic_manager.get_topics(
            subject["id"],
            self.user_email
        )

        topic_names = [
            topic["name"] for topic in self.topics
        ]

        if topic_names:
            self.topic_combo.configure(values=topic_names)
            self.topic_combo.set(topic_names[0])
        else:
            self.topic_combo.configure(
                values=["No topics available"]
            )
            self.topic_combo.set("No topics available")

    # Generate quiz using AI
    def generate_quiz(self):

        if not self.subjects:
            self.message_label.configure(
                text="Please add a subject before generating a quiz."
            )
            return

        selected_subject = self.subject_combo.get()
        selected_topic = self.topic_combo.get()

        subject = next(
            (
                item for item in self.subjects
                if item["name"] == selected_subject
            ),
            None
        )

        if not subject:
            self.message_label.configure(
                text="Please select a valid subject."
            )
            return

        topic = next(
            (
                item for item in self.topics
                if item["name"] == selected_topic
            ),
            None
        )

        if not topic:
            self.message_label.configure(
                text="Please add or select a valid topic."
            )
            return

        # Validate question count
        try:
            number_of_questions = int(
                self.question_count_var.get().strip()
            )

            if number_of_questions <= 0:
                raise ValueError

        except ValueError:
            self.message_label.configure(
                text="Please enter a valid positive whole number.",
                text_color="#D9534F"
            )
            return

        self.generate_button.configure(
            text="Generating...",
            state="disabled"
        )

        self.message_label.configure(
            text="Please wait while AI generates your quiz...",
            text_color="#3157D5"
        )

        self.update_idletasks()

        try:
            self.quiz = self.quiz_manager.generate_quiz(
                subject["name"],
                topic["name"],
                number_of_questions
            )

            if not self.quiz:
                error = (
                    self.quiz_manager.last_error
                    or "Quiz generation failed. Please try again."
                )

                self.message_label.configure(
                    text=error,
                    text_color="#D9534F"
                )

                return

            self.user_answers = [
                None for _ in self.quiz["questions"]
            ]

            self.current_question = 0

            self.show_question()

        except Exception as error:

            self.message_label.configure(
                text=f"An error occurred: {error}",
                text_color="#D9534F"
            )

        finally:

            if (
                self.winfo_exists()
                and self.generate_button.winfo_exists()
            ):
                self.generate_button.configure(
                    text="Generate Quiz",
                    state="normal"
                )

    # Display current question
    def show_question(self):

        self.clear_interface()

        questions = self.quiz["questions"]
        question = questions[self.current_question]

        total = len(questions)
        question_number = self.current_question + 1

        self.create_heading(
            "Your Quiz",
            f'{self.quiz["subject"]}  |  {self.quiz["topic"]}'
        )

        # Question information card
        card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        card.pack(
            fill="x",
            padx=35,
            pady=10
        )

        # Progress information
        ctk.CTkLabel(
            card,
            text=f"Question {question_number} of {total}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3157D5"
        ).pack(
            anchor="w",
            padx=25,
            pady=(22, 10)
        )

        progress_bar = ctk.CTkProgressBar(
            card,
            height=10
        )

        progress_bar.pack(
            fill="x",
            padx=25,
            pady=(0, 22)
        )

        progress_bar.set(question_number / total)

        # Question text
        ctk.CTkLabel(
            card,
            text=question["question"],
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#202938",
            wraplength=750,
            justify="left"
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 22)
        )

        # Answer options
        options_card = ctk.CTkFrame(
            card,
            fg_color="#F4F6FA",
            corner_radius=10
        )

        options_card.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        self.answer_var = ctk.StringVar(
            value=self.user_answers[self.current_question] or ""
        )

        for key, option in question["options"].items():

            ctk.CTkRadioButton(
                options_card,
                text=f"{key}. {option}",
                variable=self.answer_var,
                value=key,
                font=ctk.CTkFont(size=14),
                text_color="#202938",
                fg_color="#3157D5",
                hover_color="#2546B5"
            ).pack(
                anchor="w",
                padx=20,
                pady=13
            )

        # Navigation buttons
        navigation = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        navigation.pack(
            fill="x",
            padx=35,
            pady=20
        )

        if self.current_question > 0:

            ctk.CTkButton(
                navigation,
                text="Previous",
                width=120,
                height=40,
                fg_color="#E5E9F0",
                hover_color="#D5DAE4",
                text_color="#202938",
                command=self.previous_question
            ).pack(side="left")

        if self.current_question < total - 1:

            ctk.CTkButton(
                navigation,
                text="Next Question",
                width=140,
                height=40,
                command=self.next_question
            ).pack(side="right")

        else:

            ctk.CTkButton(
                navigation,
                text="Submit Quiz",
                width=140,
                height=40,
                fg_color="#238636",
                hover_color="#1B6E2B",
                command=self.submit_quiz
            ).pack(side="right")

    # Save current answer
    def save_current_answer(self):

        answer = self.answer_var.get().strip()

        if not answer:
            return False

        self.user_answers[self.current_question] = answer

        return True

    # Go to next question
    def next_question(self):

        if not self.save_current_answer():
            return

        self.current_question += 1
        self.show_question()

    # Go to previous question
    def previous_question(self):

        if self.answer_var.get().strip():
            self.save_current_answer()

        self.current_question -= 1
        self.show_question()

    # Submit and calculate quiz result
    def submit_quiz(self):

        if not self.save_current_answer():
            ctk.CTkLabel(
                self,
                text="Please select an answer before submitting.",
                text_color="#D9534F"
            ).pack(
                anchor="w",
                padx=35,
                pady=5
            )
            return

        if any(answer is None for answer in self.user_answers):
            ctk.CTkLabel(
                self,
                text="Please answer all questions before submitting.",
                text_color="#D9534F"
            ).pack(
                anchor="w",
                padx=35,
                pady=5
            )
            return

        result = QuizResult.calculate(
            self.quiz,
            self.user_answers
        )

        try:
            self.history_manager.save_result(
                result,
                self.user_email
            )

        except Exception:
            self.show_result_content(result, save_error=True)
            return

        self.show_result_content(result)

    # Display quiz results
    def show_result_content(self, result, save_error=False):

        self.clear_interface()

        self.create_heading(
            "Quiz Results",
            f'{result["subject"]}  |  {result["topic"]}'
        )

        if save_error:
            ctk.CTkLabel(
                self,
                text="Your result was calculated, but it could not be saved.",
                text_color="#D9534F",
                font=ctk.CTkFont(size=13)
            ).pack(
                anchor="w",
                padx=35,
                pady=5
            )

        # Result summary card
        summary = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        summary.pack(
            fill="x",
            padx=35,
            pady=10
        )

        ctk.CTkLabel(
            summary,
            text=f'{result["percentage"]}%',
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="#3157D5"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            summary,
            text=result["remark"],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#202938"
        ).pack(pady=(0, 18))

        stats = ctk.CTkFrame(
            summary,
            fg_color="transparent"
        )

        stats.pack(
            fill="x",
            padx=15,
            pady=(0, 20)
        )

        result_stats = [
            ("Total", result["total_questions"]),
            ("Correct", result["correct"]),
            ("Wrong", result["wrong"])
        ]

        for title, value in result_stats:

            item = ctk.CTkFrame(
                stats,
                fg_color="#F4F6FA",
                corner_radius=8
            )

            item.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            ctk.CTkLabel(
                item,
                text=title,
                font=ctk.CTkFont(size=12),
                text_color="#778195"
            ).pack(pady=(12, 3))

            ctk.CTkLabel(
                item,
                text=str(value),
                font=ctk.CTkFont(size=22, weight="bold"),
                text_color="#202938"
            ).pack(pady=(0, 12))

        # Weak topics
        if result["weak_topics"]:

            ctk.CTkLabel(
                self,
                text="Topics to Practice",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#B54735"
            ).pack(
                anchor="w",
                padx=35,
                pady=(15, 5)
            )

            ctk.CTkLabel(
                self,
                text=", ".join(result["weak_topics"]),
                font=ctk.CTkFont(size=13),
                text_color="#778195"
            ).pack(
                anchor="w",
                padx=35,
                pady=(0, 10)
            )

        # Answer review heading
        ctk.CTkLabel(
            self,
            text="Answer Review",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=35,
            pady=(20, 10)
        )

        review_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            height=350
        )

        review_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 10)
        )

        for index, item in enumerate(result["review"], start=1):

            card = ctk.CTkFrame(
                review_container,
                fg_color="#FFFFFF",
                corner_radius=10,
                border_width=1,
                border_color="#E5E9F0"
            )

            card.pack(
                fill="x",
                padx=10,
                pady=7
            )

            status_color = (
                "#238636"
                if item["status"] == "Correct"
                else "#D9534F"
            )

            ctk.CTkLabel(
                card,
                text=f'Question {index}  -  {item["status"]}',
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=status_color
            ).pack(
                anchor="w",
                padx=18,
                pady=(15, 7)
            )

            ctk.CTkLabel(
                card,
                text=item["question"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#202938",
                wraplength=750,
                justify="left"
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 10)
            )

            question = self.quiz["questions"][index - 1]

            user_answer = item["user_answer"]
            correct_answer = item["correct_answer"]

            user_text = question["options"].get(
                user_answer,
                "Not answered"
            )

            correct_text = question["options"].get(
                correct_answer,
                ""
            )

            ctk.CTkLabel(
                card,
                text=f"Your answer: {user_answer}. {user_text}",
                font=ctk.CTkFont(size=12),
                text_color=status_color,
                wraplength=750,
                justify="left"
            ).pack(
                anchor="w",
                padx=18,
                pady=3
            )

            ctk.CTkLabel(
                card,
                text=f"Correct answer: {correct_answer}. {correct_text}",
                font=ctk.CTkFont(size=12),
                text_color="#238636",
                wraplength=750,
                justify="left"
            ).pack(
                anchor="w",
                padx=18,
                pady=3
            )

            ctk.CTkLabel(
                card,
                text=f'Explanation: {item["explanation"]}',
                font=ctk.CTkFont(size=12),
                text_color="#778195",
                wraplength=750,
                justify="left"
            ).pack(
                anchor="w",
                padx=18,
                pady=(8, 15)
            )

        # Bottom buttons
        buttons = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=35,
            pady=20
        )

        ctk.CTkButton(
            buttons,
            text="Take Another Quiz",
            width=160,
            height=40,
            command=self.show_setup
        ).pack(side="left")

        if not save_error:

            ctk.CTkLabel(
                buttons,
                text="Result saved to your quiz history.",
                font=ctk.CTkFont(size=12),
                text_color="#238636"
            ).pack(
                side="right",
                padx=5
            )
