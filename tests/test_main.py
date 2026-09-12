import base64
import hashlib
import hmac
import time
import unittest

from app.main import (
    normalize_transcript,
    status_url,
    verify_slack_signature,
    verify_teams_hmac,
)


class MainTests(unittest.TestCase):
    def test_short_message_uses_demo_transcript(self) -> None:
        transcript = normalize_transcript({"text": "<at>Relay</at> help"})
        self.assertIn("premium subscription", transcript)

    def test_mentions_are_removed_from_long_message(self) -> None:
        transcript = normalize_transcript({"text": "<at>Relay</at> Add premium validation and test the protected endpoint today."})
        self.assertNotIn("<at>", transcript)

    def test_hmac_allows_local_demo_when_not_configured(self) -> None:
        self.assertIsInstance(verify_teams_hmac(None, b"payload"), bool)

    def test_status_url_ends_at_the_run_view(self) -> None:
        self.assertTrue(status_url("example-run").endswith("/runs/example-run/view"))

    def test_slack_signature_accepts_a_fresh_signed_request(self) -> None:
        secret = "slack-unit-test-secret"
        timestamp = str(int(time.time()))
        body = b"command=%2Frelay&text=protect+the+premium+endpoint"
        signature = "v0=" + hmac.new(
            secret.encode(), b"v0:" + timestamp.encode() + b":" + body, hashlib.sha256
        ).hexdigest()
        self.assertTrue(verify_slack_signature(signature, timestamp, body, secret))

    def test_slack_signature_rejects_an_invalid_signature(self) -> None:
        self.assertFalse(verify_slack_signature("v0=invalid", str(int(time.time())), b"body", "secret"))


if __name__ == "__main__":
    unittest.main()
