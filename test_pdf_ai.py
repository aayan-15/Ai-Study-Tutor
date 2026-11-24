
from Core.pdf_processor import PDFProcessor
from Core.gemini_service import GeminiService

processor = PDFProcessor()
ai = GeminiService()

file_path = input("Enter PDF file path: ")

pdf_text = processor.extract_text(file_path)

if pdf_text:

    print("\nGenerating PDF summary...\n")

    result = ai.analyze_pdf(
        pdf_text,
        "Summarize this PDF into clear, easy-to-understand study notes."
    )

    print(result)

else:
    print("Could not read PDF.")

