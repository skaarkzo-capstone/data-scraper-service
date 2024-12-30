import os
import sys
import requests

from bs4 import BeautifulSoup
from app.scraper.pdf_scraper import PDFScraper
from app.service.website_identifier_service import get_company_website
import app.util.website_keywords as wk


class CompanyWebsiteScraper:
    """
    A web scraping tool for extracting structured data and PDF documents from a company's website.

    It scans specific sections identified by keywords (e.g., 'about', 'sustainability', 'reports', 'products'),
    processes linked PDF files, handles navigation bar links, and excludes irrelevant pages based on
    exclusion keywords. The extracted data is stored in a JSON for further use.
    """

    def __init__(self, base_url, extract_pdfs=True, pdf_directory='downloaded_pdfs'):
        """
        Initialize the scraper with:
          - base_url: the website's base URL
          - extract_pdfs: whether to download and process PDFs
          - pdf_directory: directory to store downloaded PDFs
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.explored_urls = set()  # Track URLs already visited to avoid redundancy
        self.pdf_checked_urls = set()  # Track URLs already checked for PDFs
        self.extract_pdfs = extract_pdfs
        self.pdf_directory = pdf_directory
        self.pdf_processor = PDFScraper(pdf_directory=self.pdf_directory, headers=self.headers)
        self.data = {}  # Data structure to hold the scraped content

        if self.extract_pdfs and not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)

        self.keywords = wk.keywords  # Keywords to identify sections of interest
        self.exclusion_keywords = wk.exclusion_keywords  # Keywords to exclude certain pages

    def scrape(self):
        """
        Main entry point to scrape predefined sections of the website (e.g., 'about', 'sustainability', 'reports', 'products').
        For each section, fetch relevant links (and navbar links for 'products'), and recursively scrape their content.
        """
        for section, keywords in self.keywords.items():
            print(f"Scraping section: {section}")
            section_links = self.get_relevant_links(self.base_url, keywords)

            # For the 'products' section, also include navbar links
            if section == 'products':
                navbar_links = self.get_navbar_links(self.base_url, keywords)
                section_links.update(navbar_links)

            # Adjust recursion depth based on the section
            max_depth = 2 if section not in ['reports', 'products'] else 1

            for link_text, url in section_links.items():
                content = self.explore_and_scrape(url, keywords, current_depth=0, max_depth=max_depth)
                if content:
                    self.data.setdefault(section, {})[link_text] = content

    def get_relevant_links(self, url, keywords):
        """
        Fetch links from a page that match specific keywords, excluding irrelevant or duplicate links.
        Returns a dict of { link_text: full_url }.
        """
        relevant_links = {}
        soup = self.get_soup(url)
        if soup:
            for link in soup.find_all("a", href=True):
                text_lower = link.get_text(strip=True).lower()
                href = link["href"]
                if any(keyword in text_lower for keyword in keywords):
                    full_url = self.get_full_url(href)
                    if not self.is_excluded_link(text_lower, full_url):
                        relevant_links[text_lower] = full_url
        return relevant_links

    def get_navbar_links(self, url, keywords):
        """
        Specifically fetch links from the website's navigation bar (if present).
        Useful for finding product-related pages.
        Returns a dict of { link_text: full_url }.
        """
        navbar_links = {}
        soup = self.get_soup(url)
        if soup:
            nav = soup.find('nav')
            if nav:
                for link in nav.find_all("a", href=True):
                    text = link.get_text(strip=True)
                    text_lower = text.lower()
                    href = link["href"]
                    full_url = self.get_full_url(href)
                    if any(keyword in text_lower for keyword in keywords):
                        if not self.is_excluded_link(text_lower, full_url):
                            navbar_links[text_lower] = full_url
            else:
                print("Navigation menu not found.")
        return navbar_links

    def explore_and_scrape(self, url, keywords, current_depth=0, max_depth=2):
        """
        Recursively explore a webpage to extract textual content, PDFs, and nested links,
        stopping if the URL has been visited or the max depth is reached.
        Returns a dictionary with page data (url, content, pdfs, links).
        """
        if url in self.explored_urls or current_depth > max_depth:
            return None

        print(f"Exploring: {url}")
        self.explored_urls.add(url)

        page_data = {
            "url": url,
            "content": "",
            "pdfs": [],
            "links": {}
        }

        soup = self.get_soup(url)
        if not soup:
            return None

        # Extract main text content
        page_data["content"] = self.extract_page_text(soup)

        # Identify and process PDFs linked on the page
        page_pdf_links = self.find_pdfs_on_page(soup, url, keywords)
        for pdf_url in page_pdf_links:
            pdf_info = self.process_pdf(pdf_url)
            if pdf_info:
                page_data["pdfs"].append(pdf_info)

        # Recursively explore nested links
        if current_depth < max_depth:
            self.explore_nested_links(soup, keywords, current_depth, max_depth, page_data)

        return page_data

    def explore_nested_links(self, soup, keywords, current_depth, max_depth, page_data):
        """
        Recursively explore and scrape links within a BeautifulSoup object,
        adding found link data to the page_data 'links' section.
        """
        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            link_text_lower = link_text.lower()
            full_url = self.get_full_url(link["href"])

            if full_url not in self.explored_urls \
                    and not self.is_excluded_link(link_text_lower, full_url) \
                    and any(keyword in link_text_lower for keyword in keywords):

                nested_content = self.explore_and_scrape(full_url, keywords, current_depth + 1, max_depth)
                if nested_content:
                    page_data["links"][link_text] = nested_content

    def extract_page_text(self, soup):
        """
        Extracts and returns concatenated text content from all <p> tags in the soup.
        """
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(paragraphs)

    def find_pdfs_on_page(self, soup, page_url, keywords):
        """
        Identify PDF links on a webpage (either by .pdf extension or by content type check).
        Returns a list of PDF URLs.
        """
        pdf_urls = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text_lower = link.get_text(strip=True).lower()
            full_url = self.get_full_url(href)

            # Skip if we've already checked this URL for PDFs
            if full_url in self.pdf_checked_urls:
                continue
            self.pdf_checked_urls.add(full_url)

            # Exclude link if it contains exclusion keywords
            if self.is_excluded_link(text_lower, full_url):
                continue

            is_pdf = False
            # Check file extension
            if href.lower().endswith(".pdf"):
                is_pdf = True
            else:
                # Check text or content type
                if 'pdf' in text_lower or 'download' in text_lower \
                        or any(kw in text_lower for kw in self.keywords.get('reports', [])):
                    try:
                        head = requests.head(full_url, headers=self.headers, allow_redirects=True, timeout=10)
                        content_type = head.headers.get('Content-Type', '').lower()
                        if 'pdf' in content_type:
                            is_pdf = True
                    except Exception as e:
                        print(f"Error checking {full_url}: {e}")
                        continue

            if is_pdf:
                pdf_urls.append(full_url)

        return pdf_urls

    def process_pdf(self, pdf_url):
        """
        Downloads and processes a PDF using the PDFScraper class.
        Returns the extracted PDF data (if any).
        """
        return self.pdf_processor.process_pdf(pdf_url, extract_pdfs=self.extract_pdfs)

    def is_excluded_link(self, text, url):
        """
        Determine if a link should be excluded based on exclusion keywords.
        Combines link text and URL for comprehensive checking.
        """
        combined_text = f"{text} {url}"
        for keyword in self.exclusion_keywords:
            if keyword in combined_text.lower():
                return True
        return False

    def get_full_url(self, href):
        """
        Convert a relative URL to an absolute URL by prefixing the base URL when needed.
        """
        if href.startswith("http"):
            return href
        return f"{self.base_url}/{href.lstrip('/')}"

    def get_soup(self, url):
        """
        Fetch and parse the HTML content of a page using BeautifulSoup.
        Returns a BeautifulSoup object or None if the request fails.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def save_to_json(self, output_file):
        """
        Save the collected data structure to a JSON file.
        """
        self.pdf_processor.save_to_json(self.data, output_file)

    def make_safe_filename(self, filename):
        """
        Ensure a filename is safe for file systems by replacing invalid characters.
        """
        return self.pdf_processor.make_safe_filename(filename)


if __name__ == "__main__":
    # Capture the company name from the command line
    company_name = sys.argv[1]
    csv_file_path = "app/scraper/filtered_companies_canada.csv"

    # Fetch the company's website URL
    company_url = "https://" + get_company_website(company_name, csv_file_path)
    if company_url:
        print(f"Found website: {company_url}")

    scraper = CompanyWebsiteScraper(company_url)
    scraper.scrape()

    output_file = f"{company_name.replace(' ', '_')}_scraped_data.json"
    scraper.save_to_json(output_file)
