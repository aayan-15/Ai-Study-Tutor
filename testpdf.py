
from Core.pdf_processor import PDFProcessor

processor = PDFProcessor()

file_path = input("Enter PDF file path: ")

text = processor.extract_text(file_path)

if text:
    print("\nPDF extracted successfully!")
    print("\nExtracted Content:\n")
    print(text[:3000])
else:
    print("Could not extract text from this PDF.")
