import json
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class ExampleConfigTests(unittest.TestCase):
    def test_feeds_example_is_category_map(self):
        data = json.loads((BASE_DIR / "feeds.example.json").read_text(encoding="utf-8"))

        self.assertIsInstance(data, dict)
        self.assertTrue(data)
        for category, urls in data.items():
            self.assertIsInstance(category, str)
            self.assertIsInstance(urls, list)
            self.assertTrue(urls)
            self.assertTrue(all(isinstance(url, str) and url.startswith("https://") for url in urls))

    def test_youtube_examples_have_channels(self):
        for file_name, feed_type in (
            ("bloggers.example.json", "blogger"),
            ("news_channels.example.json", "news_channel"),
        ):
            with self.subTest(file_name=file_name):
                data = json.loads((BASE_DIR / file_name).read_text(encoding="utf-8"))
                self.assertIn("channels", data)
                self.assertTrue(data["channels"])
                for channel in data["channels"]:
                    self.assertEqual(channel["platform"], "youtube")
                    self.assertEqual(channel["feed_type"], feed_type)
                    self.assertTrue(channel["source_id"])
                    self.assertTrue(channel["name"])
                    self.assertTrue(channel["url"].startswith("https://www.youtube.com/feeds/videos.xml?channel_id="))
                    self.assertIn("parser_priority", channel)
                    self.assertIn("banned_ru", channel)


if __name__ == "__main__":
    unittest.main()
