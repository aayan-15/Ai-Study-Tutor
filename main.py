import time
import tkinter

import customtkinter as ctk

from Gui.login import LoginFrame
from Gui.register import RegisterFrame
from Gui.dashboard import DashboardFrame
from Gui import theme as t
from Core.authentication import Authentication


# Application settings
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# The sign-in card: forms on white, and a dark panel that slides over
# whichever form is not in use. The panel uses theme's dark graphite,
# the same as the sidebar, so the first screen looks like the app.
CARD_WIDTH = 1040
CARD_HEIGHT = 620
HALF_WIDTH = CARD_WIDTH // 2
PANEL_PAD = 48

# A sample week in the app, shown on the panel. Plausible, not real.
SAMPLE_SUBJECTS = [
    ("Databases", 7, 10),
    ("Operating systems", 4, 12),
    ("Calculus II", 9, 9),
]

SLIDE_MS = 650          # how long the panel takes to cross
SLIDE_FRAME_MS = 10     # redraw interval, about 100 frames a second


class AIStudyPlatform(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AI Study")
        self.geometry("1200x750")
        self.minsize(1100, 700)
        self.configure(fg_color=t.BG)

        self.auth = Authentication()
        self.current_user = None

        self.auth_container = None
        self.panel = None
        self.panel_button = None

        self.register_mode = False
        self.is_animating = False

        self.build_auth_screen()

    # Authentication screen

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.auth_container = None

    def build_auth_screen(self):
        self.clear_screen()

        self.auth_container = ctk.CTkFrame(
            self,
            width=CARD_WIDTH,
            height=CARD_HEIGHT,
            corner_radius=t.RADIUS + 4,
            fg_color=t.CARD,
            border_width=1,
            border_color=t.HAIRLINE
        )
        self.auth_container.place(relx=0.5, rely=0.5, anchor="center")
        self.auth_container.pack_propagate(False)

        # Login form, left half
        self.login_frame = LoginFrame(
            self.auth_container,
            self.show_register,
            self.login_success,
            self.auth
        )
        self.login_frame.place(**_form_box(0))

        # Registration form, right half
        self.register_frame = RegisterFrame(
            self.auth_container,
            self.show_login,
            self.auth
        )
        self.register_frame.place(**_form_box(HALF_WIDTH))

        # Panel covers the form that is not in use
        self.create_branding_panel()

        self.register_mode = False

    # Panel

    def create_branding_panel(self):
        self.panel = ctk.CTkFrame(
            self.auth_container,
            width=HALF_WIDTH,
            height=CARD_HEIGHT,
            corner_radius=t.RADIUS + 4,
            fg_color=t.DARK_BG
        )
        self.panel.place(x=HALF_WIDTH, y=0)
        self.panel.pack_propagate(False)

        self._build_logo(self.panel)

        # Text and preview sit at the bottom of the panel, the logo at
        # the top, and the space between them stays calm.
        body = ctk.CTkFrame(self.panel, fg_color="transparent")
        body.pack(side="bottom", fill="x", padx=PANEL_PAD,
                  pady=(0, PANEL_PAD))

        t.label(body, "Work through your syllabus one topic at a time",
                "title", t.DARK_TEXT, height=0,
                wraplength=HALF_WIDTH - PANEL_PAD * 2).pack(anchor="w")
        t.label(
            body,
            "Add your subjects and topics, ask the AI tutor when you get "
            "stuck and quiz yourself before you tick a topic off",
            "body", t.DARK_TEXT_2, height=0,
            wraplength=HALF_WIDTH - PANEL_PAD * 2 - 24
        ).pack(anchor="w", pady=(12, 0))

        self._build_preview(body)

        self.panel_button = ctk.CTkButton(
            body,
            text="Create an account",
            width=200,
            height=44,
            corner_radius=t.CONTROL_RADIUS,
            fg_color=t.DARK_BG,
            hover_color=t.DARK_HOVER,
            border_width=1,
            border_color=t.DARK_BORDER,
            text_color=t.DARK_TEXT,
            font=t.fonts()["body"],
            command=self.panel_action
        )
        self.panel_button.pack(anchor="w", pady=(32, 0))

    def _build_logo(self, parent):
        logo = ctk.CTkFrame(parent, fg_color="transparent")
        logo.pack(anchor="w", padx=PANEL_PAD, pady=(PANEL_PAD, 0))

        # Same three-tick mark as the sidebar
        mark = tkinter.Canvas(logo, width=20, height=20, bg=t.DARK_BG,
                              highlightthickness=0, bd=0)
        mark.pack(side="left")
        for index, color in enumerate((t.ACCENT_ON_DARK, t.ACCENT_ON_DARK,
                                       t.TICK_EMPTY_DARK)):
            x0 = index * 7
            mark.create_rectangle(x0, 4, x0 + 5, 16, fill=color, width=0)

        t.label(logo, "AI Study", "heading", t.DARK_TEXT).pack(
            side="left", padx=(10, 0))

    def _build_preview(self, parent):
        """The moment: a slice of the syllabus card, one tick per topic."""
        card = ctk.CTkFrame(parent, fg_color=t.DARK_HOVER,
                            corner_radius=t.RADIUS, border_width=1,
                            border_color=t.DARK_HAIRLINE)
        card.pack(fill="x", pady=(32, 0))

        for index, (name, done, total) in enumerate(SAMPLE_SUBJECTS):
            row = ctk.CTkFrame(card, fg_color="transparent")
            last = index == len(SAMPLE_SUBJECTS) - 1
            row.pack(fill="x", padx=20, pady=(20 if index == 0 else 12,
                                              20 if last else 0))
            row.grid_columnconfigure(0, weight=1)

            t.label(row, name, "small", t.DARK_TEXT).grid(
                row=0, column=0, sticky="w")
            t.label(row, f"{done} of {total}", "meta", t.DARK_MUTED,
                    anchor="e").grid(row=0, column=1, sticky="e")

            t.tick_bar(row, done, total, height=8, dark=True).grid(
                row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    # Panel actions

    def panel_action(self):
        if self.register_mode:
            self.show_login()
        else:
            self.show_register()

    def show_register(self):
        if self.register_mode or self.is_animating:
            return
        self.animate_panel(target_register=True)

    def show_login(self):
        # Still on the sign-in screen: slide back to the login form
        if (self.auth_container is not None
                and self.auth_container.winfo_exists()):
            if self.register_mode and not self.is_animating:
                self.animate_panel(target_register=False)
            return

        # Coming back from the dashboard after logging out
        self.build_auth_screen()

    # Slide

    def animate_panel(self, target_register):
        if self.is_animating:
            return
        self.is_animating = True

        start_x = 0 if self.register_mode else HALF_WIDTH
        end_x = 0 if target_register else HALF_WIDTH
        started = time.perf_counter()

        def animate():
            if self.panel is None or not self.panel.winfo_exists():
                self.is_animating = False
                return

            # Timed by the clock, not by frame count, so the slide takes
            # the same time on a slow laptop and a fast desktop.
            elapsed = (time.perf_counter() - started) * 1000
            progress = min(elapsed / SLIDE_MS, 1)
            # Ease in and out: eases off the edge, glides, settles
            eased = (4 * progress ** 3 if progress < 0.5
                     else 1 - (-2 * progress + 2) ** 3 / 2)
            self.panel.place_configure(
                x=round(start_x + (end_x - start_x) * eased))

            if progress < 1:
                self.after(SLIDE_FRAME_MS, animate)
                return

            self.register_mode = target_register
            self.is_animating = False
            self.panel_button.configure(
                text="Log in instead" if self.register_mode
                else "Create an account")

        animate()

    # Dashboard

    def login_success(self, user):
        self.current_user = user
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_screen()
        dashboard = DashboardFrame(self, self.current_user, self.show_login)
        dashboard.pack(fill="both", expand=True)


def _form_box(x):
    """Inset the forms by the card radius, so a form's own square
    background never covers the card's rounded corners."""
    inset = t.RADIUS + 4
    # CTk widgets refuse width/height in place(), so use relative sizes
    return {"x": x + inset, "y": inset,
            "relwidth": (HALF_WIDTH - inset * 2) / CARD_WIDTH,
            "relheight": (CARD_HEIGHT - inset * 2) / CARD_HEIGHT}


if __name__ == "__main__":
    app = AIStudyPlatform()
    app.mainloop()