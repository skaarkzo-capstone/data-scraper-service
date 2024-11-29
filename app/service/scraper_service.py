import argparse
import subprocess

from app.scraper.pdf_scraper import PDFScraper


def clear_directories():
    processor = PDFScraper()
    processor.clear_pdf_directory()
    processor.clear_temp_directory()
    processor.clear_json_directory()
    print("Cleared all directories")

def run_subprocess(module_path, *args):
    command = ["python", "-m", module_path, *args]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"Subprocess completed with return code {result.returncode}")
    if result.stdout:
        print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
    return result

def run_company_website_scraper(company_name):
    print(f"Running company_website_scraper for {company_name}...")
    run_subprocess("app.scraper.company_website_scraper", company_name)

def run_sedar_automation(company_name):
    print(f"Running sedar_automation for {company_name}...")
    run_subprocess("app.automation.sedar_automation", company_name)

def combine_all_json_files(output_file="combined_results.json"):
    processor = PDFScraper()
    processor.combine_json_files(output_file)
    print(f"Combined JSON files into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run automation tasks for a company.")
    parser.add_argument("company_name", type=str, help="The name of the company to process.")
    parser.add_argument("--website", action="store_true", help="Run the website scraper.")
    parser.add_argument("--sedar", action="store_true", help="Run the SEDAR automation.")

    print("Starting the automation tasks...")

    args = parser.parse_args()

    print("Starting the automation tasks...")

    clear_directories()

    if args.website:
        run_company_website_scraper(args.company_name)

    if args.sedar:
        run_sedar_automation(args.company_name)
    
    combine_all_json_files()

    print("All tasks completed.")
