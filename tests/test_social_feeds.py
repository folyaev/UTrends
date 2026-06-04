import unittest

from utrends.social_feeds import build_rsshub_social_feeds


class SocialFeedsTests(unittest.TestCase):
    def test_returns_empty_without_base_url(self):
        self.assertEqual(build_rsshub_social_feeds(env={}), [])

    def test_builds_rsshub_routes(self):
        feeds = build_rsshub_social_feeds(env={
            "RSSHUB_BASE_URL": "https://rsshub.example.com/",
            "RSSHUB_VK_USERS": "durov",
            "RSSHUB_VK_GROUPS": "club1",
            "RSSHUB_OK_GROUPS": "ok-group",
            "RSSHUB_X_USERS": "@openai",
        })
        self.assertEqual(feeds, [
            "https://rsshub.example.com/vk/user/durov",
            "https://rsshub.example.com/vk/group/club1",
            "https://rsshub.example.com/ok/group/ok-group",
            "https://rsshub.example.com/twitter/user/openai",
        ])


if __name__ == "__main__":
    unittest.main()
