import unittest

from utrends.time_window import format_window, parse_window_arg


class TimeWindowTests(unittest.TestCase):
    def test_uses_default_without_argument(self):
        self.assertEqual(parse_window_arg("/bloggers", 24, 168), (24, None))

    def test_parses_hours_and_days(self):
        self.assertEqual(parse_window_arg("/bloggers 6h", 24, 168), (6, None))
        self.assertEqual(parse_window_arg("/bloggers 3d", 24, 168), (72, None))
        self.assertEqual(parse_window_arg("/bloggers 2д", 24, 168), (48, None))

    def test_rejects_invalid_or_too_large_window(self):
        hours, error = parse_window_arg("/bloggers week", 24, 168)
        self.assertIsNone(hours)
        self.assertIn("формате", error)

        hours, error = parse_window_arg("/bloggers 8d", 24, 168)
        self.assertIsNone(hours)
        self.assertIn("Максимальное окно", error)

    def test_formats_window(self):
        self.assertEqual(format_window(6), "6 ч.")
        self.assertEqual(format_window(72), "3 дн.")


if __name__ == "__main__":
    unittest.main()
