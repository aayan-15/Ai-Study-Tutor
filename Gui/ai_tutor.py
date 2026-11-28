import re
import threading

import customtkinter as ctk

from Core.gemini_service import GeminiService
from Gui import theme as t


WRAP = 640          # reading width for messages
TOP_PAD = 40        # page top
BOTTOM_PAD = 32     # page bottom

GREETING = (
    "Ask me about anything you're studying. I can explain a concept, "
    "walk through an example or check your understanding."
)


def clean_markdown(text):
    """Model replies often use markdown. Labels show it raw, so tidy it."""
    lines = []
    for line in (text or "").strip().splitlines():
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        if stripped.startswith(("* ", "- ")):
            stripped = "• " + stripped[2:]
        stripped = re.sub(r"^#{1,6}\s+", "", stripped)
        lines.append(indent + stripped)
    text = "\n".join(lines)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return re.sub(r"\n{3,}", "\n\n", text)


class AITutorFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, corner_radius=0, fg_color=t.BG)

        self.user = user
        self.gemini = GeminiService()
        self.is_generating = False
        self.thinking_row = None

        # Store conversation history
        self.conversation_history = []

        self.create_header()
        self.create_chat_area()
        self.create_input_area()

        self.add_message("ai", GREETING)

        # The chat fills the window height, so the conversation scrolls
        # inside its card and the input stays in view.
        self.winfo_toplevel().bind("<Configure>", self._fit_chat, add="+")
        self.after_idle(self._fit_chat)

    # Header

    def create_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=t.PAGE_X, pady=(TOP_PAD, t.GAP))

        t.label(self.header, "AI tutor", "title").pack(anchor="w")
        t.label(
            self.header,
            "Ask about anything you're studying. The tutor remembers this "
            "conversation until you leave the page",
            "small", t.TEXT_2
        ).pack(anchor="w", pady=(4, 0))

    # Conversation

    def create_chat_area(self):
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            height=360,
            fg_color=t.CARD,
            corner_radius=t.RADIUS,
            border_width=1,
            border_color=t.HAIRLINE,
            scrollbar_button_color="#E4E4E7",
            scrollbar_button_hover_color="#D4D4D8"
        )
        self.chat_frame.pack(fill="x", padx=t.PAGE_X)

    def _fit_chat(self, event=None):
        if not self.winfo_exists():
            return
        top = self.winfo_toplevel()
        if event is not None and event.widget is not top:
            return
        used = (self.header.winfo_reqheight() + TOP_PAD + t.GAP
                + self.input_frame.winfo_reqheight() + 16 + BOTTOM_PAD)
        height = max(280, top.winfo_height() - used - 35)
        if abs(self.chat_frame.cget("height") - height) > 4:
            self.chat_frame.configure(height=height)

    def add_message(self, sender, message):
        """Your messages sit right in a grey bubble, the tutor's read as
        plain text on the page, like notes."""
        is_user = sender == "user"

        row = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(16, 0))

        if is_user:
            bubble = ctk.CTkFrame(row, fg_color=t.RAISED,
                                  corner_radius=t.RADIUS)
            bubble.pack(side="right", padx=(96, 0))
            t.label(bubble, message, "body", wraplength=WRAP - 96,
                    height=0).pack(padx=16, pady=12)
        else:
            t.label(row, "Tutor", "meta", t.MUTED).pack(anchor="w")
            t.label(row, clean_markdown(message), "body",
                    wraplength=WRAP, height=0).pack(anchor="w",
                                                    pady=(4, 0))

        self._scroll_to_end()
        return row

    def _scroll_to_end(self):
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    # Input

    def create_input_area(self):
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=t.PAGE_X,
                              pady=(8, 20))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = t.entry(
            self.input_frame,
            "Like: explain normalization with an example"
        )
        self.message_entry.configure(height=44)
        self.message_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.message_entry.bind("<Return>", self.handle_enter)

        self.send_button = t.primary_button(
            self.input_frame, "Send", self.send_message, width=88)
        self.send_button.configure(height=44)
        self.send_button.grid(row=0, column=1)

    # Sending

    def handle_enter(self, event):
        self.send_message()
        return "break"

    def send_message(self):
        if self.is_generating:
            return

        message = self.message_entry.get().strip()
        if not message:
            return

        self.message_entry.delete(0, "end")
        self.add_message("user", message)

        self.is_generating = True
        t.set_primary_enabled(self.send_button, False)

        # Placeholder row, replaced by the answer when it arrives
        self.thinking_row = ctk.CTkFrame(self.chat_frame,
                                         fg_color="transparent")
        self.thinking_row.pack(fill="x", padx=16, pady=(16, 0))
        t.label(self.thinking_row, "Tutor", "meta", t.MUTED).pack(anchor="w")
        t.label(self.thinking_row, "Thinking", "body", t.MUTED).pack(
            anchor="w", pady=(4, 0))
        self._scroll_to_end()

        # Copy previous conversation history
        history = self.conversation_history.copy()

        threading.Thread(
            target=self.generate_ai_response,
            args=(message, history),
            daemon=True
        ).start()

    # AI response

    def generate_ai_response(self, message, history):
        try:
            response = self.gemini.generate_response(message, history)
            if not response:
                response = "No answer came back. Try asking again."
        except Exception as error:
            print(f"AI Tutor Error: {error}")
            response = (
                "Couldn't reach the AI service. Check your internet "
                "connection and API key, then try again."
            )

        try:
            self.after(
                0,
                lambda response=response, message=message:
                self.display_ai_response_safe(response, message)
            )
        except Exception as error:
            print(f"AI scheduling error: {error}")

    def display_ai_response_safe(self, response, user_message):
        try:
            if not self.winfo_exists() or not self.chat_frame.winfo_exists():
                return
            self.display_ai_response(response, user_message)
        except Exception as error:
            print(f"AI response display error: {error}")

    def display_ai_response(self, response, user_message):
        if self.thinking_row is not None and self.thinking_row.winfo_exists():
            self.thinking_row.destroy()
        self.thinking_row = None

        # Store conversation in memory
        self.conversation_history.append(
            {"role": "user", "content": user_message})
        self.conversation_history.append(
            {"role": "assistant", "content": response})

        self.add_message("ai", response)

        self.is_generating = False
        t.set_primary_enabled(self.send_button, True)
        self.message_entry.focus_set()