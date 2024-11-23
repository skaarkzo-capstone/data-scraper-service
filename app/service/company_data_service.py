from app.dto.company_scraped_data_dto import CompanyDTO, ProductDTO
from website_identifier_service import get_company_website
import requests
from bs4 import BeautifulSoup

class CompanyWebsiteScraper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.visited_urls = set()

        # Define keywords for different sections, including 'products'
        self.keywords = [
            "about", "our story", "company", "about us",
            "sustainability", "csr", "environment", "climate",
            "annual report", "sustainability report", "investor relations", "financial report", "pdf", "download",
            "product", "products", "services", "offerings", "solutions", "features"
        ]

        # Exclusion keywords for pages to skip
        self.exclusion_keywords = [
            "login", "sign in", "sign_in", "signin", "sign-in",
            "privacy policy", "terms", "terms of service", "terms-of-service",
            "careers", "jobs", "employment",
            "support", "help", "faq", "documentation", "customer service",
            "contact us", "contactus", "contact-us", "blog", "newsletter",
            "what's new"
        ]

    # Fetches a web page and returns a BeautifulSoup object.
    def get_soup(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while fetching {url}: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred while fetching {url}: {req_err}")
        except Exception as e:
            print(f"An error occurred while fetching {url}: {e}")

    # Extracts internal links from the given BeautifulSoup object.
    def get_internal_links(self, soup):
        links = set()
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True).lower()
            href = link["href"]
            full_url = self.get_full_url(href)
            combined_text = text + " " + full_url
            if any(keyword in combined_text for keyword in self.exclusion_keywords):
                continue
            if any(keyword in text for keyword in self.keywords):
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
        try:
            soup = self.get_soup(url)
            if soup is None:
                print(f"Skipping {url} due to an error.")
                return None  # Skip processing if the page couldn't be fetched
            content = [p.get_text(strip=True) for p in soup.find_all("p")]
            links = self.get_internal_links(soup)
            return "\n".join(content), links
        except Exception as e:
            print(f"Error processing {url}: {e}")

    # Recursively crawl website up to maximum depth
    def crawl(self, url, depth=0, max_depth=2):
        try:
            if depth > max_depth or url in self.visited_urls:
                return
            print(f"Crawling: {url} at depth {depth}")
            self.visited_urls.add(url)
            content, links = self.extract_main_content(url)
            # Process content as needed
            for link in links:
                self.crawl(link, depth + 1, max_depth)
        except Exception as e:
            print(f"Error processing {url}: {e}")


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
