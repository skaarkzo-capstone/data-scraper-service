from app.service.website_identifier_service import get_company_website
from app.scraper.pdf_scraper import PDFScraper
import requests
from bs4 import BeautifulSoup
import os
import sys

class CompanyWebsiteScraper:
    def __init__(self, base_url, extract_pdfs=True, pdf_directory='downloaded_pdfs'):
        self.base_url = base_url.rstrip('/')
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.explored_urls = set() # Keep track of urls that have been visited/explored
        self.pdf_checked_urls = set()  # Keep track of URLs checked for PDFs on a certain page
        self.extract_pdfs = extract_pdfs
        self.pdf_directory = pdf_directory
        self.pdf_processor = PDFScraper(pdf_directory=self.pdf_directory, headers=self.headers)
        self.data = {}  # Initialize data dictionary

        # Create directory for PDFs if it doesn't exist
        if self.extract_pdfs and not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)

        # Define keywords for different sections
        self.keywords = {
            'about': ["about", "our story", "company", "about us"],
            'sustainability': ["sustainability", "csr", "environment", "climate"],
            'reports': ["annual report", "sustainability report", "investor relations", "financial report", "pdf", "download"],
            'products': ["product", "products", "services", "offerings", "solutions", "features"]
        }

        # Exclusion keywords for pages to skip
        self.exclusion_keywords = [
            "login", "sign in", "sign_in", "signin", "sign-in",
            "privacy policy", "terms", "terms of service", "terms-of-service",
            "careers", "jobs", "employment",
            "support", "help", "faq", "documentation", "customer service",
            "contact us", "contactus", "contact-us", "blog", "newsletter",
            "what's new"
        ]

    def scrape(self):
        # Scrape predefined sections
        for section, keywords in self.keywords.items():
            print(f"Scraping section: {section}")
            section_links = self.get_relevant_links(self.base_url, keywords)

            # Include navbar links for 'products'
            if section == 'products':
                navbar_links = self.get_navbar_links(self.base_url, keywords)
                section_links.update(navbar_links)

            for name, url in section_links.items():
                # Set max_depth based on section
                max_depth = 2 if section not in ['reports', 'products'] else 1
                content = self.explore_and_scrape(url, keywords, current_depth=0, max_depth=max_depth)
                # Add content to data dictionary
                if content:
                    self.data.setdefault(section, {})[name] = content

    # Function to get links on each page, allows us to crawl entire site
    def get_relevant_links(self, url, keywords):
        relevant_links = {}
        try:
            soup = self.get_soup(url)
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True).lower()
                href = link["href"]
                if any(keyword in text for keyword in keywords):
                    full_url = self.get_full_url(href)
                    if not self.is_excluded_link(text, full_url):
                        relevant_links[text] = full_url
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return relevant_links

    # Mainly used to get products, often they are listed as solution, offerings, etc. So grabs these links from navbar
    def get_navbar_links(self, url, keywords):
        navbar_links = {}
        try:
            soup = self.get_soup(url)
            nav = soup.find('nav')
            if nav:
                for link in nav.find_all("a", href=True):
                    text = link.get_text(strip=True)
                    text_lower = text.lower()
                    href = link["href"]
                    full_url = self.get_full_url(href)
                    if any(keyword in text_lower for keyword in keywords):
                        if not self.is_excluded_link(text_lower, full_url):
                            navbar_links[text] = full_url
            else:
                print("Navigation menu not found.")
        except Exception as e:
            print(f"Error fetching navbar links from {url}: {e}")
        return navbar_links

    # Makes sure not to pick up links we want to exclude
    def is_excluded_link(self, text, url):
        combined_text = text + " " + url
        for keyword in self.exclusion_keywords:
            if keyword in combined_text.lower():
                return True
        return False

    def get_full_url(self, href):
        if href.startswith("http"):
            return href
        else:
            return f"{self.base_url}/{href.lstrip('/')}"

    def get_soup(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    # Recursively explore and scrape the website
    def explore_and_scrape(self, url, keywords, current_depth=0, max_depth=2):
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
        if soup is None:
            return None

        try:
            # Extract main content
            content = [p.get_text(strip=True) for p in soup.find_all("p")]
            page_data["content"] = "\n".join(content)

            # Find PDFs on the page
            pdf_links = self.find_pdfs_on_page(soup, url, keywords)
            for pdf_url in pdf_links:
                pdf_info = self.process_pdf(pdf_url)
                if pdf_info:
                    page_data["pdfs"].append(pdf_info)

            # Find nested links
            if current_depth < max_depth:
                for link in soup.find_all("a", href=True):
                    text = link.get_text(strip=True)
                    href = link["href"]
                    full_url = self.get_full_url(href)
                    text_lower = text.lower()

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

    # As the function name suggests
    def find_pdfs_on_page(self, soup, page_url, keywords):
        pdf_urls = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True).lower()
            full_url = self.get_full_url(href)
            if full_url in self.pdf_checked_urls:
                continue
            self.pdf_checked_urls.add(full_url)
            if self.is_excluded_link(text, full_url):
                continue

            is_pdf = False
            # Check if the link ends with .pdf
            if href.lower().endswith(".pdf"):
                is_pdf = True
            else:
                # Check the content type
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
        return self.pdf_processor.process_pdf(pdf_url, extract_pdfs=self.extract_pdfs)
        
    def make_safe_filename(self, filename):
        return self.pdf_processor.make_safe_filename(filename)
    
    def save_to_json(self, output_file):
        self.pdf_processor.save_to_json(self.data, output_file)

if __name__ == "__main__":
    company_name = sys.argv[1]
    csv_file_path = "app/scraper/filtered_companies_canada.csv"  # Path to your CSV file

    # Get the company's website
    company_url = "https://" + get_company_website(company_name, csv_file_path)
    if company_url:
        print(f"Found website: {company_url}")

    scraper = CompanyWebsiteScraper(company_url)
    scraper.scrape()

    # Save the scraped data to a JSON file
    output_file = f"{company_name.replace(' ', '_')}_scraped_data.json"
    scraper.save_to_json(output_file)
