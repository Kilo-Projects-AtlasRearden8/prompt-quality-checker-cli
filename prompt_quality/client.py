"""Client for OpenAI-compatible chat endpoints (Ollama by default).

Uses only the Python standard library so the tool runs with no dependencies
and no API keys by default.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


class EndpointError(RuntimeError):
    """Raised when the OpenAI-compatible endpoint cannot be reached or fails."""


@dataclass
class ChatMessage:
    role: str
    content: str


class EndpointClient:
    """Thin wrapper around POST /chat/completions on an OpenAI-compatible endpoint."""

    def __init__(self, endpoint, model, api_key="", timeout=60):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.api_key = api_key or ""
        self.timeout = timeout

    def complete(self, messages):
        """Send a chat completion request and return the assistant message text."""
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.2,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        request = urllib.request.Request(
            f"{self.endpoint}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise EndpointError(f"endpoint returned HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise EndpointError(
                f"could not reach endpoint {self.endpoint}: {exc}"
            ) from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EndpointError(f"endpoint returned invalid JSON: {exc}") from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise EndpointError(f"unexpected endpoint response: {data!r}") from exc
