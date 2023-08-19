import os
import sys
import unittest
from unittest.mock import patch, Mock

from fetch import Fetcher

class TestFetcher(unittest.TestCase):

    @patch('fetch.requests.get')
    def test_fetch_successful(self, mock_get):
        # Mocking the response from requests.get
        mock_response = Mock()
        mock_response.text = '<html><body><a href="#">Link</a><img src="image.jpg" /></body></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        save_dir = os.path.join(sys.path[0], 'tests')

        fetcher = Fetcher("http://example.com", save_dir)
        fetcher.fetch()

        # Check if the output file exists
        index_path = os.path.join(save_dir, "example.com.html")
        assets_path = os.path.join(save_dir, "example.com")
        
        # as all the assets are indexed with counter the only image in test page would be image_0.jpg:
        image_path = os.path.join(assets_path, "image_0.jpg")

        self.assertTrue(os.path.exists(index_path))
        self.assertTrue(os.path.exists(assets_path))
        self.assertTrue(os.path.exists(image_path))

        res = fetcher.get_metadata()

        self.assertEqual(res['filename'], "example.com.html")
        self.assertEqual(res['links_num'], 1)
        self.assertEqual(res['images_num'], 1)
        self.assertEqual(res['script_num'], 0)

        os.remove(image_path)
        os.remove(index_path)
        os.rmdir(assets_path)


if __name__ == '__main__':
    unittest.main()
