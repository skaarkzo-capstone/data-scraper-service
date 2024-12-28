import argparse
import concurrent.futures

from app.scraper.pdf_scraper import PDFScraper
from app.service.utils import run_subprocess

# Task registry for dynamically adding and managing tasks
TASK_REGISTRY = {}

# Register a new task in the registry
def register_task(name, function):
    TASK_REGISTRY[name] = function

# Clears the downloads, json and temp folders
def clear_directories():
    processor = PDFScraper()
    processor.clear_pdf_directory()
    processor.clear_temp_directory()
    processor.clear_json_directory()
    print("Cleared all directories")

# Script to run a python scripts in parallel
def run_tasks_in_parallel(tasks, company_name):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(task, company_name) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error occurred while running task: {e}")

# Runs the website scraper
def run_company_website_scraper(company_name):
    print(f"Running company_website_scraper for {company_name}...")
    run_subprocess("app.scraper.company_website_scraper", company_name)

# Runs the sedar automation scraper
def run_sedar_automation(company_name):
    print(f"Running sedar_automation for {company_name}...")
    run_subprocess("app.automation.sedar_automation", company_name)

# Registering tasks
register_task("website", run_company_website_scraper)
register_task("sedar", run_sedar_automation)

# Combines all json files in the json folder
def combine_all_json_files(output_file="combined_results.json"):
    processor = PDFScraper()
    processor.combine_json_files(output_file)
    print(f"Combined JSON files into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run automation tasks for a company.")
    parser.add_argument("company_name", type=str, help="The name of the company to process.")
    parser.add_argument("--tasks", nargs="*", choices=TASK_REGISTRY.keys(), help="Run the scrapers and automations.")

    print("Starting the automation tasks...")

    args = parser.parse_args()

    print("Starting the automation tasks...")

    # Clears the downloads, json and temp folders
    clear_directories()

    # Runs the scrapers and automations in parallel
    if args.tasks:
        tasks_to_run = [TASK_REGISTRY[task] for task in args.tasks]
        run_tasks_in_parallel(tasks_to_run, args.company_name)
    
    # Combines all json files in the json folder
    combine_all_json_files()

    print("All tasks completed.")
