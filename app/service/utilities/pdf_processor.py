import os
import requests
from PyPDF2 import PdfReader
import hashlib
import time

class PDFProcessor:
    def __init__(self, pdf_directory='downloaded_pdfs', headers=None):
        self.pdf_directory = pdf_directory
        self.headers = headers or {"User-Agent": "Mozilla/5.0"}

        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)

    def process_pdf(self, pdf_url, extract_pdfs=True):
        print(f"Processing PDF: {pdf_url}")
        try:
            response = requests.get(pdf_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            if extract_pdfs:
                # Generate a unique file name
                file_name = os.path.basename(pdf_url)
                if not file_name.lower().endswith('.pdf'):
                    file_name += '.pdf'

                # Create a unique identifier using timestamp and URL hash
                unique_id = hashlib.md5(f"{time.time()}_{pdf_url}".encode()).hexdigest()[:10]
                safe_file_name = self.make_safe_filename(file_name)
                unique_file_name = f"{unique_id}_{safe_file_name}"

                pdf_path = os.path.join(self.pdf_directory, unique_file_name)

                # Save the PDF to disk
                with open(pdf_path, "wb") as f:
                    f.write(response.content)

                # Extract text from the PDF
                text = ""
                try:
                    with open(pdf_path, 'rb') as f:
                        reader = PdfReader(f)
                        text = "\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception as e:
                    print(f"Error extracting text from {pdf_path}: {e}")

                return {"url": pdf_url, "file_path": pdf_path, "content": text}
            else:
                return {"url": pdf_url}
        except Exception as e:
            print(f"Error downloading PDF from {pdf_url}: {e}")
            return None

    @staticmethod
    def make_safe_filename(filename):
        return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)
