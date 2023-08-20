import os
import sys
import unittest
from unittest.mock import patch, Mock, PropertyMock

from fetcherSelenium import FetcherSelenium

class TestFetcher(unittest.TestCase):

    @patch('fetcherSelenium.requests.get')
    @patch("fetcherSelenium.webdriver.Chrome")
    def test_fetch_successful(self, MockChrome, mock_get):
        sample_html = '<html><body><a href="#">Link</a><img src="image1.jpg" /><img src="image2.jpg" /></body></html>'

        # Mocking the response from requests.get
        mock_response = Mock()
        mock_response.text = sample_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mocking the driver and its methods
        mock_driver_instance = MockChrome.return_value
        type(mock_driver_instance).page_source = PropertyMock(return_value=sample_html)

        save_dir = os.path.join(sys.path[0], 'tests')

        fetcher = FetcherSelenium(save_dir)
        res = fetcher.fetch("http://example.com")

        # Check if the output file exists
        index_path = os.path.join(save_dir, "example.com.html")
        assets_path = os.path.join(save_dir, "example.com")
        
        # !All the assets are indexed with counter!
        image1_path = os.path.join(assets_path, "image1_0.jpg")
        image2_path = os.path.join(assets_path, "image2_1.jpg")

        self.assertTrue(os.path.exists(index_path))
        self.assertTrue(os.path.exists(assets_path))
        self.assertTrue(os.path.exists(image1_path))
        self.assertTrue(os.path.exists(image2_path))

        fetcher.close()

        self.assertEqual(res['filename'], "example.com.html")
        self.assertEqual(res['links_num'], 1)
        self.assertEqual(res['images_num'], 2)

        os.remove(image1_path)
        os.remove(image2_path)
        os.remove(index_path)
        os.rmdir(assets_path)


if __name__ == '__main__':
    unittest.main()
