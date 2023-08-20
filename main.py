#!/usr/bin/env python3

import sys
from fetcher import Fetcher

# For testing with Selenium:
#from fetcherSelenium import FetcherSelenium

def main():
    if len(sys.argv) < 2:
        print("For usage please type: fetch.py url1 url2 ...")
        sys.exit(1)

    fetcher = Fetcher()
    for url in sys.argv[1:]:
        fetcher.fetch(url)

    '''
    # for testing with Selenium:
    fetcherSelenium = FetcherSelenium()
    for url in sys.argv[1:]:
        fetcherSelenium.fetch(url)
    fetcherSelenium.close()
    '''

    print("DONE\n") 


if __name__ == "__main__":
    main()
