import os
import unittest
from unittest.mock import patch

from utrends.config import env_int


class EnvIntTests(unittest.TestCase):
    def test_uses_default_for_missing_value(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env_int("MISSING", 7), 7)

    def test_reads_integer_value(self):
        with patch.dict(os.environ, {"LIMIT": "12"}, clear=True):
            self.assertEqual(env_int("LIMIT", 7), 12)

    def test_rejects_invalid_integer(self):
        with patch.dict(os.environ, {"LIMIT": "many"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "LIMIT must be an integer"):
                env_int("LIMIT", 7)

    def test_rejects_value_below_minimum(self):
        with patch.dict(os.environ, {"LIMIT": "0"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "LIMIT must be >= 1"):
                env_int("LIMIT", 7)


if __name__ == "__main__":
    unittest.main()
