import customtkinter as ctk

from Core.subject_manager import SubjectManager
from Core.topics import TopicManager
from Gui import theme as t


class SubjectsFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, corner_radius=0, fg_color=t.BG)

        self.user = user
        self.user_email = user["email"]

        self.subject_manager = SubjectManager()
        self.topic_manager = TopicManager()

        self.editing_subject_id = None
        self.pending_delete_id = None

        self.build_interface()
        self.load_subject_cards()

    # Navigation

    def open_topics(self, subject):
        from Gui.topics import TopicsFrame

        for widget in self.winfo_children():
            widget.destroy()

        TopicsFrame(
            self, self.user, subject, self.show_subjects
        ).pack(fill="both", expand=True)

    def show_subjects(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.editing_subject_id = None
        self.pending_delete_id = None
        self.build_interface()
        self.load_subject_cards()

    # Layout

    def build_interface(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.PAGE_X, pady=(40, t.GAP))

        t.label(header, "Subjects", "title").pack(anchor="w")
        self.summary_label = t.label(header, "", "small", t.TEXT_2)
        self.summary_label.pack(anchor="w", pady=(4, 0))

        # Add / edit form
        self.form = t.card(self)
        self.form.pack(fill="x", padx=t.PAGE_X)

        self.form_title = t.label(self.form, "New subject", "heading")
        self.form_title.pack(anchor="w", padx=t.CARD_PAD,
                             pady=(t.CARD_PAD, 12))

        fields = ctk.CTkFrame(self.form, fg_color="transparent")
        fields.pack(fill="x", padx=t.CARD_PAD, pady=(0, t.CARD_PAD))
        fields.grid_columnconfigure(0, weight=2, uniform="fields")
        fields.grid_columnconfigure(1, weight=3, uniform="fields")

        self.name_entry = t.entry(fields, "Name, like Database Systems")
        self.name_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.name_entry.bind("<Return>", lambda event: self.save_subject())

        self.description_entry = t.entry(fields, "Description (optional)")
        self.description_entry.grid(row=0, column=1, sticky="ew",
                                    padx=(0, 12))
        self.description_entry.bind("<Return>",
                                    lambda event: self.save_subject())

        self.save_button = t.primary_button(
            fields, "Add subject", self.save_subject, width=128)
        self.save_button.grid(row=0, column=2)

        self.cancel_button = t.secondary_button(
            fields, "Cancel", self.clear_form, width=88)

        # Shown under the fields only when there is something to say
        self.message_label = t.label(self.form, "", "small")

        # Subject list
        list_header = ctk.CTkFrame(self, fg_color="transparent")
        list_header.pack(fill="x", padx=t.PAGE_X, pady=(32, 12))
        t.label(list_header, "Your subjects", "heading").pack(side="left")

        self.subjects_container = t.card(self)
        self.subjects_container.pack(fill="x", padx=t.PAGE_X, pady=(0, 40))

    # Data

    def save_subject(self):
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()

        if self.editing_subject_id:
            success, message = self.subject_manager.update_subject(
                self.editing_subject_id, self.user_email, name, description
            )
        else:
            success, message = self.subject_manager.add_subject(
                self.user_email, name, description
            )

        if success:
            self.clear_form()
            self.load_subject_cards()
        self.show_message(message, success)

    def load_subject_cards(self):
        for widget in self.subjects_container.winfo_children():
            widget.destroy()

        subjects = self.subject_manager.get_subjects(self.user_email)

        if not subjects:
            self.summary_label.configure(text="No subjects yet")
            t.label(self.subjects_container, "No subjects yet", "body").pack(
                anchor="w", padx=t.CARD_PAD, pady=(t.CARD_PAD, 4))
            t.label(
                self.subjects_container,
                "Add one above, then break it into topics to track your "
                "progress",
                "small", t.MUTED
            ).pack(anchor="w", padx=t.CARD_PAD, pady=(0, t.CARD_PAD))
            return

        done_total = topics_total = 0
        for index, subject in enumerate(subjects):
            if index:
                t.divider(self.subjects_container, padx=t.CARD_PAD)
            progress = self.create_subject_card(subject)
            done_total += progress["completed_topics"]
            topics_total += progress["total_topics"]

        count = len(subjects)
        noun = "subject" if count == 1 else "subjects"
        self.summary_label.configure(
            text=f"{count} {noun}  ·  {done_total} of {topics_total} "
                 f"topics completed"
        )

    def create_subject_card(self, subject):
        """One row in the subject list. Returns the subject's progress."""
        progress = self.topic_manager.get_subject_progress(
            subject["id"], self.user_email
        )
        completed = progress["completed_topics"]
        total = progress["total_topics"]
        percent = round(progress["percentage"])

        row = ctk.CTkFrame(self.subjects_container, fg_color="transparent")
        row.pack(fill="x", padx=t.CARD_PAD, pady=16)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, minsize=240)

        # Name and description
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=0, sticky="w", padx=(0, 32))

        t.label(info, subject["name"], "body").pack(anchor="w")
        description = subject.get("description") or ""
        if description:
            t.label(info, description, "small", t.TEXT_2,
                    wraplength=420).pack(anchor="w", pady=(4, 0))

        # Progress, one tick per topic
        progress_box = ctk.CTkFrame(row, fg_color="transparent")
        progress_box.grid(row=0, column=1, sticky="ew")

        t.tick_bar(progress_box, completed, total, height=8).pack(fill="x")
        caption = (f"{completed} of {total} topics  ·  {percent}%" if total
                   else "No topics yet")
        t.label(progress_box, caption, "meta", t.MUTED).pack(
            anchor="w", pady=(8, 0))

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=2, sticky="e", padx=(32, 0))

        t.text_button(actions, "View topics",
                      lambda s=subject: self.open_topics(s),
                      color=t.ACCENT).pack(side="left")
        t.text_button(actions, "Edit",
                      lambda s=subject: self.edit_subject(s)).pack(
            side="left", padx=(4, 0))

        delete_button = t.text_button(actions, "Delete", None)
        delete_button.configure(
            command=lambda s=subject, b=delete_button: self.delete_subject(
                s, b)
        )
        delete_button.pack(side="left", padx=(4, 0))

        return progress

    def edit_subject(self, subject):
        self.editing_subject_id = subject["id"]

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, subject["name"])
        self.description_entry.delete(0, "end")
        self.description_entry.insert(0, subject.get("description") or "")

        self.form_title.configure(text=f"Edit {subject['name']}")
        self.save_button.configure(text="Save changes")
        self.cancel_button.grid(row=0, column=3, padx=(8, 0))
        self.show_message("")
        self.name_entry.focus_set()

    def delete_subject(self, subject, button=None):
        # First click asks, second click within four seconds deletes.
        if button is not None and self.pending_delete_id != subject["id"]:
            self.pending_delete_id = subject["id"]
            button.configure(text="Confirm delete", text_color=t.NEGATIVE,
                             hover_color=t.NEGATIVE_SOFT)
            self.after(4000, lambda: self._reset_delete(subject["id"],
                                                        button))
            return

        self.pending_delete_id = None
        success, message = self.subject_manager.delete_subject(
            subject["id"], self.user_email
        )

        if success:
            if self.editing_subject_id == subject["id"]:
                self.clear_form()
            self.load_subject_cards()
        self.show_message(message, success)

    def _reset_delete(self, subject_id, button):
        if self.pending_delete_id == subject_id:
            self.pending_delete_id = None
        if button.winfo_exists():
            button.configure(text="Delete", text_color=t.TEXT_2,
                             hover_color=t.RAISED)

    def clear_form(self):
        self.editing_subject_id = None

        self.name_entry.delete(0, "end")
        self.description_entry.delete(0, "end")

        self.form_title.configure(text="New subject")
        self.save_button.configure(text="Add subject")
        self.cancel_button.grid_forget()
        self.show_message("")

    def show_message(self, text, success=True):
        """Status line under the form, hidden when empty."""
        text = (text or "").strip().rstrip("!.")
        if not text:
            self.message_label.pack_forget()
            return

        self.message_label.configure(
            text=text, text_color=t.POSITIVE if success else t.NEGATIVE
        )
        self.message_label.pack(anchor="w", padx=t.CARD_PAD,
                                pady=(0, 20))
