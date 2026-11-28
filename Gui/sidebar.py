import tkinter

import customtkinter as ctk

from Gui import theme as t


# Keys are the page names the dashboard expects. Values are what the
# sidebar shows, so a label can change without breaking navigation.
PAGES = [
    ("Dashboard", "Dashboard"),
    ("My Subjects", "Subjects"),
    ("Study Planner", "Study planner"),
    ("AI Tutor", "AI tutor"),
    ("PDF Assistant", "PDF assistant"),
    ("Quizzes", "Quizzes"),
    ("Progress", "Progress"),
]

WIDTH = 248
ROW_HEIGHT = 36
SIDE_PAD = 12       # sidebar edge to rows
ROW_GAP = 2         # between rows

# Dark graphite ramp: neutral grey, not navy, so it sits next to the
# light grey pages and the teal accent without a color clash.
SIDEBAR_BG = "#141415"
ROW_HOVER = "#1C1C1E"
ROW_ACTIVE = "#232325"
DARK_HAIRLINE = "#2A2A2C"   # light text at about 8% on the sidebar
DARK_TEXT = "#EDEDED"
DARK_TEXT_2 = "#A1A1A6"
DARK_MUTED = "#85858B"
# The page accent is too dark to read on near-black, so the logo
# mark uses a lighter step of the same teal.
ACCENT_ON_DARK = "#2BA394"
TICK_EMPTY = "#3A3A3D"


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, on_navigate, on_logout):
        super().__init__(parent, width=WIDTH, corner_radius=0,
                         fg_color=SIDEBAR_BG)

        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.active_page = "Dashboard"
        self.nav_buttons = {}

        self.pack_propagate(False)

        self._build_logo()
        self._build_nav()
        self._build_footer()

        self.set_active("Dashboard")

    # Logo: the app's tick mark plus the name

    def _build_logo(self):
        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(fill="x", padx=SIDE_PAD + 12, pady=(32, 32))

        mark = tkinter.Canvas(logo, width=20, height=20, bg=SIDEBAR_BG,
                              highlightthickness=0, bd=0)
        mark.pack(side="left")
        # Three ticks, two done: the same blocks as the progress bars
        for index, color in enumerate((ACCENT_ON_DARK, ACCENT_ON_DARK,
                                       TICK_EMPTY)):
            x0 = index * 7
            mark.create_rectangle(x0, 4, x0 + 5, 16, fill=color, width=0)

        t.label(logo, "AI Study", "heading", DARK_TEXT).pack(
            side="left", padx=(10, 0))

    # Navigation

    def _row(self, parent, text, command, color):
        return ctk.CTkButton(
            parent,
            text=text,
            anchor="w",
            height=ROW_HEIGHT,
            corner_radius=t.CONTROL_RADIUS,
            border_spacing=12,
            border_width=1,
            border_color=SIDEBAR_BG,
            font=t.fonts()["body"],
            fg_color=SIDEBAR_BG,
            hover_color=ROW_HOVER,
            text_color=color,
            command=command
        )

    def _build_nav(self):
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.pack(fill="x", padx=SIDE_PAD)

        for page, text in PAGES:
            button = self._row(nav, text,
                               lambda p=page: self.navigate(p), DARK_TEXT_2)
            button.pack(fill="x", pady=(0, ROW_GAP))
            self.nav_buttons[page] = button

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=SIDE_PAD, pady=(0, 16))

        tkinter.Frame(footer, height=1, bg=DARK_HAIRLINE, bd=0,
                      highlightthickness=0).pack(fill="x", pady=(0, 8))

        self._row(footer, "Log out", self.on_logout, DARK_MUTED).pack(
            fill="x")

    # State

    def navigate(self, page):
        self.set_active(page)
        self.on_navigate(page)

    def set_active(self, page):
        """Active row is one surface step up with a hairline."""
        self.active_page = page

        for name, button in self.nav_buttons.items():
            active = name == page
            button.configure(
                fg_color=ROW_ACTIVE if active else SIDEBAR_BG,
                hover_color=ROW_ACTIVE if active else ROW_HOVER,
                border_color=DARK_HAIRLINE if active else SIDEBAR_BG,
                text_color=DARK_TEXT if active else DARK_TEXT_2
            )