import unittest

from utrends.healthcheck import is_bot_process


class HealthcheckTests(unittest.TestCase):
    def test_detects_bot_process(self):
        self.assertTrue(is_bot_process("python bot.py"))
        self.assertTrue(is_bot_process("python -m utrends.bot"))

    def test_rejects_other_python_process(self):
        self.assertFalse(is_bot_process("python healthcheck.py"))


if __name__ == "__main__":
    unittest.main()
