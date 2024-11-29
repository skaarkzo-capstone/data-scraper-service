import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth

from app.scraper.pdf_scraper import PDFScraper
from app.util.sedar_keywords import sustainability_keywords
from app.util.sedar_xpaths import *

# This is the Sedar Automation. It will automate the process of entering the data (such as company name) to get the Anual Report pdf then scrape its data using keywords.

class SedarAutomation:
    def __init__(self, extract_pdfs: bool = True, pdf_directory: str = 'downloaded_pdfs', temp_directory: str = 'temp_downloads', json_directory: str = 'json_files'):
        self.base_url = 'https://www.sedarplus.ca'
        self.extract_pdfs = extract_pdfs
        self.pdf_directory = pdf_directory
        self.temp_directory = temp_directory
        self.json_directory = json_directory

        # Initialize PDFScraper with both PDF and JSON directories
        self.pdf_processor = PDFScraper(pdf_directory=self.pdf_directory, temp_directory=self.temp_directory, json_directory=self.json_directory)

        # Use keywords from the sedar_keywords file
        self.sustainability_keywords = sustainability_keywords

        # Initialize Selenium WebDriver
        self.driver = self.init_webdriver()
        self.data = {}

    def init_webdriver(self):
        chrome_options = Options()
        prefs = {
            "download.default_directory": os.path.abspath(self.temp_directory),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)

        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver

    def download_company_annual_report(self, company_name: str):
        print(f"Searching for company: {company_name}")
        driver = self.driver
        wait = WebDriverWait(driver, 20)

        filing_type = "Annual Report"
        from_date = "01/01/2024"
        to_date = "31/12/2024"

        try:
            # Enter form and download the PDF
            driver.get(self.base_url)
            print("Loaded SEDAR+ homepage")

            # Going to Search Page
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, SEARCH_BUTTON)))
            search_button.click()
            print("Clicked Search button")
            wait.until(EC.presence_of_element_located((By.XPATH, PROFILE_NAME_INPUT)))
            print("Search page loaded")

            # Search for company
            profile_input = driver.find_element(By.XPATH, PROFILE_NAME_INPUT)
            profile_input.send_keys(company_name)
            print(f"Entered company name: {company_name}")
            time.sleep(2)
            profile_dropdown_option = wait.until(EC.element_to_be_clickable(
                (By.XPATH, PROFILE_DROPDOWN_OPTION.format(company_name=company_name))
            ))
            profile_dropdown_option.click()
            print(f"Selected company: {company_name}")
            time.sleep(2)

            # Search for Annual Reports
            filing_type_input = driver.find_element(By.XPATH, FILING_TYPE_INPUT)
            filing_type_input.click()
            filing_type_input.send_keys(filing_type)
            filing_type_option = wait.until(EC.element_to_be_clickable((By.XPATH, FILING_TYPE_OPTION)))
            filing_type_option.click()
            time.sleep(2)

            # Entering from date values
            from_date_input = driver.find_element(By.XPATH, FROM_DATE_INPUT)
            from_date_input.click()
            from_date_input.send_keys(from_date)
            time.sleep(2)

            # Entering to date values
            to_date_input = driver.find_element(By.XPATH, TO_DATE_INPUT)
            to_date_input.click()
            to_date_input.send_keys(to_date)
            time.sleep(2)

            # Click on Search button
            search_submit_button = driver.find_element(By.XPATH, SEARCH_SUBMIT_BUTTON)
            search_submit_button.click()
            print("Clicked Search button")
            time.sleep(5)

            # Download PDF
            download_pdf = wait.until(EC.presence_of_element_located((By.XPATH, DOWNLOAD_PDF)))
            download_pdf.click()
            print("Downloading PDF...")
            time.sleep(10)

            # Get the downloaded file
            files = os.listdir(self.temp_directory)
            if not files:
                raise FileNotFoundError("No files found in the temp_downloads folder.")
            latest_file = max([os.path.join(self.temp_directory, f) for f in files], key=os.path.getctime)
            print(f"Downloaded file: {latest_file}")

            # Rename and move the file
            moved_file_path = self.pdf_processor.rename_and_move_pdf(latest_file, company_name)

            # Extract and process the file
            extracted_data = self.pdf_processor.analyse_and_extract_pdf(moved_file_path, self.sustainability_keywords)
            self.data[company_name] = extracted_data

            return moved_file_path

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            if driver.service.is_connectable():
                driver.quit()

    def save_to_json(self, output_file):
        self.pdf_processor.save_to_json(self.data, output_file)

if __name__ == "__main__":
    company_name = sys.argv[1]

    scraper = SedarAutomation()
    
    # Download, process, and analyze the report
    pdf_path = scraper.download_company_annual_report(company_name)
    
    # Save the extracted data to JSON
    output_file = f"{company_name.replace(' ', '_')}_sustainability_data.json"
    scraper.save_to_json(output_file)
