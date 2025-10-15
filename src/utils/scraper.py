# src/utils/scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Optional

def scrape_text_from_url(url: str) -> Optional[str]:
    """
    Fetches and extracts clean, relevant text content from a given URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
            
        return soup.get_text(separator=' ', strip=True)
    
    except requests.RequestException as e:
        print(f"Error: Could not retrieve or parse URL {url}. Details: {e}")
        return None