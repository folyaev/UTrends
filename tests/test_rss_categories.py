import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from utrends import rss_parser


class RssCategoriesTests(unittest.TestCase):
    def test_load_categories_adds_social_feeds_from_rsshub_env(self):
        with tempfile.TemporaryDirectory() as directory:
            feeds_path = Path(directory) / "feeds.json"
            feeds_path.write_text(json.dumps({"Tech": ["https://example.com/rss"]}), encoding="utf-8")
            with patch.dict("os.environ", {
                "RSSHUB_BASE_URL": "https://rsshub.example.com",
                "RSSHUB_X_USERS": "openai",
            }):
                categories = rss_parser.load_categories(str(feeds_path))

        self.assertIn("Соцсети", categories)
        self.assertEqual(categories["Соцсети"], ["https://rsshub.example.com/twitter/user/openai"])


if __name__ == "__main__":
    unittest.main()
