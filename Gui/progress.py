
import customtkinter as ctk

from Core.subject_manager import SubjectManager
from Core.topics import TopicManager
from Core.progress_planner import ProgressPlanner


class ProgressFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color="#F4F6FA"
        )

        self.user = user
        self.user_email = user["email"]

        self.subject_manager = SubjectManager()
        self.topic_manager = TopicManager()
        self.progress_planner = ProgressPlanner()

        self.build_interface()

    def create_stat_item(self, parent, title, value):

        item = ctk.CTkFrame(
            parent,
            fg_color="#F4F6FA",
            corner_radius=8
        )

        item.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        ctk.CTkLabel(
            item,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="#778195"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            item,
            text=str(value),
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color="#3157D5"
        ).pack(pady=(0, 15))

    def build_interface(self):

        # Get progress data
        dashboard_data = self.progress_planner.get_dashboard_progress(
            self.user_email
        )

        progress = dashboard_data["learning_progress"]
        quiz_summary = dashboard_data["quiz_summary"]
        topic_performance = dashboard_data["topic_performance"]
        weak_topics = dashboard_data["weak_topics"]
        pending_topics = dashboard_data["pending_topics"]

        # Header
        ctk.CTkLabel(
            self,
            text="Learning Progress",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=35, pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="Track your learning progress and quiz performance.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(anchor="w", padx=35, pady=(0, 20))

        # Overall learning statistics
        stats_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        stats_card.pack(
            fill="x",
            padx=35,
            pady=(0, 20)
        )

        stats_container = ctk.CTkFrame(
            stats_card,
            fg_color="transparent"
        )

        stats_container.pack(
            fill="x",
            padx=20,
            pady=20
        )

        stats = [
            ("Total Subjects", progress["total_subjects"]),
            ("Total Topics", progress["total_topics"]),
            ("Completed Topics", progress["completed_topics"]),
            ("Overall Progress", f'{progress["percentage"]}%')
        ]

        for title, value in stats:
            self.create_stat_item(
                stats_container,
                title,
                value
            )

        # Main scrollable content
        content_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        content_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 10)
        )

        # Subject-wise progress
        ctk.CTkLabel(
            content_container,
            text="Subject-wise Progress",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=10, pady=(5, 10))

        subjects = self.subject_manager.get_subjects(
            self.user_email
        )

        if not subjects:

            ctk.CTkLabel(
                content_container,
                text="No subjects available yet.",
                font=ctk.CTkFont(size=14),
                text_color="#8993A5"
            ).pack(pady=25)

        for subject in subjects:

            subject_progress = self.topic_manager.get_subject_progress(
                subject["id"],
                self.user_email
            )

            card = ctk.CTkFrame(
                content_container,
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

            ctk.CTkLabel(
                card,
                text=subject["name"],
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#202938"
            ).pack(
                anchor="w",
                padx=18,
                pady=(15, 5)
            )

            ctk.CTkLabel(
                card,
                text=(
                    f'{subject_progress["completed_topics"]} of '
                    f'{subject_progress["total_topics"]} topics completed'
                ),
                font=ctk.CTkFont(size=12),
                text_color="#778195"
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 8)
            )

            bar = ctk.CTkProgressBar(
                card,
                height=10
            )

            bar.pack(
                fill="x",
                padx=18,
                pady=(0, 8)
            )

            bar.set(
                subject_progress["percentage"] / 100
            )

            ctk.CTkLabel(
                card,
                text=f'{subject_progress["percentage"]}% completed',
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#3157D5"
            ).pack(
                anchor="e",
                padx=18,
                pady=(0, 15)
            )

        # Quiz performance summary
        ctk.CTkLabel(
            content_container,
            text="Quiz Performance",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=10,
            pady=(25, 10)
        )

        quiz_card = ctk.CTkFrame(
            content_container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        quiz_card.pack(
            fill="x",
            padx=10,
            pady=(0, 15)
        )

        quiz_container = ctk.CTkFrame(
            quiz_card,
            fg_color="transparent"
        )

        quiz_container.pack(
            fill="x",
            padx=15,
            pady=15
        )

        quiz_stats = [
            ("Total Attempts", quiz_summary["total_attempts"]),
            ("Average Score", f'{quiz_summary["average_score"]}%'),
            ("Best Score", f'{quiz_summary["best_score"]}%'),
            ("Latest Score", f'{quiz_summary["latest_score"]}%')
        ]

        for title, value in quiz_stats:
            self.create_stat_item(
                quiz_container,
                title,
                value
            )

        # Topic-wise quiz performance
        ctk.CTkLabel(
            content_container,
            text="Topic-wise Quiz Performance",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=10,
            pady=(10, 10)
        )

        if topic_performance:

            for item in topic_performance:

                card = ctk.CTkFrame(
                    content_container,
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

                ctk.CTkLabel(
                    card,
                    text=item["topic"],
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#202938"
                ).pack(
                    anchor="w",
                    padx=18,
                    pady=(12, 3)
                )

                ctk.CTkLabel(
                    card,
                    text=f'Subject: {item["subject"]}',
                    font=ctk.CTkFont(size=12),
                    text_color="#778195"
                ).pack(
                    anchor="w",
                    padx=18,
                    pady=(0, 5)
                )

                ctk.CTkLabel(
                    card,
                    text=(
                        f'Average: {item["average_score"]}%   |   '
                        f'Latest: {item["latest_score"]}%   |   '
                        f'Attempts: {item["total_attempts"]}'
                    ),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#3157D5"
                ).pack(
                    anchor="w",
                    padx=18,
                    pady=(0, 12)
                )

        else:

            ctk.CTkLabel(
                content_container,
                text="No quiz attempts yet. Take a quiz to see your performance.",
                font=ctk.CTkFont(size=13),
                text_color="#8993A5"
            ).pack(
                anchor="w",
                padx=15,
                pady=15
            )

        # Weak topics
        ctk.CTkLabel(
            content_container,
            text="Weak Topics",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=10,
            pady=(20, 10)
        )

        weak_card = ctk.CTkFrame(
            content_container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        weak_card.pack(
            fill="x",
            padx=10,
            pady=(0, 15)
        )

        if weak_topics:

            for item in weak_topics:

                topic_item = ctk.CTkFrame(
                    weak_card,
                    fg_color="#FFF4F2",
                    corner_radius=8
                )

                topic_item.pack(
                    fill="x",
                    padx=15,
                    pady=6
                )

                ctk.CTkLabel(
                    topic_item,
                    text=item["topic"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#B54735"
                ).pack(
                    anchor="w",
                    padx=15,
                    pady=(10, 3)
                )

                ctk.CTkLabel(
                    topic_item,
                    text=(
                        f'Subject: {item["subject"]}   |   '
                        f'Average Score: {item["average_score"]}%'
                    ),
                    font=ctk.CTkFont(size=12),
                    text_color="#778195"
                ).pack(
                    anchor="w",
                    padx=15,
                    pady=(0, 10)
                )

        else:

            ctk.CTkLabel(
                weak_card,
                text="Great work! No weak topics detected.",
                font=ctk.CTkFont(size=13),
                text_color="#238636"
            ).pack(
                anchor="w",
                padx=20,
                pady=18
            )

        # Pending learning topics
        ctk.CTkLabel(
            content_container,
            text="Topics That Need Attention",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=10,
            pady=(20, 10)
        )

        pending_card = ctk.CTkFrame(
            content_container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        pending_card.pack(
            fill="x",
            padx=10,
            pady=(0, 25)
        )

        if pending_topics:

            for topic in pending_topics:

                item = ctk.CTkFrame(
                    pending_card,
                    fg_color="#F4F6FA",
                    corner_radius=8
                )

                item.pack(
                    fill="x",
                    padx=15,
                    pady=5
                )

                ctk.CTkLabel(
                    item,
                    text=topic["name"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#202938"
                ).pack(
                    anchor="w",
                    padx=15,
                    pady=(10, 2)
                )

                ctk.CTkLabel(
                    item,
                    text=f'Subject: {topic["subject_name"]}',
                    font=ctk.CTkFont(size=12),
                    text_color="#778195"
                ).pack(
                    anchor="w",
                    padx=15,
                    pady=(0, 10)
                )

        else:

            ctk.CTkLabel(
                pending_card,
                text="Excellent! You have completed all your topics.",
                font=ctk.CTkFont(size=13),
                text_color="#238636"
            ).pack(
                anchor="w",
                padx=20,
                pady=18
            )
