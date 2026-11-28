import os
import threading
from tkinter import filedialog

import customtkinter as ctk

from Core.pdf_processor import PDFProcessor
from Core.gemini_service import GeminiService
from Gui import theme as t


# (button label, result heading, prompt sent with the PDF)
ACTIONS = [
    ("Summary", "Summary",
     "Summarize this PDF into clear, easy-to-understand study notes."),
    ("Key points", "Key points",
     "Extract the most important points from this PDF."),
    ("10 MCQs", "Practice questions",
     "Generate 10 multiple-choice questions with four options each and "
     "provide the correct answers."),
    ("Explain concepts", "Concepts explained",
     "Explain the main concepts covered in this PDF in simple language."),
]


class PDFAssistantFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, corner_radius=0, fg_color=t.BG)

        self.user = user
        self.pdf_processor = PDFProcessor()
        self.ai = GeminiService()

        self.pdf_text = ""
        self.pdf_path = ""
        self.is_generating = False

        # Conversation memory for PDF questions
        self.pdf_conversation_history = []

        self.create_header()
        self.create_upload_section()
        self.create_analysis_section()
        self.create_result_section()
        self.update_controls()

    # Header

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.PAGE_X, pady=(40, t.GAP))

        t.label(header, "PDF assistant", "title").pack(anchor="w")
        t.label(
            header,
            "Summaries, key points, practice questions and answers from "
            "your own study material",
            "small", t.TEXT_2
        ).pack(anchor="w", pady=(4, 0))

    # Source PDF

    def create_upload_section(self):
        self.upload_card = t.card(self)
        self.upload_card.pack(fill="x", padx=t.PAGE_X)

        row = ctk.CTkFrame(self.upload_card, fg_color="transparent")
        row.pack(fill="x", padx=t.CARD_PAD, pady=20)
        row.grid_columnconfigure(0, weight=1)

        self.file_label = t.label(row, "No PDF yet", "body")
        self.file_label.grid(row=0, column=0, sticky="w")

        self.file_meta = t.label(
            row, "Choose lecture notes or a chapter to get started",
            "small", t.MUTED
        )
        self.file_meta.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.upload_button = t.primary_button(
            row, "Choose PDF", self.upload_pdf, width=128)
        self.upload_button.grid(row=0, column=1, rowspan=2, sticky="e",
                                padx=(16, 0))

    # Actions and questions

    def create_analysis_section(self):
        self.analysis_card = t.card(self)
        self.analysis_card.pack(fill="x", padx=t.PAGE_X, pady=(t.GAP, 0))

        t.label(self.analysis_card, "Study this PDF", "heading").pack(
            anchor="w", padx=t.CARD_PAD, pady=(t.CARD_PAD, 12))

        grid = ctk.CTkFrame(self.analysis_card, fg_color="transparent")
        grid.pack(fill="x", padx=t.CARD_PAD)

        self.analysis_buttons = []
        for column, (text, title, task) in enumerate(ACTIONS):
            grid.grid_columnconfigure(column * 2, weight=1, uniform="actions")
            if column:
                grid.grid_columnconfigure(column * 2 - 1, minsize=12)

            button = t.secondary_button(
                grid, text,
                lambda task=task, title=title: self.start_analysis(task,
                                                                   title)
            )
            button.grid(row=0, column=column * 2, sticky="ew")
            self.analysis_buttons.append(button)

        t.divider(self.analysis_card, padx=t.CARD_PAD, pady=t.GAP)

        t.label(self.analysis_card, "Ask about this PDF", "small",
                t.TEXT_2).pack(anchor="w", padx=t.CARD_PAD, pady=(0, 8))

        ask_row = ctk.CTkFrame(self.analysis_card, fg_color="transparent")
        ask_row.pack(fill="x", padx=t.CARD_PAD, pady=(0, t.CARD_PAD))
        ask_row.grid_columnconfigure(0, weight=1)

        self.question_entry = t.entry(
            ask_row, "Like: what is the difference between a process and "
                     "a thread")
        self.question_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.question_entry.bind("<Return>", lambda event: self.ask_question())

        self.ask_button = t.primary_button(
            ask_row, "Ask", self.ask_question, width=88)
        self.ask_button.grid(row=0, column=1)

    # Result

    def create_result_section(self):
        self.result_card = t.card(self)
        self.result_card.pack(fill="x", padx=t.PAGE_X, pady=(t.GAP, 40))

        header = ctk.CTkFrame(self.result_card, fg_color="transparent")
        header.pack(fill="x", padx=t.CARD_PAD, pady=(t.CARD_PAD, 8))

        self.result_title = t.label(header, "Results", "heading")
        self.result_title.pack(side="left")

        self.result_status = t.label(header, "", "meta", t.MUTED)
        self.result_status.pack(side="right")

        # The box grows with its text, so the page scrolls instead of
        # a second scrollbar inside the card.
        self.result_box = ctk.CTkTextbox(
            self.result_card,
            height=120,
            corner_radius=0,
            border_width=0,
            fg_color=t.CARD,
            text_color=t.TEXT,
            font=t.fonts()["body"],
            wrap="word",
            activate_scrollbars=False
        )
        self.result_box.pack(fill="x", padx=t.CARD_PAD - 4,
                             pady=(0, t.CARD_PAD - 4))
        self.result_box._textbox.configure(spacing1=2, spacing3=4)
        self.result_box.bind("<Configure>",
                             lambda event: self.fit_result_height())

        self.show_result(
            "Choose a PDF, then pick an action or ask a question. "
            "The answer shows up here.",
            muted=True
        )

    # Upload

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select study PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return

        self.file_label.configure(text=os.path.basename(file_path))
        self.file_meta.configure(text="Reading the text")
        self.upload_button.configure(state="disabled")

        threading.Thread(
            target=self.extract_pdf, args=(file_path,), daemon=True
        ).start()

    def extract_pdf(self, file_path):
        text = self.pdf_processor.extract_text(file_path)
        self.after(0, lambda: self.finish_extraction(file_path, text))

    def finish_extraction(self, file_path, text):
        if not self.winfo_exists():
            return

        self.upload_button.configure(state="normal")

        # Clear conversation whenever the PDF changes
        self.pdf_conversation_history = []

        if not text:
            self.pdf_text = ""
            self.pdf_path = ""
            self.file_label.configure(text="No PDF yet")
            self.file_meta.configure(
                text=f"Couldn't read any text from "
                     f"{os.path.basename(file_path)}. Scanned PDFs need "
                     f"to be converted with OCR first",
                text_color=t.NEGATIVE
            )
            self.update_controls()
            return

        self.pdf_text = text
        self.pdf_path = file_path

        words = len(text.split())
        self.file_label.configure(text=os.path.basename(file_path))
        self.file_meta.configure(text=f"{words:,} words", text_color=t.MUTED)

        self.show_result(
            "Ready. Pick an action or ask a question about this PDF.",
            title="Results", muted=True
        )
        self.update_controls()

    # Analysis

    def start_analysis(self, task, title="Results"):
        if not self.pdf_text:
            self.show_result("Choose a PDF first", muted=True)
            return
        if self.is_generating:
            return

        self.set_busy(True, title)
        threading.Thread(
            target=self.generate_analysis, args=(task, title), daemon=True
        ).start()

    def generate_analysis(self, task, title="Results"):
        try:
            result = self.ai.analyze_pdf(self.pdf_text, task, max_tokens=1500)
        except Exception as error:
            print(f"PDF Analysis Error: {error}")
            result = "Couldn't generate this. Try again in a moment."

        self.after(0, lambda: self.finish_analysis(result, title))

    def finish_analysis(self, result, title="Results"):
        if not self.winfo_exists():
            return

        self.set_busy(False)
        self.show_result(result, title=title)

    # Questions

    def ask_question(self):
        question = self.question_entry.get().strip()

        if not self.pdf_text:
            self.show_result("Choose a PDF first", muted=True)
            return
        if not question:
            self.question_entry.focus_set()
            return
        if self.is_generating:
            return

        self.question_entry.delete(0, "end")

        # Build prompt using conversation history
        task = f"""
You are answering a student's question about an uploaded PDF.

CURRENT QUESTION:
{question}

PREVIOUS CONVERSATION:
{self.pdf_conversation_history[-6:]}

IMPORTANT INSTRUCTIONS:

1. Answer the CURRENT QUESTION directly.
2. Use the uploaded PDF as your primary source.
3. Use previous conversation only to understand references such as:
   "it", "this", "that", "the first one", "the example", etc.
4. Stay focused on the current topic.
5. Do not switch to unrelated concepts.
6. If the student asks for an example, give an example of the
   concept currently being discussed.
7. If the answer is not available in the PDF, clearly say so.
8. Give a complete answer and do not stop in the middle of a sentence.
"""

        self.start_pdf_question(task, question)

    def start_pdf_question(self, task, question):
        if self.is_generating:
            return

        self.set_busy(True, question)
        threading.Thread(
            target=self.generate_pdf_question, args=(task, question),
            daemon=True
        ).start()

    def generate_pdf_question(self, task, question):
        try:
            result = self.ai.analyze_pdf(self.pdf_text, task, max_tokens=350)
        except Exception as error:
            print(f"PDF Question Error: {error}")
            result = "Couldn't answer that. Try again in a moment."

        self.after(0, lambda: self.finish_pdf_question(question, result))

    def finish_pdf_question(self, question, result):
        if not self.winfo_exists():
            return

        self.pdf_conversation_history.append(
            {"question": question, "answer": result}
        )
        # Keep only the latest 6 exchanges
        self.pdf_conversation_history = self.pdf_conversation_history[-6:]

        self.set_busy(False)
        self.show_result(result, title=question)

    # State and display

    def update_controls(self):
        """Actions only work once a PDF is loaded and nothing is running."""
        ready = bool(self.pdf_text) and not self.is_generating
        state = "normal" if ready else "disabled"
        for button in self.analysis_buttons:
            button.configure(state=state)
        t.set_primary_enabled(self.ask_button, ready)

        self.upload_button.configure(
            text="Replace PDF" if self.pdf_text else "Choose PDF",
            state="disabled" if self.is_generating else "normal"
        )
        style = (dict(fg_color=t.CARD, hover_color=t.RAISED,
                      text_color=t.TEXT, border_width=1,
                      border_color=t.FIELD_BORDER)
                 if self.pdf_text else
                 dict(fg_color=t.ACCENT, hover_color=t.ACCENT_HOVER,
                      text_color="#FFFFFF", border_width=0))
        self.upload_button.configure(**style)

    def set_busy(self, busy, title=None):
        self.is_generating = busy
        if busy:
            self.result_title.configure(text=self._short(title))
            self.result_status.configure(text="Working on it")
            self.show_result("", title=title)
        else:
            self.result_status.configure(text="")
        self.update_controls()

    def show_result(self, text, title=None, muted=False):
        if title is not None:
            self.result_title.configure(text=self._short(title))

        self.result_box.configure(state="normal",
                                  text_color=t.MUTED if muted else t.TEXT)
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", (text or "").strip())
        self.result_box.configure(state="disabled")
        self.fit_result_height()

    def fit_result_height(self):
        """Grow the result box to fit its text."""
        box = self.result_box._textbox
        box.update_idletasks()
        lines = box.count("1.0", "end", "displaylines")
        lines = lines[0] if lines else 1
        line_px = t.fonts()["body"].metrics("linespace") + 6
        height = max(40, lines * line_px + 12)
        if abs(self.result_box.cget("height") - height) > 2:
            self.result_box.configure(height=height)

    @staticmethod
    def _short(text, limit=72):
        text = " ".join((text or "").split())
        return text if len(text) <= limit else text[:limit - 1] + "…"