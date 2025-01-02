import argparse
import concurrent.futures
import logging
import traceback

from app.scraper.pdf_scraper import PDFScraper
from app.service.utils import run_subprocess

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Task registry for dynamically adding and managing tasks
TASK_REGISTRY = {}


def register_task(name, function):
    """
    Register a new task in the registry.
    """
    TASK_REGISTRY[name] = function


def clear_directories():
    """
    Clears the downloads, json, and temp folders.
    """
    try:
        processor = PDFScraper()
        processor.clear_pdf_directory()
        processor.clear_temp_directory()
        processor.clear_json_directory()
        logger.info("Cleared all directories.")
    except Exception as e:
        logger.exception("Error clearing directories.")
        traceback.print_exc()


def run_tasks_in_parallel(tasks, company_name):
    """
    Runs tasks (scrapers/automations) in parallel.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(task, company_name) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.exception("Error occurred while running task.")
                traceback.print_exc()


def run_company_website_scraper(company_name):
    """
    Runs the company website scraper.
    """
    logger.info("Running company_website_scraper for %s...", company_name)
    try:
        run_subprocess("app.scraper.company_website_scraper", company_name)
    except Exception as e:
        logger.exception("Error in run_company_website_scraper.")
        traceback.print_exc()


def run_sedar_automation(company_name):
    """
    Runs the sedar automation scraper.
    """
    logger.info("Running sedar_automation for %s...", company_name)
    try:
        run_subprocess("app.scraper.automation.sedar_automation", company_name)
    except Exception as e:
        logger.exception("Error in run_sedar_automation.")
        traceback.print_exc()


register_task("website", run_company_website_scraper)
register_task("sedar", run_sedar_automation)


def combine_all_json_files(output_file="combined_results.json"):
    """
    Combines all JSON files in the json folder.
    """
    try:
        processor = PDFScraper()
        processor.combine_json_files(output_file)
        logger.info("Combined JSON files into %s", output_file)
    except Exception as e:
        logger.exception("Error combining JSON files.")
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run automation tasks for a company.")
    parser.add_argument("company_name", type=str, help="The name of the company to process.")
    parser.add_argument("--tasks", nargs="*", choices=TASK_REGISTRY.keys(), help="Run the scrapers and automations.")
    logger.info("Starting the automation tasks...")

    args = parser.parse_args()
    logger.info("Starting the automation tasks...")

    clear_directories()

    if args.tasks:
        tasks_to_run = [TASK_REGISTRY[task] for task in args.tasks]
        run_tasks_in_parallel(tasks_to_run, args.company_name)

    combine_all_json_files()
    logger.info("All tasks completed.")
