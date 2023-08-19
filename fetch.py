#!/usr/bin/env python3

import sys
import os
import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class Fetcher:
    ASSETS_TAGS = {
        "img": "src",
        "script": "src",
        "link": "href"
    }

    def __init__(self, url, save_dir=None):
        self.url = url

        # for testing purposes we let to define a directory to save a page:
        self.save_dir = save_dir if save_dir else os.path.join(sys.path[0], 'pages')

        self.domain_name = urlparse(url).netloc
        self.filename = f"{self.domain_name}.html"
        self.links_num = 0
        self.images_num = 0
        self.script_num = 0
        

    ### Saves the assets near the html file: ###
    def save_asset(self, url, save_path):
        try:
            response = self.make_request(url, True)
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(8192):
                    file.write(chunk)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except TypeError as e:
            print(f"Error writing to a file {url}: {e}")
            with open(save_path, 'wt') as file:
                file.write('')


    ### Fetches the page from the given url: ###
    def fetch(self):
        try:
            ### 1. Let's fetch the page's HTML ###
            response = self.make_request(self.url)

            # Parse the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')

            # Get the number of links, images and scripts
            self.links_num = len(soup.find_all('a'))
            self.images_num = len(soup.find_all('img'))
            self.script_num = len(soup.find_all('script'))

            ### 2. Save all the assets to the local disk ###
            # Create a directory to save assets
            assets_dir = os.path.join(self.save_dir, self.domain_name)
            os.makedirs(assets_dir, exist_ok=True)

            # List of tags and attributes to search for URLs to download
            asset_count = 0
            for tag, attr in self.ASSETS_TAGS.items():
                for element in soup.find_all(tag):

                    # get a url of the asset:
                    asset_url = element.attrs.get(attr, "")
                    if not asset_url:
                        continue

                    absolute_asset_url = urljoin(self.url, asset_url)
                    asset_name = os.path.basename(urlparse(asset_url).path)

                    # there are some links not to files but to the APIs like  https://js.stripe.com/v2/
                    # we leave them as is because there no particular file
                    if not asset_name:
                        continue
                    
                    # also if the asset doesn't have a file extension, it is probably not an asset
                    splitted_filename = os.path.splitext(asset_name)
                    if len(splitted_filename) < 2 or not splitted_filename[1]:
                        continue

                    # some different assets on the page may have the same file name (they may locate in a different directories)
                    # for preventing a rewriting the files we make a new asset_name by adding an asset_count to the file name:
                    asset_name = "{}_{}{}".format(splitted_filename[0], asset_count, splitted_filename[1])
                    asset_count += 1

                    local_asset_path = os.path.join(assets_dir, asset_name)
                    self.save_asset(absolute_asset_url, local_asset_path)

                    # Update the attribute in the html to point to the local asset
                    element[attr] = os.path.join(self.domain_name, asset_name)

                    print(tag, asset_name, splitted_filename, asset_url, local_asset_path)


            ### 3. Save the modified HTML content to the disk ###
            html_filename = os.path.join(self.save_dir, self.filename)
            with open(html_filename, 'w', encoding='utf-8') as file:
                file.write(str(soup))

        except requests.RequestException as e:
            print(f"Error fetching {self.url}: {e}")


    def get_metadata(self):
        return {
            'filename': self.filename,
            'links_num': self.links_num,
            'images_num': self.images_num,
            'script_num': self.script_num
        }
    
    def print_logs(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Fetched {self.url} at {current_time}")
        print(f"  - Saved as {self.filename}")
        print(f"  - Links found on the page: {self.links_num}")
        print(f"  - Images found on the page: {self.images_num}")
        print(f"  - Scripts found on the page: {self.script_num}")


    def make_request(self, url: str, stream: bool=False):
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
        print(f"Fetching {url}...")
        fetcher = Fetcher(url)
        fetcher.fetch()
        fetcher.print_logs()
    
    print("\nDONE\n") 


if __name__ == "__main__":
    main()
