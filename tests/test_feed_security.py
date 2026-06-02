import socket
import unittest

from feed_security import validate_public_http_url


def resolver_for(address):
    def resolve(host, port, type):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port or 80))]
    return resolve


class ValidatePublicHttpUrlTests(unittest.TestCase):
    def test_accepts_public_http_address(self):
        validate_public_http_url(
            "https://example.com/feed.xml",
            resolver=resolver_for("93.184.216.34"),
        )

    def test_rejects_private_address(self):
        with self.assertRaisesRegex(ValueError, "Локальные"):
            validate_public_http_url(
                "http://example.com/feed.xml",
                resolver=resolver_for("192.168.1.10"),
            )

    def test_rejects_loopback_address(self):
        with self.assertRaisesRegex(ValueError, "Локальные"):
            validate_public_http_url(
                "http://localhost/feed.xml",
                resolver=resolver_for("127.0.0.1"),
            )

    def test_rejects_non_http_scheme(self):
        with self.assertRaisesRegex(ValueError, "http"):
            validate_public_http_url("file:///etc/passwd")

    def test_rejects_credentials(self):
        with self.assertRaisesRegex(ValueError, "логином"):
            validate_public_http_url(
                "https://user:pass@example.com/feed.xml",
                resolver=resolver_for("93.184.216.34"),
            )


if __name__ == "__main__":
    unittest.main()
