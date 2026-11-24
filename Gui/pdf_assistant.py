
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

        self.create_header()
        self.create_upload_section()
        self.create_analysis_section()
        self.create_result_section()

    def create_header(self):

        ctk.CTkLabel(
            self,
            text="PDF Study Assistant",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#202938"
        ).pack(anchor="w", padx=35, pady=(30, 5))

        ctk.CTkLabel(
            self,
            text="Upload your study material and let AI help you understand it.",
            font=ctk.CTkFont(size=14),
            text_color="#778195"
        ).pack(anchor="w", padx=35, pady=(0, 25))

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
        ).pack(anchor="w", padx=20, pady=(20, 10))

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
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.analysis_buttons = []

        actions = [
            ("Generate Summary", "Summarize this PDF into clear, easy-to-understand study notes."),
            ("Important Points", "Extract the most important points from this PDF."),
            ("Generate MCQs", "Generate 10 multiple-choice questions with four options each and provide the correct answers."),
            ("Explain Concepts", "Explain the main concepts covered in this PDF in simple language.")
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


        # PDF Question Answering

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
        ).pack(anchor="w", padx=20, pady=(8, 20))

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
        ).pack(anchor="w", padx=20, pady=(20, 10))

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

    def upload_pdf(self):

        file_path = filedialog.askopenfilename(
            title="Select Study PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not file_path:
            return

        self.file_label.configure(text="Extracting PDF text...")

        self.upload_button.configure(state="disabled")

        threading.Thread(
            target=self.extract_pdf,
            args=(file_path,),
            daemon=True
        ).start()

    def extract_pdf(self, file_path):

        text = self.pdf_processor.extract_text(file_path)

        self.after(
            0,
            lambda: self.finish_extraction(file_path, text)
        )

    def finish_extraction(self, file_path, text):

        if not self.winfo_exists():
            return

        self.upload_button.configure(state="normal")

        if not text:
            self.pdf_text = ""
            self.pdf_path = ""

            self.file_label.configure(
                text="Could not extract text from this PDF."
            )

            return

        self.pdf_text = text
        self.pdf_path = file_path

        filename = file_path.replace("\\", "/").split("/")[-1]

        self.file_label.configure(
            text=f"Selected: {filename}"
        )

        self.show_result(
            "PDF uploaded successfully!\n\n"
            "Text extracted successfully. You can now choose an AI analysis action."
        )

    def start_analysis(self, task):

        if not self.pdf_text:
            self.show_result("Please upload a PDF before starting AI analysis.")
            return

        if self.is_generating:
            return

        self.is_generating = True

        for button in self.analysis_buttons:
            button.configure(state="disabled")

        self.show_result("AI is analyzing your PDF. Please wait...")

        threading.Thread(
            target=self.generate_analysis,
            args=(task,),
            daemon=True
        ).start()

    def generate_analysis(self, task):

        result = self.ai.analyze_pdf(
            self.pdf_text,
            task
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

        for button in self.analysis_buttons:
            button.configure(state="normal")

    def show_result(self, text):

        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")

    
    def ask_question(self):

        question = self.question_entry.get().strip()

        if not self.pdf_text:
            self.show_result(
                "Please upload a PDF before asking a question."
            )
            return

        if not question:
            self.show_result(
                "Please enter a question first."
            )
            return

        task = f"""
Answer the following question using the uploaded PDF.

Student's question:
{question}

Instructions:
- Focus only on the student's question.
- Use the PDF as your primary source.
- Explain the answer in simple language.
- Give an example if helpful.
- Do not introduce unrelated topics.
- If the PDF does not contain the answer, say so clearly.
"""

        self.start_analysis(task)
        self.question_entry.delete(0, "end")

