import customtkinter as ctk

from Gui import theme as t


FORM_WIDTH = 340


class LoginFrame(ctk.CTkFrame):

    def __init__(self, master, show_register, login_success, auth):
        super().__init__(master, fg_color="transparent")

        self.show_register = show_register
        self.login_success = login_success
        self.auth = auth

        self.password_visible = False

        self.create_widgets()

    def create_widgets(self):
        # One column, centered in the half of the card
        form = ctk.CTkFrame(self, fg_color="transparent", width=FORM_WIDTH)
        form.place(relx=0.5, rely=0.5, anchor="center")

        t.label(form, "Log in", "title").pack(anchor="w")
        t.label(form, "Pick up where you left off", "small",
                t.TEXT_2).pack(anchor="w", pady=(4, 32))

        self.identifier = self._field(form, "Email or username")
        self.password, self.toggle_button = self._password_field(
            form, "Password", self.toggle_password, top=16)

        # Fixed height, so a message does not push the buttons down
        self.error_label = t.label(form, "", "small", t.NEGATIVE,
                                   wraplength=FORM_WIDTH)
        self.error_label.pack(anchor="w", fill="x", pady=(12, 12))

        self.login_button = t.primary_button(form, "Log in", self.login,
                                             width=FORM_WIDTH)
        self.login_button.pack(anchor="w")

        switch = ctk.CTkFrame(form, fg_color="transparent")
        switch.pack(anchor="w", pady=(20, 0))
        t.label(switch, "No account yet?", "small", t.TEXT_2).pack(
            side="left")
        t.text_button(switch, "Create one", self.show_register,
                      color=t.ACCENT).pack(side="left", padx=(4, 0))

        for entry in (self.identifier, self.password):
            entry.bind("<Return>", lambda event: self.login())

    # Fields

    def _field(self, parent, text, top=0):
        t.label(parent, text, "small", t.TEXT_2).pack(anchor="w",
                                                      pady=(top, 4))
        entry = t.entry(parent, "", width=FORM_WIDTH)
        entry.pack(anchor="w")
        return entry

    def _password_field(self, parent, text, command, top=0):
        """Password entry with a quiet Show / Hide toggle inside it."""
        t.label(parent, text, "small", t.TEXT_2).pack(anchor="w",
                                                      pady=(top, 4))
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
        self.toggle_button.configure(
            text="Hide" if self.password_visible else "Show")

    # Logging in

    def login(self):
        identifier = self.identifier.get().strip()
        password = self.password.get()

        self.error_label.configure(text="")

        if not identifier or not password:
            self.error_label.configure(
                text="Enter your email or username and your password")
            return

        success, result = self.auth.login(identifier, password)

        if success:
            self.login_success(result)
        else:
            self.error_label.configure(text=result)