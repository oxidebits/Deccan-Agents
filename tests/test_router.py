import unittest

from app.core.router import OpenRouterManager


class OpenRouterParserTests(unittest.TestCase):
    def test_parser_accepts_a_markdown_json_fence(self) -> None:
        parsed = OpenRouterManager._parse_json_object('```json\n{"title": "Premium"}\n```')
        self.assertEqual(parsed, {"title": "Premium"})

    def test_parser_extracts_json_after_reasoning_text(self) -> None:
        parsed = OpenRouterManager._parse_json_object(
            'I reviewed the request.\n{"decision": "approved", "checks": []}'
        )
        self.assertEqual(parsed["decision"], "approved")


if __name__ == "__main__":
    unittest.main()
