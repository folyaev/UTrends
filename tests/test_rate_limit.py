import unittest

from rate_limit import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def test_allows_first_call(self):
        limiter = RateLimiter(clock=lambda: 100.0)
        self.assertEqual(limiter.retry_after(1, "search", 30), 0)

    def test_blocks_repeated_call_until_cooldown_expires(self):
        now = [100.0]
        limiter = RateLimiter(clock=lambda: now[0])
        self.assertEqual(limiter.retry_after(1, "search", 30), 0)
        now[0] = 105.1
        self.assertEqual(limiter.retry_after(1, "search", 30), 25)
        now[0] = 130.0
        self.assertEqual(limiter.retry_after(1, "search", 30), 0)

    def test_tracks_users_and_commands_independently(self):
        limiter = RateLimiter(clock=lambda: 100.0)
        self.assertEqual(limiter.retry_after(1, "search", 30), 0)
        self.assertEqual(limiter.retry_after(2, "search", 30), 0)
        self.assertEqual(limiter.retry_after(1, "digest", 30), 0)


if __name__ == "__main__":
    unittest.main()
