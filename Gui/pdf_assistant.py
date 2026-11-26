import customtkinter as ctk
from tkinter import filedialog
import threading

from Core.pdf_processor import PDFProcessor
from Core.gemini_service import GeminiService


class PDFAssistantFrame(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color="#F4F6FA")

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

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    def create_header(self):

        ctk.CTkLabel(
            self,
            text="PDF Study Assistant",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=35,
            pady=(30, 5)
        )

        ctk.CTkLabel(
            self,
            text="Upload your study material and let AI help you understand it.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(
            anchor="w",
            padx=35,
            pady=(0, 25)
        )

    # ---------------------------------------------------------
    # PDF UPLOAD SECTION
    # ---------------------------------------------------------

    def create_upload_section(self):

        self.upload_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        self.upload_card.pack(
            fill="x",
            padx=35,
            pady=10
        )

        ctk.CTkLabel(
            self.upload_card,
            text="Upload Study Material",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        self.upload_button = ctk.CTkButton(
            self.upload_card,
            text="Choose PDF File",
            height=40,
            fg_color="#3157D5",
            hover_color="#2546B5",
            command=self.upload_pdf
        )

        self.upload_button.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        self.file_label = ctk.CTkLabel(
            self.upload_card,
            text="No PDF selected",
            font=ctk.CTkFont(size=12),
            text_color="#8993A5"
        )

        self.file_label.pack(
            anchor="w",
            padx=20,
            pady=(5, 20)
        )

    # ---------------------------------------------------------
    # ANALYSIS SECTION
    # ---------------------------------------------------------

    def create_analysis_section(self):

        self.analysis_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        self.analysis_card.pack(
            fill="x",
            padx=35,
            pady=10
        )

        ctk.CTkLabel(
            self.analysis_card,
            text="AI Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        # -----------------------------------------------------
        # PDF ANALYSIS BUTTONS
        # -----------------------------------------------------

        self.analysis_buttons = []

        actions = [
            (
                "Generate Summary",
                "Summarize this PDF into clear, easy-to-understand study notes."
            ),
            (
                "Important Points",
                "Extract the most important points from this PDF."
            ),
            (
                "Generate MCQs",
                "Generate 10 multiple-choice questions with four options each and provide the correct answers."
            ),
            (
                "Explain Concepts",
                "Explain the main concepts covered in this PDF in simple language."
            )
        ]

        for title, task in actions:

            button = ctk.CTkButton(
                self.analysis_card,
                text=title,
                height=38,
                fg_color="#3157D5",
                hover_color="#2546B5",
                command=lambda t=task: self.start_analysis(t)
            )

            button.pack(
                fill="x",
                padx=20,
                pady=5
            )

            self.analysis_buttons.append(button)

        # -----------------------------------------------------
        # PDF QUESTION ANSWERING
        # -----------------------------------------------------

        ctk.CTkLabel(
            self.analysis_card,
            text="Ask a Question About Your PDF",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        self.question_entry = ctk.CTkEntry(
            self.analysis_card,
            height=42,
            placeholder_text="Ask something about your study material..."
        )

        self.question_entry.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.ask_button = ctk.CTkButton(
            self.analysis_card,
            text="Ask AI",
            height=38,
            fg_color="#16865C",
            hover_color="#116B49",
            command=self.ask_question
        )

        self.ask_button.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            self.analysis_card,
            text="Select an action to analyze your uploaded PDF.",
            font=ctk.CTkFont(size=12),
            text_color="#8993A5"
        ).pack(
            anchor="w",
            padx=20,
            pady=(8, 20)
        )

    # ---------------------------------------------------------
    # RESULT SECTION
    # ---------------------------------------------------------

    def create_result_section(self):

        self.result_card = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E5E9F0"
        )

        self.result_card.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(10, 30)
        )

        ctk.CTkLabel(
            self.result_card,
            text="AI Results",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#202938"
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        self.result_box = ctk.CTkTextbox(
            self.result_card,
            height=300,
            corner_radius=8,
            fg_color="#F4F6FA",
            text_color="#202938",
            font=ctk.CTkFont(size=13),
            wrap="word"
        )

        self.result_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.result_box.insert(
            "1.0",
            "Your AI-generated PDF analysis will appear here."
        )

        self.result_box.configure(state="disabled")

    # ---------------------------------------------------------
    # UPLOAD PDF
    # ---------------------------------------------------------

    def upload_pdf(self):

        file_path = filedialog.askopenfilename(
            title="Select Study PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not file_path:
            return

        self.file_label.configure(
            text="Extracting PDF text..."
        )

        self.upload_button.configure(
            state="disabled"
        )

        threading.Thread(
            target=self.extract_pdf,
            args=(file_path,),
            daemon=True
        ).start()

    # ---------------------------------------------------------
    # EXTRACT PDF
    # ---------------------------------------------------------

    def extract_pdf(self, file_path):

        text = self.pdf_processor.extract_text(file_path)

        self.after(
            0,
            lambda: self.finish_extraction(
                file_path,
                text
            )
        )

    def finish_extraction(self, file_path, text):

        if not self.winfo_exists():
            return

        self.upload_button.configure(
            state="normal"
        )

        if not text:

            self.pdf_text = ""
            self.pdf_path = ""
            self.pdf_conversation_history = []

            self.file_label.configure(
                text="Could not extract text from this PDF."
            )

            return

        self.pdf_text = text
        self.pdf_path = file_path

        # Clear conversation when a new PDF is uploaded
        self.pdf_conversation_history = []

        filename = file_path.replace("\\", "/").split("/")[-1]

        self.file_label.configure(
            text=f"Selected: {filename}"
        )

        self.show_result(
            "PDF uploaded successfully!\n\n"
            "Text extracted successfully. You can now choose "
            "an AI analysis action or ask a question."
        )

    # ---------------------------------------------------------
    # NORMAL PDF ANALYSIS
    # ---------------------------------------------------------

    def start_analysis(self, task):

        if not self.pdf_text:

            self.show_result(
                "Please upload a PDF before starting AI analysis."
            )

            return

        if self.is_generating:
            return

        self.is_generating = True

        # Disable analysis buttons
        for button in self.analysis_buttons:
            button.configure(
                state="disabled"
            )

        # Disable Ask AI too
        self.ask_button.configure(
            state="disabled"
        )

        self.show_result(
            "AI is analyzing your PDF. Please wait..."
        )

        threading.Thread(
            target=self.generate_analysis,
            args=(task,),
            daemon=True
        ).start()

    def generate_analysis(self, task):

        result = self.ai.analyze_pdf(
    self.pdf_text,
    task,
    max_tokens=1500
)

        self.after(
            0,
            lambda: self.finish_analysis(result)
        )

    def finish_analysis(self, result):

        if not self.winfo_exists():
            return

        self.show_result(result)

        self.is_generating = False

        # Re-enable analysis buttons
        for button in self.analysis_buttons:
            button.configure(
                state="normal"
            )

        # Re-enable Ask AI
        self.ask_button.configure(
            state="normal"
        )

    # ---------------------------------------------------------
    # ASK QUESTION
    # ---------------------------------------------------------

    def ask_question(self):

        question = self.question_entry.get().strip()

        # Check PDF
        if not self.pdf_text:

            self.show_result(
                "Please upload a PDF before asking a question."
            )

            return

        # Check question
        if not question:

            self.show_result(
                "Please enter a question first."
            )

            return

        # Prevent multiple requests
        if self.is_generating:
            return

        # Clear input
        self.question_entry.delete(
            0,
            "end"
        )

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

        self.start_pdf_question(
            task,
            question
        )

    # ---------------------------------------------------------
    # START PDF QUESTION
    # ---------------------------------------------------------

    def start_pdf_question(self, task, question):

        if self.is_generating:
            return

        self.is_generating = True

        # Disable Ask AI
        self.ask_button.configure(
            state="disabled"
        )

        # Also disable analysis buttons
        for button in self.analysis_buttons:
            button.configure(
                state="disabled"
            )

        self.show_result(
            "AI is thinking..."
        )

        threading.Thread(
            target=self.generate_pdf_question,
            args=(task, question),
            daemon=True
        ).start()

    # ---------------------------------------------------------
    # GENERATE PDF QUESTION ANSWER
    # ---------------------------------------------------------

    def generate_pdf_question(self, task, question):

        try:

            result = self.ai.analyze_pdf(
                self.pdf_text,
    task,
    max_tokens=350
)

        except Exception as e:

            print(f"PDF Question Error: {e}")

            result = (
                "Sorry, I couldn't generate an answer. "
                "Please try again."
            )

        self.after(
            0,
            lambda: self.finish_pdf_question(
                question,
                result
            )
        )

    # ---------------------------------------------------------
    # FINISH PDF QUESTION
    # ---------------------------------------------------------

    def finish_pdf_question(self, question, result):

        if not self.winfo_exists():
            return

        self.show_result(result)

        # Save conversation
        self.pdf_conversation_history.append(
            {
                "question": question,
                "answer": result
            }
        )

        # Keep only the latest 6 exchanges
        self.pdf_conversation_history = (
            self.pdf_conversation_history[-6:]
        )

        self.is_generating = False

        # Re-enable Ask AI
        self.ask_button.configure(
            state="normal"
        )

        # Re-enable analysis buttons
        for button in self.analysis_buttons:
            button.configure(
                state="normal"
            )

    # ---------------------------------------------------------
    # SHOW RESULT
    # ---------------------------------------------------------

    def show_result(self, text):

        self.result_box.configure(
            state="normal"
        )

        self.result_box.delete(
            "1.0",
            "end"
        )

        self.result_box.insert(
            "1.0",
            text
        )

        self.result_box.configure(
            state="disabled"
        )