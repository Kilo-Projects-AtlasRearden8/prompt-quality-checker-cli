"""Tests for the OpenAI-compatible endpoint client, backed by a local mock
server. No network access and no API keys are required.
"""

from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from prompt_quality.client import ChatMessage, EndpointClient, EndpointError


class _RecordingHandler(BaseHTTPRequestHandler):
    """Mock /chat/completions that records requests and replies with canned JSON."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.server.received_body = self.rfile.read(length)
        self.server.received_path = self.path
        self.server.received_headers = dict(self.headers)
        response = {
            "choices": [
                {"message": {"content": '{"score": 4, "reasoning": "clear enough"}'}}
            ]
        }
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class MockEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _RecordingHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_complete_returns_assistant_text(self):
        client = EndpointClient(f"http://127.0.0.1:{self.port}/v1", "test-model")
        content = client.complete([ChatMessage("user", "hello world")])
        self.assertEqual(content, '{"score": 4, "reasoning": "clear enough"}')

    def test_complete_sends_expected_payload(self):
        client = EndpointClient(f"http://127.0.0.1:{self.port}/v1", "test-model")
        client.complete([ChatMessage("user", "hello world")])
        payload = json.loads(self.server.received_body)
        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(
            payload["messages"], [{"role": "user", "content": "hello world"}]
        )
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["temperature"], 0.2)

    def test_complete_sends_authorization_header(self):
        client = EndpointClient(
            f"http://127.0.0.1:{self.port}/v1", "test-model", api_key="sk-test"
        )
        client.complete([ChatMessage("user", "hello world")])
        self.assertEqual(
            self.server.received_headers.get("Authorization"), "Bearer sk-test"
        )

    def test_connection_failure_raises_endpoint_error(self):
        client = EndpointClient("http://127.0.0.1:1", "test-model")
        with self.assertRaises(EndpointError):
            client.complete([ChatMessage("user", "hello")])
