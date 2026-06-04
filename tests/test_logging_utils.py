import json
import logging
import unittest

from utrends.logging_utils import JsonLogFormatter


class LoggingUtilsTests(unittest.TestCase):
    def test_json_formatter_outputs_structured_record(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )
        payload = json.loads(JsonLogFormatter().format(record))
        self.assertEqual(payload["level"], "INFO")
        self.assertEqual(payload["logger"], "test")
        self.assertEqual(payload["message"], "hello world")
        self.assertIn("ts", payload)


if __name__ == "__main__":
    unittest.main()
