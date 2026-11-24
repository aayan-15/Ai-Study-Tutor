from Core.task_manager import TaskManager
import customtkinter as ctk
from Gui.planner import PlannerFrame
from Core.subject_manager import SubjectManager
from Core.activity import ActivityManager
from Gui.progress import ProgressFrame
from Gui.sidebar import Sidebar
from Gui.subjects import SubjectsFrame
from Gui.activity import ActivityFrame
from Gui.ai_tutor import AITutorFrame
from Gui.pdf_assistant import PDFAssistantFrame





class DashboardFrame(ctk.CTkFrame):

    def __init__(self, parent, user, on_logout):
        super().__init__(parent, corner_radius=0)

        self.user = user
        self.on_logout = on_logout

        self.subject_manager = SubjectManager()
        self.activity_manager = ActivityManager()
        self.task_manager = TaskManager()

        self.configure(fg_color="#F4F6FA")

        # Sidebar
        self.sidebar = Sidebar(
            self,
            self.show_page,
            self.on_logout
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        # Main content area
        # Main content area
        self.content = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color="#F4F6FA",
            scrollbar_button_color="#A0AEC0",
            scrollbar_button_hover_color="#718096"
        )

        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.show_page("Dashboard")

    # Clear existing page
    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    # Page navigation
    def show_page(self, page):

        self.clear_content()

        if page == "Dashboard":
            self.show_dashboard()

        elif page == "My Subjects":

            subjects_frame = SubjectsFrame(
                self.content,
                self.user
            )

            subjects_frame.pack(
                fill="both",
                expand=True
            )

        elif page == "AI Tutor":
            self.clear_content()
            AITutorFrame(
            self.content,
            self.user
        ).pack(fill="both", expand=True)

        elif page == "All Activity":

            activity_frame = ActivityFrame(
                self.content,
                self.user,
                lambda: self.show_page("Dashboard")
            )

            activity_frame.pack(
                fill="both",
                expand=True
            )

        elif page == "Progress":

            progress_frame = ProgressFrame(
                self.content,
                self.user
            )

            progress_frame.pack(
                fill="both",
                expand=True
            )

        elif page == "Study Planner":

            planner_frame = PlannerFrame(
                self.content,
                self.user
            )

            planner_frame.pack(
                fill="both",
                expand=True
            )

        elif page == "PDF Assistant":

            pdf_frame = PDFAssistantFrame(
                self.content,
                self.user
        )

            pdf_frame.pack(
                fill="both",
                expand=True
            )

        else:
            self.show_placeholder(page)

    # Dashboard page
    def show_dashboard(self):

        username = self.user.get("username", "Student")
        user_email = self.user["email"]

        # Fetch subjects
        subjects = self.subject_manager.get_subjects(
            user_email
        )

        total_subjects = len(subjects)

        # Fetch overall progress
        overall_progress = self.subject_manager.get_overall_progress(
            user_email
        )

        # Header
        header = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 20)
        )

        ctk.CTkLabel(
            header,
            text=f"Welcome back, {username}!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Here's an overview of your learning progress.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(
            anchor="w",
            pady=(7, 0)
        )

        # Statistics cards
        cards_frame = ctk.CTkFrame(
            self.content,
            fg_color="transparent"
        )

        cards_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        task_statistics = self.task_manager.get_task_statistics(
            user_email
        )

        cards = [
            ("My Total Subjects", total_subjects, "Subjects added"),
            (
                "Study Tasks",
                task_statistics["pending_tasks"],
                f'{task_statistics["completed_tasks"]} completed'
            ),
            ("Quizzes Taken", 0, "Quizzes completed")
        ]

        for title, value, description in cards:

            card = ctk.CTkFrame(
                cards_frame,
                fg_color="#FFFFFF",
                corner_radius=12,
                border_width=1,
                border_color="#E5E9F0"
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=10,
                pady=10
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#657087"
            ).pack(
                anchor="w",
                padx=20,
                pady=(20, 5)
            )

            ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=30, weight="bold"),
                text_color="#3157D5"
            ).pack(
                anchor="w",
                padx=20
            )

            ctk.CTkLabel(
                card,
                text=description,
                font=ctk.CTkFont(size=12),
                text_color="#8993A5"
            ).pack(
                anchor="w",
                padx=20,
                pady=(5, 20)
            )

        # Overall Learning Progress
        progress_card = ctk.CTkFrame(
            self.content,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        progress_card.pack(
            fill="x",
            padx=35,
            pady=(10, 20)
        )

        ctk.CTkLabel(
            progress_card,
            text="Overall Learning Progress",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        ctk.CTkLabel(
            progress_card,
            text=(
                f"{overall_progress['completed_topics']} of "
                f"{overall_progress['total_topics']} topics completed"
            ),
            font=ctk.CTkFont(size=13),
            text_color="#778195"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        progress_bar = ctk.CTkProgressBar(
            progress_card,
            height=12
        )

        progress_bar.pack(
            fill="x",
            padx=20,
            pady=(0, 8)
        )

        progress_bar.set(
            overall_progress["percentage"] / 100
        )

        ctk.CTkLabel(
            progress_card,
            text=f"{overall_progress['percentage']}%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3157D5"
        ).pack(
            anchor="e",
            padx=20,
            pady=(0, 15)
        )

        # Recent Activity
        activity_frame = ctk.CTkFrame(
            self.content,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        activity_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(20, 30)
        )

        # Activity heading
        activity_header = ctk.CTkFrame(
            activity_frame,
            fg_color="transparent"
        )

        activity_header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            activity_header,
            text="Recent Activity",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#202938"
        ).pack(side="left")

        ctk.CTkButton(
            activity_header,
            text="View All",
            width=90,
            height=32,
            fg_color="#3157D5",
            hover_color="#2546B5",
            command=lambda: self.show_page("All Activity")
        ).pack(side="right")

        # Fetch latest 10 activities
        recent_activities = (
            self.activity_manager.get_recent_activities(
                user_email,
                limit=10
            )
        )

        activities_container = ctk.CTkScrollableFrame(
            activity_frame,
            fg_color="transparent",
            corner_radius=0
        )

        activities_container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        if recent_activities:

            for activity in recent_activities:

                item = ctk.CTkFrame(
                    activities_container,
                    fg_color="#F4F6FA",
                    corner_radius=8
                )

                item.pack(
                    fill="x",
                    padx=10,
                    pady=5
                )

                details = ctk.CTkFrame(
                    item,
                    fg_color="transparent"
                )

                details.pack(
                    fill="x",
                    padx=15,
                    pady=10
                )

                ctk.CTkLabel(
                    details,
                    text=(
                        f"{activity['action']}: "
                        f"{activity['item_name']}"
                    ),
                    font=ctk.CTkFont(
                        size=14,
                        weight="bold"
                    ),
                    text_color="#202938"
                ).pack(anchor="w")

                if activity.get("details"):

                    ctk.CTkLabel(
                        details,
                        text=activity["details"],
                        font=ctk.CTkFont(size=11),
                        text_color="#778195"
                    ).pack(
                        anchor="w",
                        pady=(3, 0)
                    )

                ctk.CTkLabel(
                    details,
                    text=activity.get("created_at", ""),
                    font=ctk.CTkFont(size=11),
                    text_color="#8993A5"
                ).pack(
                    anchor="w",
                    pady=(3, 0)
                )

        else:

            ctk.CTkLabel(
                activities_container,
                text="No recent activity yet.",
                font=ctk.CTkFont(size=14),
                text_color="#8993A5"
            ).pack(
                anchor="w",
                padx=10,
                pady=15
            )

            ctk.CTkLabel(
                activities_container,
                text="Add your first subject or topic to get started!",
                font=ctk.CTkFont(size=12),
                text_color="#8993A5"
            ).pack(
                anchor="w",
                padx=10,
                pady=(0, 15)
            )

    # Placeholder for upcoming pages
    def show_placeholder(self, page):

        ctk.CTkLabel(
            self.content,
            text=page,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(pady=(180, 10))

        ctk.CTkLabel(
            self.content,
            text="This section will be implemented in a later step.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack()
