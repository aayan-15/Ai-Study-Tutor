
import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, on_navigate, on_logout):
        super().__init__(
            parent,
            width=230,
            corner_radius=0,
            fg_color="#151923"
        )

        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.active_page = "Dashboard"
        self.nav_buttons = {}

        self.pack_propagate(False)

        # Application title
        ctk.CTkLabel(
            self,
            text="AI STUDY",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="YOUR LEARNING SPACE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#8490A5"
        ).pack(pady=(0, 35))

        # Navigation section
        pages = [
            "Dashboard",
            "My Subjects",
            "Study Planner",
            "AI Tutor",
            "PDF Assistant",
            "Quizzes",
            "Progress"
        ]

        for page in pages:
            button = ctk.CTkButton(
                self,
                text=f"   {page}",
                anchor="w",
                height=43,
                corner_radius=8,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="#293246",
                text_color="#C5CCDA",
                command=lambda p=page: self.navigate(p)
            )

            button.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[page] = button

        # Logout button at the bottom
        ctk.CTkButton(
            self,
            text="   Logout",
            anchor="w",
            height=43,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color="#472B35",
            text_color="#F08080",
            command=self.on_logout
        ).pack(side="bottom", fill="x", padx=15, pady=25)

        self.set_active("Dashboard")

    def navigate(self, page):
        self.set_active(page)
        self.on_navigate(page)

    def set_active(self, page):
        self.active_page = page

        for name, button in self.nav_buttons.items():
            if name == page:
                button.configure(
                    fg_color="#3157D5",
                    text_color="#FFFFFF"
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color="#C5CCDA"
                )
