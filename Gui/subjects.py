import customtkinter as ctk

from Core.subject_manager import SubjectManager
from Core.topics import TopicManager


class SubjectsFrame(ctk.CTkFrame):

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

        self.editing_subject_id = None

        self.build_interface()
        self.load_subject_cards()

    # Open topics for a subject
    def open_topics(self, subject):

        from Gui.topics import TopicsFrame

        for widget in self.winfo_children():
            widget.destroy()

        topics_frame = TopicsFrame(
            self,
            self.user,
            subject,
            self.show_subjects
        )

        topics_frame.pack(
            fill="both",
            expand=True
        )

    # Return to subjects list
    def show_subjects(self):

        for widget in self.winfo_children():
            widget.destroy()

        self.build_interface()
        self.load_subject_cards()

    # Build the main interface
    def build_interface(self):

        # Page heading
        ctk.CTkLabel(
            self,
            text="My Subjects",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 5)
        )

        ctk.CTkLabel(
            self,
            text="Manage your subjects and organize your learning.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(
            anchor="w",
            padx=35,
            pady=(0, 20)
        )

        # Add / edit subject form
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
            text="Add a Subject",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.name_entry = ctk.CTkEntry(
            self.form,
            placeholder_text="Subject name",
            height=40
        )

        self.name_entry.pack(
            fill="x",
            padx=20,
            pady=6
        )

        self.description_entry = ctk.CTkEntry(
            self.form,
            placeholder_text="Description (optional)",
            height=40
        )

        self.description_entry.pack(
            fill="x",
            padx=20,
            pady=6
        )

        self.message_label = ctk.CTkLabel(
            self.form,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#D9534F"
        )

        self.message_label.pack(
            anchor="w",
            padx=20,
            pady=(4, 0)
        )

        buttons_frame = ctk.CTkFrame(
            self.form,
            fg_color="transparent"
        )

        buttons_frame.pack(
            fill="x",
            padx=20,
            pady=(8, 18)
        )

        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Add Subject",
            width=130,
            height=38,
            command=self.save_subject
        )

        self.save_button.pack(side="left")

        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel Edit",
            width=110,
            height=38,
            fg_color="#E5E9F0",
            hover_color="#D5DAE4",
            text_color="#202938",
            command=self.clear_form
        )

        # Subjects heading
        ctk.CTkLabel(
            self,
            text="Your Subjects",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=35,
            pady=(5, 10)
        )

        # Scrollable subjects list
        self.subjects_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.subjects_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

    # Add or update a subject
    def save_subject(self):

        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if self.editing_subject_id:

            success, message = self.subject_manager.update_subject(
                self.editing_subject_id,
                self.user_email,
                name,
                description
            )

        else:

            success, message = self.subject_manager.add_subject(
                self.user_email,
                name,
                description
            )

        self.message_label.configure(
            text=message,
            text_color="#238636" if success else "#D9534F"
        )

        if success:
            self.clear_form()
            self.load_subject_cards()

    # Load and display subjects
    def load_subject_cards(self):

        for widget in self.subjects_container.winfo_children():
            widget.destroy()

        subjects = self.subject_manager.get_subjects(
            self.user_email
        )

        if not subjects:

            ctk.CTkLabel(
                self.subjects_container,
                text="No subjects added yet. Add your first subject above.",
                font=ctk.CTkFont(size=14),
                text_color="#8993A5"
            ).pack(pady=30)

            return

        for subject in subjects:
            self.create_subject_card(subject)

    # Create an individual subject card
    def create_subject_card(self, subject):

        card = ctk.CTkFrame(
            self.subjects_container,
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

        # Subject information
        details = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        details.pack(
            side="left",
            fill="both",
            expand=True,
            padx=18,
            pady=15
        )

        ctk.CTkLabel(
            details,
            text=subject["name"],
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color="#202938"
        ).pack(anchor="w")

        description = subject.get(
            "description",
            ""
        )

        ctk.CTkLabel(
            details,
            text=(
                description
                if description
                else "No description provided"
            ),
            font=ctk.CTkFont(size=12),
            text_color="#778195"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # Get subject progress
        progress = self.topic_manager.get_subject_progress(
            subject["id"],
            self.user_email
        )

        completed_topics = progress["completed_topics"]
        total_topics = progress["total_topics"]
        percentage = progress["percentage"]

        # Progress text
        ctk.CTkLabel(
            details,
            text=(
                f"Progress: {percentage}%  "
                f"({completed_topics}/{total_topics} topics completed)"
            ),
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color="#3157D5"
        ).pack(
            anchor="w",
            pady=(10, 5)
        )

        # Progress bar
        progress_bar = ctk.CTkProgressBar(
            details,
            width=350,
            height=10
        )

        progress_bar.pack(
            anchor="w",
            fill="x",
            padx=(0, 10)
        )

        progress_bar.set(
            percentage / 100
        )

        # Action buttons
        actions = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        actions.pack(
            side="right",
            padx=15
        )

        ctk.CTkButton(
            actions,
            text="View Topics",
            width=95,
            height=32,
            fg_color="#3157D5",
            hover_color="#2546B5",
            command=lambda s=subject: self.open_topics(s)
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            actions,
            text="Edit",
            width=65,
            height=32,
            command=lambda s=subject: self.edit_subject(s)
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            actions,
            text="Delete",
            width=70,
            height=32,
            fg_color="#D9534F",
            hover_color="#B83B37",
            command=lambda s=subject: self.delete_subject(s)
        ).pack(
            side="left",
            padx=4
        )

    # Load subject details into the form
    def edit_subject(self, subject):

        self.editing_subject_id = subject["id"]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(
            0,
            subject["name"]
        )

        self.description_entry.delete(0, "end")
        self.description_entry.insert(
            0,
            subject.get("description", "")
        )

        self.save_button.configure(
            text="Update Subject"
        )

        self.cancel_button.pack(
            side="left",
            padx=8
        )

        self.message_label.configure(
            text=""
        )

    # Delete a subject
    def delete_subject(self, subject):

        success, message = self.subject_manager.delete_subject(
            subject["id"],
            self.user_email
        )

        self.message_label.configure(
            text=message,
            text_color="#238636" if success else "#D9534F"
        )

        if success:

            if self.editing_subject_id == subject["id"]:
                self.clear_form()

            self.load_subject_cards()

    # Reset the form
    def clear_form(self):

        self.editing_subject_id = None

        self.name_entry.delete(
            0,
            "end"
        )

        self.description_entry.delete(
            0,
            "end"
        )

        self.save_button.configure(
            text="Add Subject"
        )

        self.cancel_button.pack_forget()

        self.message_label.configure(
            text=""
        )