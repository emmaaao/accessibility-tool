from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.semantic_validator import enrich_elements
from axe_selenium_python import Axe
from bs4 import BeautifulSoup
from src.ai_analyzer import AIAnalyzer
from src.semantic_validator import (
    analyze_readability,
    analyze_alt_text,
    analyze_links,
)
import time

""" Initialize the scraper
         Args:
             url (str): Website URL to analyze
             headless (bool): Run browser in background
"""


class AccessibilityScraper:
    def __init__(self, url, headless=True, use_ai=False):
        self.url = url
        self.use_ai = use_ai
        self.ai_analyzer = AIAnalyzer() if use_ai else None

        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        # Initialize Chrome driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)

    # Gets both Axe results and elements for AI
    # Returns:  dict: Contains 'axe_results' and 'elements_for_ai'
    def extract_data(self):
        try:
            print(f" Loading {self.url}...")
            self.driver.get(self.url)

            # Wait for page to load
            time.sleep(2)

            # Run Axe-core for technical analysis
            print(" Running Axe-core analysis...")
            axe = Axe(self.driver)
            axe.inject()
            axe_results = axe.run()

            # Get HTML for context extraction
            print("Extracting page elements...")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            # Extract elements with context for AI analysis
            raw_elements = {
                'links': self._extract_links(soup),
                'images': self._extract_images(soup),
                'text_blocks': self._extract_text_blocks(soup)
            }

            semantic_elements = enrich_elements(raw_elements)

            elements_for_ai = {
                **semantic_elements,
                'page_title': soup.find('title').get_text() if soup.find('title') else '',
                'main_heading': soup.find('h1').get_text() if soup.find('h1') else ''
            }

            print(f" Extraction complete!")
            print(f"   - Found {len(elements_for_ai['links'])} links")
            print(f"   - Found {len(elements_for_ai['images'])} images")
            print(f"   - Found {len(elements_for_ai['text_blocks'])} text blocks")
            print(f"   - Axe found {len(axe_results.get('violations', []))} violations")

            week2 = {
                "readability": [],
                "images": [],
                "links": []
            }

            ai_results = None

            if self.use_ai and self.ai_analyzer:
                print(" Running AI semantic analysis...")
                ai_results = self.ai_analyzer.analyze(raw_elements)

            # Analyze text readability
            for block in semantic_elements["text_blocks"]:
                readability = analyze_readability(block["text"])
                week2["readability"].append(readability)

            # Analyze images
            for image in semantic_elements["images"]:
                result = analyze_alt_text(image)
                if result["issue"]:
                    week2["images"].append(result)

            # Analyze links
            for link in semantic_elements["links"]:
                result = analyze_links(link)
                if result["issue"]:
                    week2["links"].append(result)

            return {
                'url': self.url,
                'axe_results': axe_results,
                'raw_elements': raw_elements,
                'semantic_elements': semantic_elements,
                "week2": week2,
                'ai_results': ai_results
            }

        except Exception as e:
            print(f" Error during extraction: {e}")
            raise
        finally:
            self.driver.quit()

        # Extract all links with context

    def _extract_links(self, soup):
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)

            # Skip empty links or navigation symbols
            if not link_text or link_text in ['', '«', '»', '<', '>']:
                continue

            context = self._get_context(link)
            links.append({
                'text': link_text,
                'href': link.get('href', ''),
                'context': context,
                'aria_label': link.get('aria-label'),
                'title': link.get('title'),
                'role': link.get('role')
            })
        return links

        # Extract all images with context

    def _extract_images(self, soup):
        images = []
        for img in soup.find_all('img'):
            context = self._get_context(img)

            # Get image description from various sources
            alt_text = img.get('alt', '')
            aria_label = img.get('aria-label', '')
            title = img.get('title', '')

            images.append({
                'src': img.get('src', ''),
                'alt': alt_text,
                'aria_label': aria_label,
                'title': title,
                'context': context,
                'role': img.get('role', ''),
                'is_decorative': img.get('role') == 'presentation' or img.get('alt') == ''
            })
        return images

    # Extract text blocks for readability analysis
    def _extract_text_blocks(self, soup):
        text_blocks = []

        # Get main content paragraphs
        main_content = soup.find('main') or soup.find('article') or soup.find('body')

        if main_content:
            for paragraph in main_content.find_all('p'):
                text = paragraph.get_text(strip=True)

                # Only include substantial paragraphs
                if len(text.split()) > 15:
                    heading_context = self._get_heading_context(paragraph)
                    text_blocks.append({
                        'text': text,
                        'heading_context': heading_context,
                        'word_count': len(text.split())
                    })
        return text_blocks

    # Get surrounding context for an element
    def _get_context(self, element):
        context = []

        # Find nearest heading
        parent = element.find_parent(['section', 'article', 'div', 'main'])
        if parent:
            # Look for headings in order of preference
            heading = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if heading:
                context.append(f"Section: {heading.get_text(strip=True)}")

        # Get parent paragraph text
        p_parent = element.find_parent('p')
        if p_parent:
            para_text = p_parent.get_text(strip=True)
            # Limit to 200 chars to avoid token overflow
            if len(para_text) > 200:
                para_text = para_text[:200] + "..."
            context.append(f"Paragraph: {para_text}")

        # Get surrounding text
        if not p_parent:
            prev_text = element.find_previous(string=True)
            if prev_text:
                prev_clean = prev_text.strip()
                if prev_clean and len(prev_clean) > 5:
                    context.append(f"Near: {prev_clean[:100]}")

        return ' | '.join(context) if context else 'No context available'

    # Get the heading that applies to this element
    def _get_heading_context(self, element):
        # Find nearest preceding heading
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading = element.find_previous(heading_tag)
            if heading:
                return heading.get_text(strip=True)
        return ''
