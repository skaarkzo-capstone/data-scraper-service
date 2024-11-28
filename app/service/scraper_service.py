import subprocess
from utilities.pdf_processor import PDFProcessor

def clear_directories():
    processor = PDFProcessor()
    processor.clear_pdf_directory()
    processor.clear_temp_directory()
    processor.clear_json_directory()
    print("Cleared all directories")

def run_company_data_service(company_name):
    print(f"Running company_data_service.py for {company_name}...")
    subprocess.run(
        ["python", "app/service/company_data_service.py", company_name], 
        capture_output=True, text=True
    )

def run_sedar_automation(company_name):
    print(f"Running sedar_automation.py for {company_name}...")
    subprocess.run(
        ["python", "app/service/sedar_automation.py", company_name], 
        capture_output=True, text=True
    )

def combine_all_json_files():
    processor = PDFProcessor()
    processor.combine_json_files("combined_results.json")

if __name__ == "__main__":
    company_name = "Shopify"

    clear_directories()

    run_company_data_service(company_name)

    run_sedar_automation(company_name)
    
    combine_all_json_files()

    print("All tasks completed.")
