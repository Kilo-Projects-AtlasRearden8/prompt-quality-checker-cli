"""End-to-end CLI tests using the mock endpoint and a temporary output file."""

from __future__ import annotations

import os
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

from prompt_quality.cli import main


class _ScoringHandler(BaseHTTPRequestHandler):
    CANNED = {
        "clarity": '{"score": 4, "reasoning": "Fairly clear."}',
        "variables": '{"score": 4, "reasoning": "Variables look fine."}',
        "bias": '{"score": 5, "reasoning": "Neutral."}',
        "safety": '{"score": 5, "reasoning": "Safe."}',
    }

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        system_content = payload["messages"][0]["content"]
        slug = "clarity"
        for key in self.CANNED:
            if f"Category: {key.title()}" in system_content:
                slug = key
                break
        content = self.CANNED[slug]
        response = json.dumps({"choices": [{"message": {"content": content}}]}).encode(
            "utf-8"
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, *args):
        pass


class CLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _ScoringHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _write_prompt(self, text):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
        return path

    def test_cli_writes_report_to_file(self):
        prompt_path = self._write_prompt("Draft a welcome email to {name}.")
        try:
            out_path = prompt_path + ".md"
            code = main(
                    [
                        prompt_path,
                        "--output",
                        out_path,
                        "--endpoint",
                        f"http://127.0.0.1:{self.port}/v1",
                        "--model",
                        "mock-model",
                    ]
                )
            self.assertEqual(code, 0)
            with open(out_path, encoding="utf-8") as handle:
                report = handle.read()
            self.assertIn("# Prompt Quality Review", report)
            self.assertIn("Overall score: **4.5 / 5**", report)
        finally:
            os.unlink(prompt_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_cli_missing_file_returns_error(self):
        self.assertEqual(main(["/nonexistent/prompt.txt"]), 1)
