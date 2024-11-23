from app.dto.company_scraped_data_dto import CompanyDTO, ProductDTO
from website_identifier_service import get_company_website
import requests
from bs4 import BeautifulSoup

class CompanyWebsiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.visited_urls = set()

    # Fetches a web page and returns a BeautifulSoup object.
    def get_soup(self, url):
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    # Extracts internal links from the given BeautifulSoup object.
    def get_internal_links(self, soup):
        links = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith(self.base_url) or href.startswith('/'):
                full_url = self.get_full_url(href)
                links.add(full_url)
        return links

    # Converts a relative URL to an absolute URL.
    def get_full_url(self, href):
        if href.startswith("http"):
            return href
        else:
            return f"{self.base_url}/{href.lstrip('/')}"

    # Extracts main content and internal links from the given URL.
    def extract_main_content(self, url):
        soup = self.get_soup(url)
        content = [p.get_text(strip=True) for p in soup.find_all("p")]
        links = self.get_internal_links(soup)
        return "\n".join(content), links

    # Recursively crawl website up to maximum depth
    def crawl(self, url, depth=0, max_depth=2):
        if depth > max_depth or url in self.visited_urls:
            return
        print(f"Crawling: {url} at depth {depth}")
        self.visited_urls.add(url)
        content, links = self.extract_main_content(url)
        # Process content as needed
        for link in links:
            self.crawl(link, depth + 1, max_depth)


if __name__ == "__main__":
    company_name = "urban calm coffee company"  # Replace with the target company name
    csv_file_path = "filtered_companies_canada.csv"  # Path to your CSV file

    # Get the company's website
    company_url = "https://" + get_company_website(company_name, csv_file_path)
    if company_url:
        print(f"Found website: {company_url}")

    scraper = CompanyWebsiteScraper(company_url)
    content, links = scraper.extract_main_content(company_url)
    scraper.crawl(company_url)
