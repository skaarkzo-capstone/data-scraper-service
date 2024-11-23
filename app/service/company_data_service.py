from app.dto.company_scraped_data_dto import CompanyDTO, ProductDTO
from website_identifier_service import get_company_website
import requests
from bs4 import BeautifulSoup

class CompanyWebsiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "Mozilla/5.0"}

    # Fetches a web page and returns a BeautifulSoup object.
    def get_soup(self, url):
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    # Extracts main content from a given url
    def extract_main_content(self, url):
        soup = self.get_soup(url)
        content = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(content)

if __name__ == "__main__":
    company_name = "chaotic closet"  # Replace with the target company name
    csv_file_path = "filtered_companies_canada.csv"  # Path to your CSV file

    # Get the company's website
    company_url = "https://" + get_company_website(company_name, csv_file_path)
    if company_url:
        print(f"Found website: {company_url}")

    scraper = CompanyWebsiteScraper(company_url)
    soup = scraper.get_soup(company_url)
    content = scraper.extract_main_content(company_url)
    print(soup.title.string)
    print(content)
