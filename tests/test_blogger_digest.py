import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from utrends import blogger_digest


class BloggerDigestTests(unittest.TestCase):
    def test_extract_timecodes_keeps_unique_timestamps(self):
        text = "00:00 intro\n01:25 topic\n01:25 repeated\n1:02:03 long chapter"

        self.assertEqual(
            blogger_digest.extract_timecodes(text),
            ["00:00", "01:25", "1:02:03"],
        )

    def test_description_snippet_strips_html_links_and_timecodes(self):
        text = "<p>00:00 intro</p> Main topic https://example.com details"

        self.assertEqual(
            blogger_digest.description_snippet(text),
            "intro Main topic details",
        )

    def test_load_bloggers_reads_channels_list(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bloggers.json"
            path.write_text(
                (
                    '{"channels":[{"name":"Channel","url":"https://example.com/feed",'
                    '"parser_priority":1,"banned_ru":true}]}'
                ),
                encoding="utf-8",
            )

            channels = blogger_digest.load_bloggers(str(path))

        self.assertEqual(channels[0]["name"], "Channel")
        self.assertEqual(channels[0]["url"], "https://example.com/feed")
        self.assertEqual(channels[0]["platform"], "youtube")
        self.assertEqual(channels[0]["parser_priority"], 1)
        self.assertTrue(channels[0]["banned_ru"])

    def test_split_title_topics_removes_channel_suffix_and_splits(self):
        self.assertEqual(
            blogger_digest.split_title_topics("Focus Group Rejects Ukraine Funding | Breaking Points"),
            ["Focus Group Rejects Ukraine Funding"],
        )
        self.assertEqual(
            blogger_digest.split_title_topics("Topic one / Topic two / Topic three"),
            ["Topic one", "Topic two", "Topic three"],
        )

    def test_split_title_topics_ignores_live_prefix(self):
        self.assertEqual(
            blogger_digest.split_title_topics("LIVE: OSCE briefing on Armenia election"),
            ["OSCE briefing on Armenia election"],
        )

    def test_parse_chapters_validates_order_and_filters_noise(self):
        chapters = blogger_digest.parse_chapters(
            "00:00 Intro\n"
            "01:20 Main story\n"
            "03:00 Реклама\n"
            "05:10 Second story\n"
        )

        self.assertEqual(
            [(chapter["start_time"], chapter["title"]) for chapter in chapters],
            [("00:00", "Intro"), ("01:20", "Main story"), ("05:10", "Second story")],
        )

    def test_build_blogger_digest_ranks_repeated_topics_across_channels(self):
        now = 1_700_000_000
        videos_by_url = {
            "feed-a": [{
                "title": "OpenAI released a new model",
                "link": "https://youtu.be/a",
                "channel": "A",
                "description": "00:00 intro",
                "timecodes": ["00:00"],
                "time": now,
                "words": blogger_digest.token_set("OpenAI released a new model"),
            }],
            "feed-b": [{
                "title": "New OpenAI model release explained",
                "link": "https://youtu.be/b",
                "channel": "B",
                "description": "00:00 intro",
                "timecodes": ["00:00"],
                "time": now,
                "words": blogger_digest.token_set("New OpenAI model release explained"),
            }],
            "feed-c": [{
                "title": "Random camera review",
                "link": "https://youtu.be/c",
                "channel": "C",
                "description": "",
                "timecodes": [],
                "time": now,
                "words": blogger_digest.token_set("Random camera review"),
            }],
        }

        def fake_fetch(channel):
            return videos_by_url[channel["url"]]

        with patch.object(blogger_digest, "load_bloggers", return_value=[
            {"name": "A", "url": "feed-a"},
            {"name": "B", "url": "feed-b"},
            {"name": "C", "url": "feed-c"},
        ]), patch.object(blogger_digest, "fetch_blogger_channel", side_effect=fake_fetch), \
                patch.object(blogger_digest.time, "time", return_value=now):
            digest = blogger_digest.build_blogger_digest("bloggers.json", time_window_hours=24)

        self.assertEqual(len(digest["repeated"]), 1)
        self.assertEqual(digest["repeated"][0]["channel_count"], 2)
        self.assertEqual(len(digest["latest"]), 3)

    def test_topic_clusters_use_titles_and_chapters_with_singles_last(self):
        now = 1_700_000_000
        videos_by_url = {
            "feed-a": [{
                "title": "Daily show / Drone attack in Kuwait",
                "link": "https://youtu.be/a",
                "video_url": "https://youtu.be/a",
                "channel": "A",
                "chapters": [
                    {"start_time": "00:00", "start_seconds": 0, "title": "Intro"},
                    {"start_time": "03:00", "start_seconds": 180, "title": "Telegram regulation"},
                ],
                "title_topics": ["Daily show", "Drone attack in Kuwait"],
                "time": now,
                "words": blogger_digest.token_set("Daily show Drone attack in Kuwait"),
            }],
            "feed-b": [{
                "title": "Kuwait drone attack explained",
                "link": "https://youtu.be/b",
                "video_url": "https://youtu.be/b",
                "channel": "B",
                "chapters": [],
                "title_topics": ["Kuwait drone attack explained"],
                "time": now - 1,
                "words": blogger_digest.token_set("Kuwait drone attack explained"),
            }],
        }

        def fake_fetch(channel):
            return videos_by_url[channel["url"]]

        with patch.object(blogger_digest, "load_bloggers", return_value=[
            {"name": "A", "url": "feed-a"},
            {"name": "B", "url": "feed-b"},
        ]), patch.object(blogger_digest, "fetch_blogger_channel", side_effect=fake_fetch), \
                patch.object(blogger_digest.time, "time", return_value=now):
            digest = blogger_digest.build_blogger_digest("bloggers.json", time_window_hours=24)

        self.assertTrue(digest["repeated_topics"])
        self.assertIn("Drone", digest["repeated_topics"][0]["main_title"])
        self.assertEqual(digest["repeated_topics"][0]["item_count"], 2)
        self.assertTrue(digest["single_topics"])
        self.assertEqual(digest["single_topics"][0]["main_title"], "Daily show")

    def test_same_video_title_and_chapter_do_not_create_repeated_topic(self):
        now = 1_700_000_000
        videos_by_url = {
            "feed-a": [{
                "title": "Kuwait drone attack explained",
                "link": "https://youtu.be/a",
                "video_url": "https://youtu.be/a",
                "channel": "A",
                "chapters": [
                    {"start_time": "00:00", "start_seconds": 0, "title": "Kuwait drone attack explained"},
                ],
                "title_topics": ["Kuwait drone attack explained"],
                "time": now,
                "words": blogger_digest.token_set("Kuwait drone attack explained"),
            }],
        }

        with patch.object(blogger_digest, "load_bloggers", return_value=[
            {"name": "A", "url": "feed-a"},
        ]), patch.object(blogger_digest, "fetch_blogger_channel", side_effect=lambda channel: videos_by_url[channel["url"]]), \
                patch.object(blogger_digest.time, "time", return_value=now):
            digest = blogger_digest.build_blogger_digest("bloggers.json", time_window_hours=24)

        self.assertEqual(digest["repeated_topics"], [])
        self.assertEqual(digest["single_topics"][0]["item_count"], 2)

    def test_live_prefix_does_not_create_repeated_topic(self):
        now = 1_700_000_000
        videos_by_url = {
            "feed-a": [{
                "title": "LIVE: Beirut skyline",
                "link": "https://youtu.be/a",
                "video_url": "https://youtu.be/a",
                "channel": "A",
                "chapters": [],
                "title_topics": ["LIVE", "Beirut skyline"],
                "time": now,
                "words": blogger_digest.token_set("LIVE Beirut skyline"),
            }],
            "feed-b": [{
                "title": "LIVE: Tel Aviv skyline",
                "link": "https://youtu.be/b",
                "video_url": "https://youtu.be/b",
                "channel": "B",
                "chapters": [],
                "title_topics": ["LIVE", "Tel Aviv skyline"],
                "time": now,
                "words": blogger_digest.token_set("LIVE Tel Aviv skyline"),
            }],
        }

        with patch.object(blogger_digest, "load_bloggers", return_value=[
            {"name": "A", "url": "feed-a"},
            {"name": "B", "url": "feed-b"},
        ]), patch.object(blogger_digest, "fetch_blogger_channel", side_effect=lambda channel: videos_by_url[channel["url"]]), \
                patch.object(blogger_digest.time, "time", return_value=now):
            digest = blogger_digest.build_blogger_digest("bloggers.json", time_window_hours=24)

        self.assertEqual(digest["repeated_topics"], [])
        self.assertNotIn("LIVE", [cluster["main_title"] for cluster in digest["topic_clusters"]])

    def test_detects_shorts(self):
        self.assertTrue(blogger_digest.is_short_video("https://youtube.com/shorts/abc", "Title"))
        self.assertTrue(blogger_digest.is_short_video("https://youtube.com/watch?v=abc", "Title #Shorts"))
        self.assertFalse(blogger_digest.is_short_video("https://youtube.com/watch?v=abc", "Title"))


if __name__ == "__main__":
    unittest.main()
