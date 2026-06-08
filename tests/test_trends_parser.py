import unittest

from utrends.trends_parser import parse_traffic_value


class TrendsParserTests(unittest.TestCase):
    def test_parse_traffic_value(self):
        self.assertEqual(parse_traffic_value("10000+"), 10_000)
        self.assertEqual(parse_traffic_value("10K+"), 10_000)
        self.assertEqual(parse_traffic_value("1.5M+"), 1_500_000)
        self.assertEqual(parse_traffic_value(""), 0)


if __name__ == "__main__":
    unittest.main()
