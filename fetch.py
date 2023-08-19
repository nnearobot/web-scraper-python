#!/usr/bin/env python3

import sys
import os
import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

STORAGE_DIR = os.path.join(sys.path[0], 'pages')


### Saves the assets near the html file: ###

def save_asset(url, save_path):
    try:
        response = make_request(url, True)
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(8192):
                file.write(chunk)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")


### Fetches the page from the given url: ###

def fetch_url(url):
    try:
        ### 1. Let's fetch the page's HTML ###
        response = make_request(url)

        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the number of links, images and scripts
        links_num = len(soup.find_all('a'))
        images_num = len(soup.find_all('img'))
        script_num = len(soup.find_all('script'))


        ### 2. Save all the assets to the local disk ###

        # Create a directory to save assets
        domain_name = urlparse(url).netloc
        assets_dir = os.path.join(STORAGE_DIR, domain_name)
        os.makedirs(assets_dir, exist_ok=True)

        # List of tags and attributes to search for URLs to download
        assets_tags = {
            "img": ["src"],
            "script": ["src"],
            "link": ["href", "stylesheet"]
        }
        asset_count = 0
        for tag, attr_list in assets_tags.items():
            rel = attr_list[1] if len(attr_list) > 1 else None
            for element in soup.find_all(tag, rel=rel):
                asset_url = element.attrs.get(attr_list[0], "")
                if asset_url:
                    absolute_asset_url = urljoin(url, asset_url)
                    asset_name = os.path.basename(urlparse(asset_url).path)
                    # there are some links not to files but to the APIs like  https://js.stripe.com/v2/
                    # we leave them as is because there no particular file
                    if asset_name:
                        # some different assets on the page may have the same name (the may locate in the different directories)
                        # so for not rewriting the files we make a new asset_name by adding an asset_count to the file name:
                        splitted_filename = os.path.splitext(asset_name)
                        asset_name = "{}_{}{}".format(splitted_filename[0], asset_count, splitted_filename[1])
                        asset_count += 1

                        local_asset_path = os.path.join(assets_dir, asset_name)
                        print(tag, asset_name, asset_url, local_asset_path)

                        save_asset(absolute_asset_url, local_asset_path)

                        # Update the attribute in the html to point to the local asset
                        element[attr_list[0]] = os.path.join(domain_name, asset_name)


        ### 3. Save the modified HTML content to the disk ###
        filename = f"{domain_name}.html"
        html_filename = os.path.join(STORAGE_DIR, filename)
        with open(html_filename, 'w', encoding='utf-8') as file:
            file.write(str(soup))


        # Log to the console
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Fetched {url} at {current_time}")
        print(f"  - Saved as {filename}")
        print(f"  - Links found on the page: {links_num}")
        print(f"  - Images found on the page: {images_num}")
        print(f"  - Scripts found on the page: {script_num}")

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")


def make_request(url: str, stream: bool=False):
    response = requests.get(url, stream=stream, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    })
    response.raise_for_status()
    return response


def main():
    if len(sys.argv) < 2:
        print("For usage please type: fetch.py url1 url2 ...")
        sys.exit(1)

    for url in sys.argv[1:]:
        fetch_url(url)


if __name__ == "__main__":
    main()
