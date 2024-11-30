import csv

# Get the company's website
def get_company_website(company_name, csv_file_path):
    website = search_csv_for_website(company_name, csv_file_path)
    if website:
        print(f"Found website in CSV: {website}")

    return website

# Search for a company website in a given csv file
def search_csv_for_website(company_name, csv_file_path):
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Key names based on csv file
                if row['name'].strip().lower() == company_name.strip().lower():
                    return row['website'].strip()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return None