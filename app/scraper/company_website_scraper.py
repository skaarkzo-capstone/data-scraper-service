import os
import sys

import requests
from bs4 import BeautifulSoup

from app.scraper.pdf_scraper import PDFScraper
from app.service.website_identifier_service import get_company_website
import app.util.website_keywords as wk

"""
This script defines a web scraping tool to extract structured data and PDF documents 
from a company's website. The tool is designed to locate specific sections like "About", 
"Sustainability", "Reports", and "Products" by leveraging predefined keywords. 

It also processes linked PDF files, handles navigation bar links, and excludes irrelevant pages 
based on exclusion keywords. The extracted data is stored in a JSON for further use.

The script can be executed from the command line with the company's name as an argument, 
fetching the company's website URL from a predefined CSV file before scraping.
"""


class CompanyWebsiteScraper:
    def __init__(self, base_url, extract_pdfs=True, pdf_directory='downloaded_pdfs'):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.explored_urls = set()  # Tracks URLs already visited to avoid redundancy
        self.pdf_checked_urls = set()  # Tracks URLs already checked for PDFs
        self.extract_pdfs = extract_pdfs
        self.pdf_directory = pdf_directory
        self.pdf_processor = PDFScraper(pdf_directory=self.pdf_directory, headers=self.headers)
        self.data = {}  # Data structure to hold the scraped content

        # Create directory for PDFs if it doesn't exist
        if self.extract_pdfs and not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)

        # Keywords to identify sections of interest on the website
        self.keywords = wk.keywords

        # Keywords to exclude certain pages (e.g., login, careers, etc.)
        self.exclusion_keywords = wk.exclusion_keywords

    def scrape(self):
        """
        Main method to scrape predefined sections of the website.
        Iterates through sections like 'about', 'sustainability', etc., and fetches relevant content.
        """
        for section, keywords in self.keywords.items():
            print(f"Scraping section: {section}")
            # Get all links relevant to the section
            section_links = self.get_relevant_links(self.base_url, keywords)

            # For the 'products' section, include navbar links as they often contain product information
            if section == 'products':
                navbar_links = self.get_navbar_links(self.base_url, keywords)
                section_links.update(navbar_links)

            for name, url in section_links.items():
                # Set maximum depth for recursive exploration based on the section
                max_depth = 2 if section not in ['reports', 'products'] else 1
                content = self.explore_and_scrape(url, keywords, current_depth=0, max_depth=max_depth)
                # Add the scraped content to the data structure
                if content:
                    self.data.setdefault(section, {})[name] = content

    def get_relevant_links(self, url, keywords):
        """
        Fetches links from a page that match the provided keywords.
        Ensures the links are relevant and not excluded based on exclusion rules.
        """
        relevant_links = {}
        try:
            soup = self.get_soup(url)
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True).lower()  # Extract link text and normalize to lowercase
                href = link["href"]  # Extract the hyperlink reference
                if any(keyword in text for keyword in keywords):  # Check if any keyword matches
                    full_url = self.get_full_url(href)  # Convert to absolute URL
                    if not self.is_excluded_link(text, full_url):  # Exclude irrelevant links
                        relevant_links[text] = full_url
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return relevant_links

    def get_navbar_links(self, url, keywords):
        """
        Specifically fetches links from the website's navigation bar.
        Often useful for finding 'products' or other major sections.
        """
        navbar_links = {}
        try:
            soup = self.get_soup(url)
            nav = soup.find('nav')  # Locate the navigation element
            if nav:
                for link in nav.find_all("a", href=True):
                    text = link.get_text(strip=True)  # Extract visible link text
                    text_lower = text.lower()
                    href = link["href"]
                    full_url = self.get_full_url(href)  # Convert to absolute URL
                    if any(keyword in text_lower for keyword in keywords):  # Check if keywords match
                        if not self.is_excluded_link(text_lower, full_url):  # Exclude irrelevant links
                            navbar_links[text] = full_url
            else:
                print("Navigation menu not found.")
        except Exception as e:
            print(f"Error fetching navbar links from {url}: {e}")
        return navbar_links

    def is_excluded_link(self, text, url):
        """
        Determines if a link should be excluded based on exclusion keywords.
        Combines link text and URL for comprehensive checking.
        """
        combined_text = text + " " + url
        for keyword in self.exclusion_keywords:
            if keyword in combined_text.lower():
                return True
        return False

    def get_full_url(self, href):
        """
        Converts relative URLs to absolute URLs.
        """
        if href.startswith("http"):
            return href
        else:
            return f"{self.base_url}/{href.lstrip('/')}"

    def get_soup(self, url):
        """
        Fetches and parses the HTML content of a page using BeautifulSoup.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def explore_and_scrape(self, url, keywords, current_depth=0, max_depth=2):
        """
        Recursively explores a webpage to extract content, PDFs, and nested links.
        """
        if url in self.explored_urls or current_depth > max_depth:
            return None  # Stop recursion if the URL is already visited or max depth is reached
        print(f"Exploring: {url}")
        self.explored_urls.add(url)  # Mark the URL as visited
        page_data = {
            "url": url,
            "content": "",  # Main textual content of the page
            "pdfs": [],  # List of PDF metadata (e.g., URL, extracted content)
            "links": {}  # Nested links and their content
        }
        soup = self.get_soup(url)
        if soup is None:
            return None

        try:
            # Extract main text content
            content = [p.get_text(strip=True) for p in soup.find_all("p")]
            page_data["content"] = "\n".join(content)

            # Identify and process PDFs linked on the page
            pdf_links = self.find_pdfs_on_page(soup, url, keywords)
            for pdf_url in pdf_links:
                pdf_info = self.process_pdf(pdf_url)
                if pdf_info:
                    page_data["pdfs"].append(pdf_info)

            # Recursively explore nested links within the current page
            if current_depth < max_depth:
                for link in soup.find_all("a", href=True):
                    text = link.get_text(strip=True)
                    href = link["href"]
                    full_url = self.get_full_url(href)
                    text_lower = text.lower()

                    # Check for relevance and process further if valid
                    if (full_url not in self.explored_urls and
                            not self.is_excluded_link(text_lower, full_url) and
                            any(keyword in text_lower for keyword in keywords)):
                        nested_content = self.explore_and_scrape(
                            full_url, keywords, current_depth + 1, max_depth)
                        if nested_content:
                            page_data["links"][text] = nested_content
        except Exception as e:
            print(f"Error processing {url}: {e}")
        return page_data

    def find_pdfs_on_page(self, soup, page_url, keywords):
        """
        Identifies PDF links on a webpage, either by extension or content type.
        """
        pdf_urls = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True).lower()
            full_url = self.get_full_url(href)
            if full_url in self.pdf_checked_urls:  # Skip already checked URLs
                continue
            self.pdf_checked_urls.add(full_url)  # Mark the URL as checked
            if self.is_excluded_link(text, full_url):  # Exclude irrelevant links
                continue

            is_pdf = False
            # Check if the link explicitly points to a PDF
            if href.lower().endswith(".pdf"):
                is_pdf = True
            else:
                # Check the link's metadata for PDF content type
                if 'pdf' in text or 'download' in text or any(kw in text for kw in self.keywords.get('reports', [])):
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
        """
        return self.pdf_processor.process_pdf(pdf_url, extract_pdfs=self.extract_pdfs)

    def make_safe_filename(self, filename):
        """
        Ensures a filename is safe for file systems by replacing invalid characters.
        """
        return self.pdf_processor.make_safe_filename(filename)

    def save_to_json(self, output_file):
        """
        Saves the collected data to a JSON file.
        """
        self.pdf_processor.save_to_json(self.data, output_file)


if __name__ == "__main__":
    company_name = sys.argv[1]  # Get company name from command line arguments
    csv_file_path = "app/scraper/filtered_companies_canada.csv"  # Path to the CSV file with company details

    # Fetch the company's website URL
    company_url = "https://" + get_company_website(company_name, csv_file_path)
    if company_url:
        print(f"Found website: {company_url}")

    scraper = CompanyWebsiteScraper(company_url)
    scraper.scrape()

    # Save the scraped data to a JSON file
    output_file = f"{company_name.replace(' ', '_')}_scraped_data.json"
    scraper.save_to_json(output_file)
