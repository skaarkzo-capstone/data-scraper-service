import glob
import hashlib
import json
import os
import shutil
import time
import requests
import logging
import traceback

from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PDFScraper:
    """
    Provides tools for downloading, extracting, analyzing, and managing PDF documents.
    """

    def __init__(
            self,
            pdf_directory='downloaded_pdfs',
            temp_directory='temp_downloads',
            json_directory='json_files',
            headers=None
    ):
        """
        Initialize the PDFScraper with directory paths and HTTP headers.
        Ensures all required directories exist.
        """
        logger.info("Initializing PDFScraper.")
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
        Downloads a PDF from the given URL, saves it with a unique filename, and extracts its text content.
        """
        logger.info("Processing PDF: %s", pdf_url)
        try:
            response = self._download_pdf_content(pdf_url)
            if extract_pdfs:
                # Generate a unique filename and save the PDF
                file_path = self._save_pdf_content(response, pdf_url)

                # Extract text from the PDF
                text = self._extract_text_from_pdf(file_path)
                return {"url": pdf_url, "file_path": file_path, "content": text}
            else:
                return {"url": pdf_url}
        except Exception as e:
            logger.exception("Error downloading PDF from %s", pdf_url)
            traceback.print_exc()
            return None

    @staticmethod
    def make_safe_filename(filename):
        """
        Replace invalid filename characters with underscores.
        """
        return "".join(c if c.isalnum() or c in (' ', '.', '_') else '_' for c in filename)

    def clear_pdf_directory(self):
        """
        Delete and recreate the PDF directory.
        """
        logger.info("Clearing PDF directory.")
        try:
            shutil.rmtree(self.pdf_directory, ignore_errors=True)
            os.makedirs(self.pdf_directory)
        except Exception as e:
            logger.exception("Error clearing PDF directory.")
            traceback.print_exc()

    def clear_json_directory(self):
        """
        Delete and recreate the JSON directory.
        """
        logger.info("Clearing JSON directory.")
        try:
            shutil.rmtree(self.json_directory, ignore_errors=True)
            os.makedirs(self.json_directory)
        except Exception as e:
            logger.exception("Error clearing JSON directory.")
            traceback.print_exc()

    def clear_temp_directory(self):
        """
        Delete and recreate the temporary directory.
        """
        logger.info("Clearing temp directory.")
        try:
            shutil.rmtree(self.temp_directory, ignore_errors=True)
            os.makedirs(self.temp_directory)
        except Exception as e:
            logger.exception("Error clearing temp directory.")
            traceback.print_exc()

    def save_to_json(self, data, output_file):
        """
        Save the provided data to a JSON file in the json_directory.
        """
        logger.info("Saving data to JSON: %s", output_file)
        try:
            output_path = os.path.join(self.json_directory, output_file)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info("Data successfully saved to %s", output_path)
        except Exception as e:
            logger.exception("Error saving data to JSON.")
            traceback.print_exc()

    def analyse_and_extract_pdf(self, pdf_path, keywords):
        """
        Extract text from a PDF, then search the extracted text for the specified keywords.
        """
        logger.info("Analysing PDF: %s", pdf_path)
        extracted_data = {}
        try:
            text = self._extract_text_from_pdf(pdf_path)
            for keyword in keywords:
                matching_lines = [
                    line.strip() for line in text.splitlines()
                    if keyword.lower() in line.lower()
                ]
                if matching_lines:
                    extracted_data[keyword] = matching_lines
            logger.info("Extraction completed for %s.", pdf_path)
        except Exception as e:
            logger.exception("Error analysing %s", pdf_path)
            traceback.print_exc()
        return extracted_data

    def move_pdf(self, pdf_path):
        """
        Move a PDF to the designated pdf_directory with a safe filename.
        """
        logger.info("Moving PDF: %s", pdf_path)
        try:
            file_name = os.path.basename(pdf_path)
            safe_file_name = self.make_safe_filename(file_name)
            destination_path = os.path.join(self.pdf_directory, safe_file_name)
            shutil.move(pdf_path, destination_path)
            logger.info("Moved PDF to %s.", destination_path)
            return destination_path
        except Exception as e:
            logger.exception("Error moving PDF %s", pdf_path)
            traceback.print_exc()
            return None

    def rename_and_move_pdf(self, original_path: str, company_name: str) -> str:
        """
        Rename a PDF file using a unique identifier based on the company name and current time,
        then move it to the pdf_directory. Returns the new file path.
        """
        logger.info("Renaming and moving PDF for company: %s", company_name)
        unique_id = hashlib.md5(f"{time.time()}_{company_name}".encode()).hexdigest()[:10]
        new_name = f"{company_name.replace(' ', '_')}_{unique_id}.pdf"
        new_path = os.path.join(self.pdf_directory, new_name)
        try:
            os.rename(original_path, new_path)
            logger.info("Moved and renamed file to: %s", new_path)
        except Exception as e:
            logger.exception("Error renaming and moving file.")
            traceback.print_exc()
            raise
        return new_path

    def combine_json_files(self, output_file="combined_data.json"):
        """
        Combine all JSON files in the json_directory into a single JSON file.
        """
        logger.info("Combining JSON files into %s", output_file)
        combined_data = {}
        try:
            json_files = glob.glob(os.path.join(self.json_directory, "*.json"))
            for json_file in json_files:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    combined_data.update(data)
            self.save_to_json(combined_data, output_file)
            logger.info("Combined JSON data saved to %s", output_file)
        except Exception as e:
            logger.exception("Error combining JSON files.")
            traceback.print_exc()

    def _download_pdf_content(self, pdf_url, timeout=30):
        """
        Internal helper method to download PDF content from a URL.
        Raises an exception if the request fails.
        """
        response = requests.get(pdf_url, headers=self.headers, timeout=timeout)
        response.raise_for_status()
        return response

    def _save_pdf_content(self, response, pdf_url):
        """
        Internal helper method to create a unique filename and save the PDF content.
        Returns the full path where the PDF is saved.
        """
        file_name = os.path.basename(pdf_url) or "downloaded.pdf"
        if not file_name.lower().endswith('.pdf'):
            file_name += '.pdf'
        unique_id = hashlib.md5(f"{time.time()}_{pdf_url}".encode()).hexdigest()[:10]
        safe_file_name = self.make_safe_filename(file_name)
        unique_file_name = f"{unique_id}_{safe_file_name}"
        pdf_path = os.path.join(self.pdf_directory, unique_file_name)

        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return pdf_path

    def _extract_text_from_pdf(self, pdf_path):
        """
        Internal helper method to read text from a PDF file using PyPDF2.
        Returns the extracted text as a string.
        """
        logger.info("Extracting text from PDF: %s", pdf_path)
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            logger.exception("Error extracting text from %s", pdf_path)
            traceback.print_exc()
        return text
