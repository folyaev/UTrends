import unittest

from telegram_html import html_link, html_text


class TelegramHtmlTests(unittest.TestCase):
    def test_escapes_external_text(self):
        self.assertEqual(
            html_text("<b>unsafe & quoted</b>"),
            "&lt;b&gt;unsafe &amp; quoted&lt;/b&gt;",
        )

    def test_escapes_link_url_and_label(self):
        self.assertEqual(
            html_link("https://example.com/?q='x'&lang=ru", "<headline>"),
            "<a href='https://example.com/?q=&#x27;x&#x27;&amp;lang=ru'>&lt;headline&gt;</a>",
        )


if __name__ == "__main__":
    unittest.main()
