
import customtkinter as ctk

from Core.subject_manager import SubjectManager
from Core.topics import TopicManager


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

        self.build_interface()

    def build_interface(self):

        # Header
        ctk.CTkLabel(
            self,
            text="Learning Progress",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=35, pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="Track your learning progress and topics that need attention.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(anchor="w", padx=35, pady=(0, 20))

        # Overall statistics
        progress = self.subject_manager.get_overall_progress(
            self.user_email
        )

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

            item = ctk.CTkFrame(
                stats_container,
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

        # Subject-wise progress
        ctk.CTkLabel(
            self,
            text="Subject-wise Progress",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=35, pady=(5, 10))

        subjects_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        subjects_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 10)
        )

        subjects = self.subject_manager.get_subjects(
            self.user_email
        )

        if not subjects:

            ctk.CTkLabel(
                subjects_container,
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
                subjects_container,
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

        # Pending topics
        pending_topics = self.topic_manager.get_pending_topics(
            self.user_email
        )

        pending_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        pending_card.pack(
            fill="x",
            padx=35,
            pady=(10, 25)
        )

        ctk.CTkLabel(
            pending_card,
            text="Topics That Need Attention",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
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
                pady=(0, 18)
            )
