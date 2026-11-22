
import customtkinter as ctk

from Gui.login import LoginFrame
from Gui.register import RegisterFrame
from Gui.dashboard import DashboardFrame
from Core.authentication import Authentication


# Application settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AIStudyPlatform(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AI Study Platform")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.auth = Authentication()
        self.current_user = None

        self.show_login()

    # Remove the current screen
    def clear_screen(self):

        for widget in self.winfo_children():
            widget.destroy()

    # Display login screen
    def show_login(self):

        self.clear_screen()

        login_frame = LoginFrame(
            self,
            self.show_register,
            self.login_success,
            self.auth
        )

        login_frame.pack(
            fill="both",
            expand=True
        )

    # Display registration screen
    def show_register(self):

        self.clear_screen()

        register_frame = RegisterFrame(
            self,
            self.show_login,
            self.auth
        )

        register_frame.pack(
            fill="both",
            expand=True
        )

    # Handle successful login
    def login_success(self, user):

        self.current_user = user
        self.show_dashboard()

    # Display dashboard
    def show_dashboard(self):

        self.clear_screen()

        dashboard = DashboardFrame(
            self,
            self.current_user,
            self.show_login
        )

        dashboard.pack(
            fill="both",
            expand=True
        )


# Run application
if __name__ == "__main__":

    app = AIStudyPlatform()
    app.mainloop()
