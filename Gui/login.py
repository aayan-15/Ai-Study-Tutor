
import customtkinter as ctk
from PIL import Image
from pathlib import Path


class LoginFrame(ctk.CTkFrame):

    def __init__(self, master, show_register, login_success, auth):
        super().__init__(master)

        self.show_register = show_register
        self.login_success = login_success
        self.auth = auth

        self.password_visible = False

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
            text="Welcome Back",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(100, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Login to continue learning"
        )
        subtitle.pack(pady=(0, 30))

        self.identifier = ctk.CTkEntry(
            self,
            width=320,
            height=40,
            placeholder_text="Email or Username"
        )
        self.identifier.pack(pady=10)

        # Password field container
        password_frame = ctk.CTkFrame(
            self,
            width=320,
            height=40,
            fg_color="transparent"
        )
        password_frame.pack(pady=10)
        password_frame.pack_propagate(False)

        self.password = ctk.CTkEntry(
            password_frame,
            width=320,
            height=40,
            placeholder_text="Password",
            show="*"
        )
        self.password.place(x=0, y=0)

        # Eye icon button
        self.toggle_button = ctk.CTkButton(
            password_frame,
            text="",
            image=self.eye_image,
            width=30,
            height=30,
            fg_color="transparent",
            hover=False,
            command=self.toggle_password
        )
        self.toggle_button.place(
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
        self.error_label.pack(pady=8)

        ctk.CTkButton(
            self,
            text="Login",
            width=320,
            height=40,
            command=self.login
        ).pack(pady=10)

        ctk.CTkButton(
            self,
            text="Create an account",
            width=320,
            height=40,
            fg_color="transparent",
            border_width=1,
            command=self.show_register
        ).pack()

    def toggle_password(self):

        self.password_visible = not self.password_visible

        if self.password_visible:

            self.password.configure(show="")
            self.toggle_button.configure(
                image=self.eyecross_image
            )

        else:

            self.password.configure(show="*")
            self.toggle_button.configure(
                image=self.eye_image
            )

    def login(self):

        identifier = self.identifier.get().strip()
        password = self.password.get()

        self.error_label.configure(text="")

        if not identifier or not password:
            self.error_label.configure(
                text="Please enter your email/username and password."
            )
            return

        success, result = self.auth.login(
            identifier,
            password
        )

        if success:
            self.login_success(result)

        else:
            self.error_label.configure(text=result)
