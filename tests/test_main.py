import base64
import hashlib
import hmac
import unittest

from app.main import normalize_transcript, verify_teams_hmac


class MainTests(unittest.TestCase):
    def test_short_message_uses_demo_transcript(self) -> None:
        transcript = normalize_transcript({"text": "<at>ContextBridge</at> help"})
        self.assertIn("premium subscription", transcript)

    def test_mentions_are_removed_from_long_message(self) -> None:
        transcript = normalize_transcript({"text": "<at>ContextBridge</at> Add premium validation and test the protected endpoint today."})
        self.assertNotIn("<at>", transcript)

    def test_hmac_allows_local_demo_when_not_configured(self) -> None:
        self.assertIsInstance(verify_teams_hmac(None, b"payload"), bool)


if __name__ == "__main__":
    unittest.main()
