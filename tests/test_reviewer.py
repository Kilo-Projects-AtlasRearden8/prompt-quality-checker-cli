"""Tests for the reviewer, backed by a local mock endpoint that returns
different canned scores per rubric category. No network access or keys needed.
"""

from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from prompt_quality.client import EndpointClient
from prompt_quality.reviewer import Reviewer


class _ScoringHandler(BaseHTTPRequestHandler):
    """Mock endpoint returning canned scores keyed by rubric category."""

    CANNED = {
        "clarity": '{"score": 5, "reasoning": "Task and output format are clear."}',
        "variables": (
            '{"score": 3, "reasoning": "Variable {name} is used but never defined."}'
        ),
        "bias": '{"score": 5, "reasoning": "Neutral language throughout."}',
        "safety": '{"score": 5, "reasoning": "Requests general information only."}',
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


class ReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _ScoringHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_review_returns_all_categories_with_scores(self):
        client = EndpointClient(f"http://127.0.0.1:{self.port}/v1", "mock-model")
        reviewer = Reviewer(client)
        result = reviewer.review("Write a friendly email to {name} about their order.")

        scores = {cat.slug: cat.score for cat in result.categories}
        self.assertEqual(
            scores, {"clarity": 5, "variables": 3, "bias": 5, "safety": 5}
        )
        self.assertEqual(len(result.categories), 4)
        self.assertAlmostEqual(result.overall, 4.5)
        self.assertEqual(result.categories[1].title, "Variables")
        self.assertIn("{name}", result.categories[1].reasoning)

    def test_review_reasoning_is_preserved(self):
        client = EndpointClient(f"http://127.0.0.1:{self.port}/v1", "mock-model")
        reviewer = Reviewer(client)
        result = reviewer.review("Say hello.")
        reasons = {cat.slug: cat.reasoning for cat in result.categories}
        self.assertEqual(
            reasons["clarity"], "Task and output format are clear."
        )
