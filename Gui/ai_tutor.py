import customtkinter as ctk
import threading
from Core.gemini_service import GeminiService

class AITutorFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color="#F4F6FA"
        )

        self.user = user
        self.gemini = GeminiService()
        self.is_generating = False

        # Store conversation history
        self.conversation_history = []

        self.create_header()
        self.create_chat_area()
        self.create_input_area()

        self.add_message(
            "ai",
            "Hello! I'm your AI Study Tutor. Ask me anything about your studies."
        )

    # ---------------- HEADER ----------------

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12
        )

        header.pack(
            fill="x",
            padx=25,
            pady=(25, 15)
        )

        ctk.CTkLabel(
            header,
            text="AI Study Tutor",
            font=("Arial", 24, "bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            header,
            text="Your personal AI assistant for learning and understanding concepts.",
            font=("Arial", 13),
            text_color="#7B8494"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

    # ---------------- CHAT AREA ----------------

    def create_chat_area(self):

        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            corner_radius=12
        )

        self.chat_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 15)
        )

    def add_message(self, sender, message):

        is_user = sender == "user"

        message_row = ctk.CTkFrame(
            self.chat_frame,
            fg_color="transparent"
        )

        message_row.pack(
            fill="x",
            padx=15,
            pady=8
        )

        message_bubble = ctk.CTkFrame(
            message_row,
            fg_color="#2563EB" if is_user else "#F0F2F5",
            corner_radius=12
        )

        message_bubble.pack(
            side="right" if is_user else "left",
            padx=(80, 0) if is_user else (0, 80)
        )

        ctk.CTkLabel(
            message_bubble,
            text=message,
            font=("Arial", 14),
            text_color="white" if is_user else "#202938",
            wraplength=550,
            justify="left"
        ).pack(
            padx=15,
            pady=12
        )

        self.chat_frame._parent_canvas.yview_moveto(1.0)

    # ---------------- INPUT AREA ----------------

    def create_input_area(self):

        input_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12
        )

        input_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask your study question...",
            height=45,
            font=("Arial", 14),
            border_color="#D9DEE8"
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(15, 10),
            pady=15
        )

        self.message_entry.bind(
            "<Return>",
            self.handle_enter
        )

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            width=90,
            height=45,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.send_message
        )

        self.send_button.pack(
            side="right",
            padx=(0, 15),
            pady=15
        )

    # ---------------- SEND MESSAGE ----------------

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

        self.send_button.configure(
            state="disabled",
            text="..."
        )

        self.add_message("ai", "Thinking...")

        # Copy previous conversation history
        history = self.conversation_history.copy()

        # Run AI generation in background
        thread = threading.Thread(
            target=self.generate_ai_response,
            args=(message, history),
            daemon=True
        )

        thread.start()

    # ---------------- AI RESPONSE ----------------

    def generate_ai_response(self, message, history):

        try:

            response = self.gemini.generate_response(
                message,
                history
            )

            if not response:
                response = "Sorry, no response was generated."

        except Exception as e:

            print(f"Local AI Error: {e}")

            response = (
                "Sorry, I couldn't connect to the AI service. "
                "Please make sure Grok is running and try again."
            )

        # Safely schedule UI update
        try:

            self.after(
                100,
                lambda response=response, message=message:
                self.display_ai_response_safe(response, message)
            )

        except Exception as e:

            print(f"AI scheduling error: {e}")

    # ---------------- DISPLAY AI RESPONSE ----------------

    def display_ai_response_safe(self, response, user_message):

        try:

            if not self.winfo_exists():
                return

            if not self.chat_frame.winfo_exists():
                return

            self.display_ai_response(
                response,
                user_message
            )

        except Exception as e:

            print(f"AI response display error: {e}")

    def display_ai_response(self, response, user_message):

        # Remove temporary Thinking message
        children = self.chat_frame.winfo_children()

        if children:
            children[-1].destroy()

        # Store conversation in memory
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Display AI response
        self.add_message("ai", response)

        self.is_generating = False

        self.send_button.configure(
            state="normal",
            text="Send"
        )
