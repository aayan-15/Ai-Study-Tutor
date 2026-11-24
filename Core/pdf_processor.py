
from pypdf import PdfReader


class PDFProcessor:

    def extract_text(self, file_path):

        try:
            reader = PdfReader(file_path)

            extracted_text = ""

            for page_number, page in enumerate(reader.pages, start=1):

                page_text = page.extract_text()

                if page_text:
                    extracted_text += f"\n--- Page {page_number} ---\n"
                    extracted_text += page_text

            if not extracted_text.strip():
                return None

            return extracted_text

        except Exception as e:
            print(f"PDF Extraction Error: {e}")
            return None
