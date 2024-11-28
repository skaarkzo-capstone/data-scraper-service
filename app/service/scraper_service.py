import subprocess
from app.scraper.pdf_scraper import PDFScraper

def clear_directories():
    processor = PDFScraper()
    processor.clear_pdf_directory()
    processor.clear_temp_directory()
    processor.clear_json_directory()
    print("Cleared all directories")

def run_company_website_scraper(company_name):
    print(f"Running company_website_scraper.py for {company_name}...")
    subprocess.run(
        ["python", "app/scraper/company_website_scraper.py", company_name],
        capture_output=True, text=True
    )

def run_sedar_automation(company_name):
    print(f"Running sedar_automation.py for {company_name}...")
    subprocess.run(
        ["python", "app/automation/sedar_automation.py", company_name],
        capture_output=True, text=True
    )

def combine_all_json_files():
    processor = PDFScraper()
    processor.combine_json_files("combined_results.json")

if __name__ == "__main__":
    company_name = "Shopify"

    clear_directories()

    run_company_website_scraper(company_name)

    run_sedar_automation(company_name)
    
    combine_all_json_files()

    print("All tasks completed.")
