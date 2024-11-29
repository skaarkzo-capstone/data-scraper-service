import glob
import hashlib
import json
import os
import shutil
import time

import requests
from PyPDF2 import PdfReader

"""
Overview:
The `PDFScraper` class provides tools for downloading, extracting, analyzing, and managing PDF documents from web sources. 
It supports features like generating unique filenames, extracting text content, keyword-based analysis, and saving data as JSON.
"""

class PDFScraper:
    def __init__(self, pdf_directory: str = 'downloaded_pdfs', temp_directory: str = 'temp_downloads', json_directory: str = 'json_files', headers=None):
        self.pdf_directory = pdf_directory
        self.temp_directory = temp_directory
        self.json_directory = json_directory
        self.headers = headers or {"User-Agent": "Mozilla/5.0"}

        # Ensure directories exist
        os.makedirs(self.pdf_directory, exist_ok=True)
        os.makedirs(self.json_directory, exist_ok=True)
        os.makedirs(self.temp_directory, exist_ok=True)

    def process_pdf(self, pdf_url, extract_pdfs=True):
        """
        Downloads a PDF, saves it with a unique filename, and extracts its text content.
        """
        print(f"Processing PDF: {pdf_url}")
        try:
            response = requests.get(pdf_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            if extract_pdfs:
                # Generate unique filename based on URL and timestamp
                file_name = os.path.basename(pdf_url) or "downloaded.pdf"
                if not file_name.lower().endswith('.pdf'):
                    file_name += '.pdf'

                unique_id = hashlib.md5(f"{time.time()}_{pdf_url}".encode()).hexdigest()[:10]
                safe_file_name = self.make_safe_filename(file_name)
                unique_file_name = f"{unique_id}_{safe_file_name}"
                pdf_path = os.path.join(self.pdf_directory, unique_file_name)

                # Save the PDF
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
        """
        Replaces invalid characters in a filename with underscores.
        """
        return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)

    def clear_pdf_directory(self):
        """
        Deletes and recreates the PDF directory.
        """
        shutil.rmtree(self.pdf_directory, ignore_errors=True)
        os.makedirs(self.pdf_directory)

    def clear_json_directory(self):
        """
        Deletes and recreates the JSON directory.
        """
        shutil.rmtree(self.json_directory, ignore_errors=True)
        os.makedirs(self.json_directory)

    def clear_temp_directory(self):
        """
        Deletes and recreates the temporary directory.
        """
        shutil.rmtree(self.temp_directory, ignore_errors=True)
        os.makedirs(self.temp_directory)

    def save_to_json(self, data, output_file):
        """
        Saves the given data to a JSON file in the JSON directory.
        """
        try:
            output_path = os.path.join(self.json_directory, output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Data successfully saved to {output_path}")
        except Exception as e:
            print(f"Error saving data to JSON: {e}")

    def analyse_and_extract_pdf(self, pdf_path, keywords):
        """
        Extracts text content from a PDF and searches for specified keywords.
        """
        print(f"Analysing PDF: {pdf_path}")
        extracted_data = {}
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)

            # Search for keywords in the extracted text
            for keyword in keywords:
                keyword_data = [line.strip() for line in text.splitlines() if keyword.lower() in line.lower()]
                if keyword_data:
                    extracted_data[keyword] = keyword_data

            print(f"Extraction completed for {pdf_path}.")
        except Exception as e:
            print(f"Error analysing {pdf_path}: {e}")

        return extracted_data

    def move_pdf(self, pdf_path):
        """
        Moves a PDF to the designated directory with a safe filename.
        """
        try:
            file_name = os.path.basename(pdf_path)
            safe_file_name = self.make_safe_filename(file_name)
            destination_path = os.path.join(self.pdf_directory, safe_file_name)
            shutil.move(pdf_path, destination_path)
            print(f"Moved PDF to {destination_path}.")
            return destination_path
        except Exception as e:
            print(f"Error moving PDF {pdf_path}: {e}")
            return None

    def rename_and_move_pdf(self, original_path: str, company_name: str) -> str:
        """
        Renames a PDF with a unique identifier and moves it to the designated directory.
        """
        unique_id = hashlib.md5(f"{time.time()}_{company_name}".encode()).hexdigest()[:10]
        new_name = f"{company_name.replace(' ', '_')}_{unique_id}.pdf"
        new_path = os.path.join(self.pdf_directory, new_name)
        try:
            os.rename(original_path, new_path)
            print(f"Moved and renamed file to: {new_path}")
        except Exception as e:
            print(f"Error renaming and moving file: {e}")
            raise
        return new_path

    def combine_json_files(self, output_file="combined_data.json"):
        """
        Combines all JSON files in the JSON directory into a single JSON file.
        """
        combined_data = {}
        try:
            json_files = glob.glob(os.path.join(self.json_directory, "*.json"))
            for json_file in json_files:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    combined_data.update(data)  # Merge JSON content
            self.save_to_json(combined_data, output_file)
            print(f"Combined JSON data saved to {output_file}")
        except Exception as e:
            print(f"Error combining JSON files: {e}")

