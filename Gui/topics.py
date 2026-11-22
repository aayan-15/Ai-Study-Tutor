import customtkinter as ctk

from Core.topics import TopicManager


class TopicsFrame(ctk.CTkFrame):

    def __init__(self, parent, user, subject, on_back):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color="#F4F6FA"
        )

        self.user = user
        self.subject = subject
        self.on_back = on_back

        self.topic_manager = TopicManager()
        self.editing_topic_id = None

        self.build_interface()
        self.load_topic_cards()

    # Build interface
    def build_interface(self):

        # Header
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 10)
        )

        ctk.CTkButton(
            header,
            text="← Back to Subjects",
            width=140,
            height=34,
            fg_color="#E5E9F0",
            hover_color="#D5DAE4",
            text_color="#202938",
            command=self.on_back
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=self.subject["name"],
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            ),
            text_color="#202938"
        ).pack(anchor="w", pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="Manage topics for this subject.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(anchor="w")

        # Add / Edit topic form
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
            pady=(15, 20)
        )

        ctk.CTkLabel(
            self.form,
            text="Add a Topic",
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
            placeholder_text="Topic name",
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
            text="Add Topic",
            width=130,
            height=38,
            command=self.save_topic
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

        # Topics heading
        ctk.CTkLabel(
            self,
            text="Your Topics",
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

        # Scrollable topic list
        self.topics_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.topics_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

    # Add or update topic
    def save_topic(self):

        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if self.editing_topic_id:

            success, message = self.topic_manager.update_topic(
                self.editing_topic_id,
                self.subject["id"],
                self.user["email"],
                name,
                description
            )

        else:

            success, message = self.topic_manager.add_topic(
                self.subject["id"],
                self.user["email"],
                name,
                description
            )

        self.message_label.configure(
            text=message,
            text_color="#238636" if success else "#D9534F"
        )

        if success:
            self.clear_form()
            self.load_topic_cards()

    # Load topics
    def load_topic_cards(self):

        for widget in self.topics_container.winfo_children():
            widget.destroy()

        topics = self.topic_manager.get_topics(
            self.subject["id"],
            self.user["email"]
        )

        if not topics:

            ctk.CTkLabel(
                self.topics_container,
                text="No topics added yet. Add your first topic above.",
                font=ctk.CTkFont(size=14),
                text_color="#8993A5"
            ).pack(pady=30)

            return

        for topic in topics:
            self.create_topic_card(topic)

    # Create topic card
    def create_topic_card(self, topic):

        card = ctk.CTkFrame(
            self.topics_container,
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

        # Topic information
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

        # Status
        completed = topic.get("completed", False)

        if completed:
            status_text = "Completed"
            status_color = "#238636"
        else:
            status_text = "Pending"
            status_color = "#D97706"

        ctk.CTkLabel(
            details,
            text=topic["name"],
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color="#202938"
        ).pack(anchor="w")

        description = topic.get(
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

        ctk.CTkLabel(
            details,
            text=status_text,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=status_color
        ).pack(
            anchor="w",
            pady=(6, 0)
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

        # Completion button
        if completed:
            completion_text = "Mark Pending"
            completion_color = "#D97706"
            completion_hover = "#B45309"
        else:
            completion_text = "Mark Completed"
            completion_color = "#238636"
            completion_hover = "#1A6B2B"

        ctk.CTkButton(
            actions,
            text=completion_text,
            width=115,
            height=32,
            fg_color=completion_color,
            hover_color=completion_hover,
            command=lambda t=topic: self.toggle_topic_completion(t)
        ).pack(
            side="left",
            padx=4
        )

        # Edit button
        ctk.CTkButton(
            actions,
            text="Edit",
            width=65,
            height=32,
            command=lambda t=topic: self.edit_topic(t)
        ).pack(
            side="left",
            padx=4
        )

        # Delete button
        ctk.CTkButton(
            actions,
            text="Delete",
            width=70,
            height=32,
            fg_color="#D9534F",
            hover_color="#B83B37",
            command=lambda t=topic: self.delete_topic(t)
        ).pack(
            side="left",
            padx=4
        )

    # Toggle completion status
    def toggle_topic_completion(self, topic):

        success, result = self.topic_manager.toggle_completion(
            topic["id"],
            self.subject["id"],
            self.user["email"]
        )

        if success:

            if result:
                message = "Topic marked as completed."
            else:
                message = "Topic marked as pending."

            self.load_topic_cards()

            self.message_label.configure(
                text=message,
                text_color="#238636"
            )

    # Edit topic
    def edit_topic(self, topic):

        self.editing_topic_id = topic["id"]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(
            0,
            topic["name"]
        )

        self.description_entry.delete(
            0,
            "end"
        )

        self.description_entry.insert(
            0,
            topic.get("description", "")
        )

        self.save_button.configure(
            text="Update Topic"
        )

        self.cancel_button.pack(
            side="left",
            padx=8
        )

        self.message_label.configure(
            text=""
        )

    # Delete topic
    def delete_topic(self, topic):

        success, message = self.topic_manager.delete_topic(
            topic["id"],
            self.subject["id"],
            self.user["email"]
        )

        self.message_label.configure(
            text=message,
            text_color="#238636" if success else "#D9534F"
        )

        if success:

            if self.editing_topic_id == topic["id"]:
                self.clear_form()

            self.load_topic_cards()

    # Clear form
    def clear_form(self):

        self.editing_topic_id = None

        self.name_entry.delete(
            0,
            "end"
        )

        self.description_entry.delete(
            0,
            "end"
        )

        self.save_button.configure(
            text="Add Topic"
        )

        self.cancel_button.pack_forget()

        self.message_label.configure(
            text=""
        )