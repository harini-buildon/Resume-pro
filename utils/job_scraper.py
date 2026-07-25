"""
utils/job_scraper.py – Target Job Description URL Scraper & Extractor
========================================================================
Scrapes and extracts clean job description text from job posting URLs
(LinkedIn, Indeed, Glassdoor, or company career pages).
"""

import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser


class SimpleTextHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.ignore_tags = {'script', 'style', 'head', 'title', 'meta', 'nav', 'header', 'footer'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            cleaned = data.strip()
            if cleaned and len(cleaned) > 2:
                self.text_chunks.append(cleaned)


def extract_job_from_url(job_url):
    """
    Fetch and extract clean job description text from a job posting URL.

    Parameters:
        job_url (str): Target web URL

    Returns:
        dict: {
            'status': 'success' | 'error',
            'extracted_text': str,
            'job_url': str,
            'error_message': str or None
        }
    """
    if not job_url or not (job_url.startswith("http://") or job_url.startswith("https://")):
        return {
            'status': 'error',
            'extracted_text': "",
            'job_url': job_url,
            'error_message': "Invalid URL format. URL must start with http:// or https://"
        }

    try:
        req = urllib.request.Request(
            job_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8', errors='ignore')

        parser = SimpleTextHTMLParser()
        parser.feed(html_content)
        raw_text = " ".join(parser.text_chunks)

        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()

        if len(clean_text) < 50:
            return {
                'status': 'error',
                'extracted_text': "",
                'job_url': job_url,
                'error_message': "Could not extract sufficient text from URL. Please paste text manually."
            }

        return {
            'status': 'success',
            'extracted_text': clean_text[:4000],  # Truncate to reasonable max length
            'job_url': job_url,
            'error_message': None
        }

    except Exception as e:
        return {
            'status': 'error',
            'extracted_text': "",
            'job_url': job_url,
            'error_message': f"Failed to fetch job URL: {str(e)}"
        }
