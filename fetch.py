#!/usr/bin/env python3

import sys
import os
import requests
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup

STORAGE_DIR = os.path.join(sys.path[0], 'pages')

# Fetches the page from the given url:
def fetch_url(url):
    try:
        ### 1. Let's fetch the page's HTML ###

        response = requests.get(url)
        response.raise_for_status()

        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the number of links and images
        links_num = len(soup.find_all('a'))
        images_num = len(soup.find_all('img'))

        ### 2. Save the file to the disk ###

        # Extract the domain name to name the file
        domain_name = urlparse(url).netloc
        filename = f"{domain_name}.html"
        save_path = os.path.join(STORAGE_DIR, filename)

        # Save the content
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(response.text)

        # Log to the console
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Fetched {url} at {current_time}")
        print(f"  - Saved as {filename}")
        print(f"  - Links found on the page: {links_num}")
        print(f"  - Images found on the page: {images_num}")

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")


def main():
    if len(sys.argv) < 2:
        print("For usage please type: fetch.py url1 url2 ...")
        sys.exit(1)

    for url in sys.argv[1:]:
        fetch_url(url)


if __name__ == "__main__":
    main()
