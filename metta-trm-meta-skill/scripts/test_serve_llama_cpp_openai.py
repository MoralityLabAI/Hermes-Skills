from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("serve_llama_cpp_openai.py")
SPEC = importlib.util.spec_from_file_location("serve_llama_cpp_openai", SCRIPT)
assert SPEC and SPEC.loader
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


class ServeLlamaCppOpenAITests(unittest.TestCase):
    def test_make_chat_response_normalizes_text_choice(self) -> None:
        response = server.make_chat_response({"choices": [{"text": "hello"}]}, "test-model", 1000.0)
        self.assertEqual(response["model"], "test-model")
        self.assertEqual(response["choices"][0]["message"]["content"], "hello")

    def test_make_chat_response_handles_empty_choices(self) -> None:
        response = server.make_chat_response({}, "test-model", 1000.0)
        self.assertEqual(response["choices"][0]["message"]["role"], "assistant")
        self.assertEqual(response["choices"][0]["message"]["content"], "")


if __name__ == "__main__":
    unittest.main()
