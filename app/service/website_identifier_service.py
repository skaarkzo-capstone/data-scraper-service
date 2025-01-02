import csv
import logging
import traceback

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_company_website(company_name, csv_file_path):
    """
    Get the company's website by searching for it in the provided CSV.
    """
    logger.info("Getting company website for %s from %s", company_name, csv_file_path)
    try:
        website = search_csv_for_website(company_name, csv_file_path)
        if website:
            logger.info("Found website in CSV: %s", website)
        return website
    except Exception as e:
        logger.exception("Error getting company website.")
        traceback.print_exc()
        return None


def search_csv_for_website(company_name, csv_file_path):
    """
    Search for a company website in a given CSV file.
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Key names based on CSV file
                if row['name'].strip().lower() == company_name.strip().lower():
                    return row['website'].strip()
    except Exception as e:
        logger.exception("Error reading CSV file.")
        traceback.print_exc()
    return None
