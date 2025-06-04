"""Testing suite for the scraper module."""

import unittest
import requests
import io
import sys
from unittest.mock import patch, MagicMock
from scraper import search_posts


class TestSearchPosts(unittest.TestCase):
    """Testing the search_posts() method."""

    @patch("scraper.requests.get")
    def test_no_query(self, mock_get: MagicMock) -> None:
        """Test if the function raises ValueError when a query is not provided."""
        params = {}
        token = "valid_token"

        with self.assertRaises(ValueError) as cm:
            search_posts(params, token)

        mock_get.assert_not_called()
        self.assertIn("query", str(cm.exception).lower())

    @patch("scraper.requests.get")
    def test_no_token(self, mock_get: MagicMock) -> None:
        """Test if the function raises ValueError when a token is not provided."""
        params = {"q": "test"}
        token = None

        with self.assertRaises(ValueError) as cm:
            search_posts(params, token)

        mock_get.assert_not_called()
        self.assertIn("token", str(cm.exception).lower())

    @patch("scraper.requests.get")
    def test_valid_response(self, mock_get: MagicMock) -> None:
        """Test that the function returns a list of posts when valid parameters are provided."""
        params = {"q": "test"}
        token = "valid_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "posts": [
                {
                    "uri": "at://did:plc:12345/app.bsky.feed.post/abcdef",
                    "cid": "bafyre123...",
                    "author": {
                        "did": "did:plc:12345",
                        "handle": "author_handle",
                        "displayName": "Author Name",
                    },
                    "record": {
                        "text": "Post content",
                        "createdAt": "2023-10-01T00:00:00Z",
                        "$type": "app.bsky.feed.post",
                    },
                    "indexedAt": "2023-10-01T00:00:01Z",
                }
            ],
            "cursor": None,
        }

        mock_get.return_value = mock_response

        result = search_posts(params, token)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["record"]["text"], "Post content")
        self.assertEqual(result[0]["author"]["handle"], "author_handle")
        self.assertEqual(result[0]["record"]["createdAt"], "2023-10-01T00:00:00Z")
        self.assertEqual(
            result[0]["uri"], "at://did:plc:12345/app.bsky.feed.post/abcdef"
        )

    # Simulate a failed API response (e.g., 400: [InvalidRequest, ExpiredToken, InvalidToken, BadQueryString])
    @patch("scraper.requests.get")
    def test_invalid_request(self, mock_get: MagicMock) -> None:
        """Test that the function handles invalid requests gracefully."""
        params = {"q": "test"}
        token = "invalid_token"

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error: InvalidToken"
        )
        mock_get.return_value = mock_response

        # Redirecting stdout to StringIO
        captured_output = io.StringIO()
        sys.stdout = captured_output

        result = search_posts(params, token)
        sys.stdout = sys.__stdout__

        self.assertEqual(result, [])
        self.assertIn("400 Client Error:", captured_output.getvalue())


if __name__ == "__main__":
    unittest.main()
