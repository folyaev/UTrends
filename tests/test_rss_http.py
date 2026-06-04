import unittest
from unittest.mock import Mock, patch

from utrends import rss_parser


class RssHttpTests(unittest.TestCase):
    def tearDown(self):
        rss_parser._HTTP_SESSION = None

    def test_fetch_url_uses_retry_session_and_raises_for_status(self):
        response = Mock()
        session = Mock()
        session.get.return_value = response
        with patch("utrends.rss_parser.get_http_session", return_value=session):
            result = rss_parser.fetch_url("https://example.com/feed.xml")

        self.assertIs(result, response)
        session.get.assert_called_once_with(
            "https://example.com/feed.xml",
            headers=rss_parser.DEFAULT_HEADERS,
            timeout=rss_parser.FETCH_TIMEOUT_SECONDS,
        )
        response.raise_for_status.assert_called_once()

    def test_get_http_session_mounts_retry_adapters(self):
        with patch("utrends.rss_parser.requests.Session") as session_factory:
            session = session_factory.return_value
            result = rss_parser.get_http_session()

        self.assertIs(result, session)
        self.assertEqual(session.mount.call_count, 2)


if __name__ == "__main__":
    unittest.main()
