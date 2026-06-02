import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import rss_parser


class FakeResponse:
    status_code = 200
    content = b"<rss><channel><item><title>News</title></item></channel></rss>"

    def raise_for_status(self):
        return None


class FeedHealthTests(unittest.TestCase):
    @patch("rss_parser.requests.get", return_value=FakeResponse())
    def test_check_source_health_reports_success(self, get):
        result = rss_parser.check_source_health("https://example.com/feed.xml")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["entries"], 1)
        get.assert_called_once()

    @patch("rss_parser.requests.get", side_effect=RuntimeError("offline"))
    def test_check_source_health_reports_error(self, get):
        result = rss_parser.check_source_health("https://example.com/feed.xml")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "offline")
        get.assert_called_once()

    @patch("rss_parser.check_source_health")
    def test_check_all_sources_adds_category(self, check):
        check.side_effect = lambda url: {
            "url": url, "ok": True, "status_code": 200,
            "elapsed_ms": 5, "entries": 1, "error": "",
        }
        with tempfile.TemporaryDirectory() as directory:
            feeds_path = Path(directory) / "feeds.json"
            feeds_path.write_text(
                json.dumps({"Tech": ["https://example.com/feed.xml"]}),
                encoding="utf-8",
            )
            results = rss_parser.check_all_sources(str(feeds_path))

        self.assertEqual(results[0]["category"], "Tech")


if __name__ == "__main__":
    unittest.main()
