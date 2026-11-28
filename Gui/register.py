import customtkinter as ctk

from Gui import theme as t


FORM_WIDTH = 340


class RegisterFrame(ctk.CTkFrame):

    def __init__(self, master, show_login, auth):
        super().__init__(master, fg_color="transparent")

        self.show_login = show_login
        self.auth = auth

        self.password_visible = False
        self.confirm_password_visible = False

        self.create_widgets()

    def create_widgets(self):
        form = ctk.CTkFrame(self, fg_color="transparent", width=FORM_WIDTH)
        form.place(relx=0.5, rely=0.5, anchor="center")

        t.label(form, "Create an account", "title").pack(anchor="w")
        t.label(form, "Your subjects, quizzes and progress stay on it",
                "small", t.TEXT_2).pack(anchor="w", pady=(4, 28))

        self.email = self._field(form, "Email")
        self.username = self._field(form, "Username", top=12)
        self.password, self.password_toggle = self._password_field(
            form, "Password", self.toggle_password, top=12,
            hint="At least 8 characters")
        self.confirm_password, self.confirm_toggle = self._password_field(
            form, "Confirm password", self.toggle_confirm_password, top=12)

        self.error_label = t.label(form, "", "small", t.NEGATIVE,
                                   wraplength=FORM_WIDTH)
        self.error_label.pack(anchor="w", fill="x", pady=(8, 8))

        self.register_button = t.primary_button(
            form, "Create account", self.register, width=FORM_WIDTH)
        self.register_button.pack(anchor="w")

        switch = ctk.CTkFrame(form, fg_color="transparent")
        switch.pack(anchor="w", pady=(16, 0))
        t.label(switch, "Already have an account?", "small",
                t.TEXT_2).pack(side="left")
        t.text_button(switch, "Log in", self.show_login,
                      color=t.ACCENT).pack(side="left", padx=(4, 0))

        for entry in (self.email, self.username, self.password,
                      self.confirm_password):
            entry.bind("<Return>", lambda event: self.register())

    # Fields

    def _field_label(self, parent, text, top, hint=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(top, 4))
        t.label(row, text, "small", t.TEXT_2).pack(side="left")
        if hint:
            t.label(row, hint, "small", t.MUTED, anchor="e").pack(
                side="right")

    def _field(self, parent, text, top=0):
        self._field_label(parent, text, top)
        entry = t.entry(parent, "", width=FORM_WIDTH)
        entry.pack(anchor="w")
        return entry

    def _password_field(self, parent, text, command, top=0, hint=None):
        """Password entry with a quiet Show / Hide toggle inside it."""
        self._field_label(parent, text, top, hint)
        box = ctk.CTkFrame(parent, fg_color="transparent",
                           width=FORM_WIDTH, height=40)
        box.pack(anchor="w")
        box.pack_propagate(False)

        entry = t.entry(box, "", width=FORM_WIDTH, show="•")
        entry.place(x=0, y=0)

        toggle = t.text_button(box, "Show", command, height=28,
                               fg_color=t.CARD, bg_color=t.CARD)
        toggle.place(relx=1.0, rely=0.5, x=-6, anchor="e")
        return entry, toggle

    def toggle_password(self):
        self.password_visible = not self.password_visible
        self.password.configure(show="" if self.password_visible else "•")
        self.password_toggle.configure(
            text="Hide" if self.password_visible else "Show")

    def toggle_confirm_password(self):
        self.confirm_password_visible = not self.confirm_password_visible
        self.confirm_password.configure(
            show="" if self.confirm_password_visible else "•")
        self.confirm_toggle.configure(
            text="Hide" if self.confirm_password_visible else "Show")

    # Registering

    def register(self):
        email = self.email.get().strip()
        username = self.username.get().strip()
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        self.error_label.configure(text="")

        if not email or not username or not password or not confirm_password:
            self.show_error("Fill in every field")
            return

        if len(username) < 3:
            self.show_error("Username needs at least 3 characters")
            return

        if len(password) < 8:
            self.show_error("Password needs at least 8 characters")
            return

        if password != confirm_password:
            self.show_error("The two passwords don't match")
            return

        success, message = self.auth.register(email, username, password)

        if success:
            self.show_error("Account created. Log in to continue",
                            success=True)
            t.set_primary_enabled(self.register_button, False)
            self.after(1200, self._finish_registration)
        else:
            self.show_error(message)

    def _finish_registration(self):
        if not self.winfo_exists():
            return
        # Leave the form empty for whoever registers next
        for entry in (self.email, self.username, self.password,
                      self.confirm_password):
            entry.delete(0, "end")
        self.error_label.configure(text="")
        t.set_primary_enabled(self.register_button, True)
        self.show_login()

    def show_error(self, message, success=False):
        self.error_label.configure(
            text=message,
            text_color=t.POSITIVE if success else t.NEGATIVE
        )