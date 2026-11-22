
import customtkinter as ctk
from PIL import Image
from pathlib import Path


class RegisterFrame(ctk.CTkFrame):

    def __init__(self, master, show_login, auth):
        super().__init__(master)

        self.show_login = show_login
        self.auth = auth

        self.password_visible = False
        self.confirm_password_visible = False

        # Image paths
        image_folder = Path(__file__).resolve().parent.parent / "Images"

        self.eye_image = ctk.CTkImage(
            light_image=Image.open(image_folder / "eye.png"),
            dark_image=Image.open(image_folder / "eye.png"),
            size=(20, 20)
        )

        self.eyecross_image = ctk.CTkImage(
            light_image=Image.open(image_folder / "eyecross.png"),
            dark_image=Image.open(image_folder / "eyecross.png"),
            size=(20, 20)
        )

        self.create_widgets()

    def create_widgets(self):

        title = ctk.CTkLabel(
            self,
            text="Create Account",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(55, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Start your learning journey"
        )
        subtitle.pack(pady=(0, 25))

        self.email = ctk.CTkEntry(
            self,
            width=320,
            height=40,
            placeholder_text="Email Address"
        )
        self.email.pack(pady=8)

        self.username = ctk.CTkEntry(
            self,
            width=320,
            height=40,
            placeholder_text="Username"
        )
        self.username.pack(pady=8)

        # Password field
        password_frame = ctk.CTkFrame(
            self,
            width=320,
            height=40,
            fg_color="transparent"
        )
        password_frame.pack(pady=8)
        password_frame.pack_propagate(False)

        self.password = ctk.CTkEntry(
            password_frame,
            width=320,
            height=40,
            placeholder_text="Password",
            show="*"
        )
        self.password.place(x=0, y=0)

        self.password_toggle = ctk.CTkButton(
            password_frame,
            text="",
            image=self.eye_image,
            width=30,
            height=30,
            fg_color="transparent",
            hover=False,
            command=self.toggle_password
        )
        self.password_toggle.place(
            relx=1.0,
            rely=0.5,
            x=-5,
            anchor="e"
        )

        # Confirm password field
        confirm_frame = ctk.CTkFrame(
            self,
            width=320,
            height=40,
            fg_color="transparent"
        )
        confirm_frame.pack(pady=8)
        confirm_frame.pack_propagate(False)

        self.confirm_password = ctk.CTkEntry(
            confirm_frame,
            width=320,
            height=40,
            placeholder_text="Confirm Password",
            show="*"
        )
        self.confirm_password.place(x=0, y=0)

        self.confirm_toggle = ctk.CTkButton(
            confirm_frame,
            text="",
            image=self.eye_image,
            width=30,
            height=30,
            fg_color="transparent",
            hover=False,
            command=self.toggle_confirm_password
        )
        self.confirm_toggle.place(
            relx=1.0,
            rely=0.5,
            x=-5,
            anchor="e"
        )

        # Inline error message
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#ff5555",
            font=ctk.CTkFont(size=13)
        )
        self.error_label.pack(pady=5)

        ctk.CTkButton(
            self,
            text="Register",
            width=320,
            height=40,
            command=self.register
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="Already have an account? Login",
            width=320,
            height=40,
            fg_color="transparent",
            border_width=1,
            command=self.show_login
        ).pack()

    def toggle_password(self):

        self.password_visible = not self.password_visible

        if self.password_visible:

            self.password.configure(show="")
            self.password_toggle.configure(
                image=self.eyecross_image
            )

        else:

            self.password.configure(show="*")
            self.password_toggle.configure(
                image=self.eye_image
            )

    def toggle_confirm_password(self):

        self.confirm_password_visible = not self.confirm_password_visible

        if self.confirm_password_visible:

            self.confirm_password.configure(show="")
            self.confirm_toggle.configure(
                image=self.eyecross_image
            )

        else:

            self.confirm_password.configure(show="*")
            self.confirm_toggle.configure(
                image=self.eye_image
            )

    def register(self):

        email = self.email.get().strip()
        username = self.username.get().strip()
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        self.error_label.configure(text="")

        if not email or not username or not password or not confirm_password:
            self.show_error("Please fill in all required fields.")
            return

        if len(username) < 3:
            self.show_error("Username must contain at least 3 characters.")
            return

        if len(password) < 8:
            self.show_error("Password must contain at least 8 characters.")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match.")
            return

        success, message = self.auth.register(
            email,
            username,
            password
        )

        if success:
            self.show_error("Account created successfully!", success=True)
            self.after(1200, self.show_login)

        else:
            self.show_error(message)

    def show_error(self, message, success=False):

        self.error_label.configure(
            text=message,
            text_color="#22c55e" if success else "#ff5555"
        )
