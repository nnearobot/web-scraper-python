#!/usr/bin/env python3

import sys
import os
import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class FetcherSelenium:
    ASSETS_TAGS = {
        "img": "src",
        "script": "src",
        "link": "href"
    }

    def __init__(self, save_dir=None):
        # for testing purposes we let to define a directory to save a page:
        self.save_dir = save_dir if save_dir else os.path.join(sys.path[0], 'pages')

        # Initializing Selenium web driver
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--incognito')
        self.chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.chrome_options)

        self.url = ""
        self.asset_count = 0
        self.domain_name = ""
        self.assets_dir = ""


    ### Saves the assets near the html file: ###
    def save_asset(self, tag: str, asset_url: str) -> str:
        if not asset_url:
            return ""

        absolute_asset_url = urljoin(self.url, asset_url)
        asset_name = os.path.basename(urlparse(asset_url).path)

        # there are some links not to files but to the APIs like  https://js.stripe.com/v2/
        # we leave them as is because there no particular file
        if not asset_name:
            return ""
        
        # also if the asset doesn't have a file extension, it is probably not an asset
        splitted_filename = os.path.splitext(asset_name)
        ext = splitted_filename[1]
        if tag == 'script':
            ext = '.js' # for simplisity purpoises let's say every script has to be .js
        if not ext:
            return ""

        # some different assets on the page may have the same file name (they may locate in a different directories)
        # for preventing a rewriting the files we make a new asset_name by adding an asset_count to the file name:
        asset_name = "{}_{}{}".format(splitted_filename[0], self.asset_count, ext)
        local_asset_path = os.path.join(self.assets_dir, asset_name)
        self.asset_count += 1

        try:
            response = self.make_request(absolute_asset_url, True)
            with open(local_asset_path, 'wb') as file:
                for chunk in response.iter_content(8192):
                    file.write(chunk)
        except requests.RequestException as e:
            print(f"Error fetching {absolute_asset_url}: {e}")

        except TypeError as e:
            print(f"Error writing to a file {absolute_asset_url}: {e}")
            with open(local_asset_path, 'wt') as file:
                file.write('')
        
        return local_asset_path


    ### Fetches the page from the given url: ###
    def fetch(self, url: str) -> dict[str]:
        self.url = url
        filename = ""
        links_num = 0
        images_num = 0

        self.asset_count = 0
        self.domain_name = urlparse(self.url).netloc
        self.assets_dir = os.path.join(self.save_dir, self.domain_name)

        print(f"Fetching with Selenium {self.url}...")

        try:
            # Fetch the page's HTML
            self.driver.get(self.url)

            # Parse the page using BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Create a directory to save assets
            os.makedirs(self.assets_dir, exist_ok=True)

            # List of tags and attributes to search for URLs to download
            for tag, attr in self.ASSETS_TAGS.items():
                for element in soup.find_all(tag):
                    # Save the asset
                    asset_url = element.attrs.get(attr, "")
                    local_asset_path = self.save_asset(tag, asset_url)

                    if not local_asset_path:
                        continue

                    # Update the attribute in the html to point to the local asset
                    element[attr] = local_asset_path
                    # print("    ", tag, asset_url)

                    # If the image has a srcset tag then save all it's images
                    if tag == "img" and element.has_attr('srcset'):
                        srcset_images = element['srcset'].split(',')
                        new_srcset = []
                        for src_img in srcset_images:
                            src_img = src_img.strip().split(' ') # split on space to separate the URL from the descriptors
                            local_asset_path = self.save_asset(tag, src_img[0])
                            description = src_img[1] if len(src_img) > 1 else ""
                            if local_asset_path:
                                new_srcset.append(f"{local_asset_path} {description}")
                                # print("    ", tag, src_img[0])
                        element['srcset'] = ', '.join(new_srcset)

            # Get the number of links and images
            links_num = len(soup.find_all('a'))
            images_num = len(soup.find_all('img'))

            # Save the modified HTML content to the disk
            filename = f"{self.domain_name}.html"
            html_filename = os.path.join(self.save_dir, filename)
            with open(html_filename, 'w', encoding='utf-8') as file:
                file.write(str(soup))

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"Fetched {self.url} at {current_time}")
            print(f"  - Saved as {filename}")
            print(f"  - Links found on the page: {links_num}")
            print(f"  - Images found on the page: {images_num}")
            print("\n")

        except WebDriverException as e:
            print(f"Error fetching {self.url}: {e}")
        
        return {
            'filename': filename,
            'links_num': links_num,
            'images_num': images_num,
        }


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

    def close(self):
        self.driver.quit()