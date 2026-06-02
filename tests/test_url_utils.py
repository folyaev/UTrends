import unittest

from url_utils import normalize_article_url


class NormalizeArticleUrlTests(unittest.TestCase):
    def test_removes_tracking_parameters_and_fragment(self):
        self.assertEqual(
            normalize_article_url(
                "https://Example.com/story/?utm_source=rss&yclid=123&lang=ru#top"
            ),
            "https://example.com/story?lang=ru",
        )

    def test_removes_trailing_slash(self):
        self.assertEqual(
            normalize_article_url("https://example.com/story/"),
            "https://example.com/story",
        )

    def test_preserves_meaningful_query_parameters(self):
        self.assertEqual(
            normalize_article_url("https://example.com/watch?v=42"),
            "https://example.com/watch?v=42",
        )


if __name__ == "__main__":
    unittest.main()
