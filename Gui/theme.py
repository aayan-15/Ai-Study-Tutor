"""Shared look for AI Study Tutor.

One neutral ramp, three text roles and one accent (fountain pen ink).
Every page imports from here, so the palette, type and spacing stay the
same across the app. Save as Gui/theme.py.
"""
import tkinter
import tkinter.font as tkfont

import customtkinter as ctk


# Colors
BG = "#FAFAFA"           # page
CARD = "#FFFFFF"         # raised surface
RAISED = "#F4F4F5"       # hover, active row
HAIRLINE = "#EBEBEB"     # borders and dividers
FIELD_BORDER = "#E4E4E7" # input borders
TRACK = "#E7E7E9"        # empty part of a progress bar

TEXT = "#171717"         # primary
TEXT_2 = "#525252"       # secondary
MUTED = "#737373"        # meta, captions

ACCENT = "#0F766E"       # ink teal, 5.4:1 with white text
ACCENT_HOVER = "#115E59"
ACCENT_SOFT = "#EEF6F5"      # selected option background
ACCENT_DISABLED = "#A3C9C5"  # primary button while it cannot be used

POSITIVE = "#16A34A"
NEGATIVE = "#DC2626"
NEGATIVE_SOFT = "#FEF2F2"

# Spacing, all on a 4px grid
PAGE_X = 32              # page side padding
GAP = 24                 # between sections and between cards
CARD_PAD = 24            # inside cards
RADIUS = 12              # cards
CONTROL_RADIUS = 8       # buttons and inputs

# Type
UI_FONTS = ["Inter", "Segoe UI Variable Text", "Segoe UI",
            "SF Pro Text", "Helvetica Neue", "DejaVu Sans"]
MONO_FONTS = ["JetBrains Mono", "Cascadia Mono", "Consolas",
              "SF Mono", "Menlo", "DejaVu Sans Mono"]

# CTkLabel pads every label to 28px tall. Fixed heights per style keep
# two-line rows and cards tight.
LINE_HEIGHTS = {"title": 36, "heading": 24, "question": 28,
                "body": 20, "small": 20,
                "figure": 36, "hero": 56, "meta": 16, "small_bold": 20,}

_fonts = None


def _pick_family(candidates):
    available = set(tkfont.families())
    return next((name for name in candidates if name in available),
                "TkDefaultFont")


def fonts():
    """Font set, built once after the Tk root exists."""
    global _fonts
    if _fonts is None:
        ui = _pick_family(UI_FONTS)
        mono = _pick_family(MONO_FONTS)
        _fonts = {
            "title": ctk.CTkFont(family=ui, size=28),
            "heading": ctk.CTkFont(family=ui, size=16, weight="bold"),
            "question": ctk.CTkFont(family=ui, size=18),
            "body": ctk.CTkFont(family=ui, size=14),
            "small": ctk.CTkFont(family=ui, size=13),
            "figure": ctk.CTkFont(family=ui, size=30),
            "hero": ctk.CTkFont(family=ui, size=48),
            "meta": ctk.CTkFont(family=mono, size=12),
            "small_bold": ctk.CTkFont(family=ui, size=13, weight="bold"),
        }
    return _fonts


# Building blocks

def label(parent, text, style, color=TEXT, **kwargs):
    kwargs.setdefault("height", LINE_HEIGHTS[style])
    kwargs.setdefault("anchor", "w")       # pass anchor="e" for numbers
    kwargs.setdefault("justify", "left")
    return ctk.CTkLabel(
        parent, text=text, font=fonts()[style], text_color=color, **kwargs
    )


def card(parent):
    return ctk.CTkFrame(
        parent, fg_color=CARD, corner_radius=RADIUS,
        border_width=1, border_color=HAIRLINE
    )


def divider(parent, **pack):
    # A plain tk frame: CTkFrame does not draw reliably at 1px tall.
    line = tkinter.Frame(parent, height=1, bg=HAIRLINE, bd=0,
                         highlightthickness=0)
    line.pack(fill="x", **pack)
    return line


def entry(parent, placeholder, **kwargs):
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        height=40,
        corner_radius=CONTROL_RADIUS,
        border_width=1,
        border_color=FIELD_BORDER,
        fg_color=CARD,
        text_color=TEXT,
        placeholder_text_color=MUTED,
        font=fonts()["body"],
        **kwargs
    )


def primary_button(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command,
        height=40, corner_radius=CONTROL_RADIUS,
        fg_color=ACCENT, hover_color=ACCENT_HOVER,
        text_color="#FFFFFF", text_color_disabled="#FFFFFF",
        font=fonts()["body"], **kwargs
    )


def secondary_button(parent, text, command, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command,
        height=40, corner_radius=CONTROL_RADIUS,
        fg_color=CARD, hover_color=RAISED,
        border_width=1, border_color=FIELD_BORDER,
        text_color=TEXT, text_color_disabled=MUTED,
        font=fonts()["body"], **kwargs
    )


def set_primary_enabled(button, enabled):
    """CTk keeps the fill when disabled, so fade it by hand."""
    button.configure(state="normal" if enabled else "disabled",
                     fg_color=ACCENT if enabled else ACCENT_DISABLED)


def text_button(parent, text, command, color=TEXT_2, **kwargs):
    """Quiet button that reads as a link, for row actions."""
    kwargs.setdefault("height", 32)
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=0, corner_radius=CONTROL_RADIUS,
        fg_color="transparent", hover_color=RAISED,
        text_color=color, font=fonts()["small"], **kwargs
    )


def tick_bar(parent, completed, total, height=12, colors=None):
    """The app's signature: one tick per topic, filled in ink when done.

    Pass `colors`, one per tick, to color each tick yourself, like
    right and wrong answers in a quiz.
    """
    # A small requested width lets the layout decide how wide it gets,
    # instead of the canvas claiming its default ~380px.
    canvas = ctk.CTkCanvas(parent, width=120, height=height, bg=CARD,
                           highlightthickness=0, bd=0)
    canvas.bind(
        "<Configure>",
        lambda event: _draw_ticks(canvas, event.width, height,
                                  completed, total, colors)
    )
    return canvas


def _draw_ticks(canvas, width, height, completed, total, colors=None):
    canvas.delete("all")

    # Too many topics to show one by one: fall back to a plain bar.
    if colors is None and (total == 0 or width / total < 6):
        share = completed / total if total else 0
        canvas.create_rectangle(0, 0, width, height, fill=TRACK, width=0)
        canvas.create_rectangle(0, 0, width * share, height,
                                fill=ACCENT, width=0)
        return

    gap = 3 if width / total >= 10 else 2
    segment = (width - gap * (total - 1)) / total
    for index in range(total):
        x0 = index * (segment + gap)
        if colors is not None:
            color = colors[index]
        else:
            color = ACCENT if index < completed else TRACK
        canvas.create_rectangle(x0, 0, x0 + segment, height,
                                fill=color, width=0)