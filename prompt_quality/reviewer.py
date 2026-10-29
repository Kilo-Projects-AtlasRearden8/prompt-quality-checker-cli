"""Orchestrates rubric-based review of a prompt draft."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .client import ChatMessage, EndpointClient
from .rubric import CATEGORY_ORDER, category_spec


@dataclass
class CategoryResult:
    slug: str
    title: str
    score: int
    reasoning: str


@dataclass
class ReviewResult:
    prompt: str
    categories: list[CategoryResult] = field(default_factory=list)

    @property
    def overall(self):
        if not self.categories:
            return 0.0
        return sum(c.score for c in self.categories) / len(self.categories)


def build_review_messages(prompt_text, slug):
    """Build the system/user messages asking the endpoint to score one category."""
    spec = category_spec(slug)
    system = (
        "You are a careful editor who reviews AI prompt drafts for beginners. "
        "Score the draft from 1 (poor) to 5 (excellent) on the category below "
        "using only the provided rubric. Reply with JSON only: "
        '{"score": <integer 1-5>, "reasoning": "<one or two sentences>"}.\n\n'
        f"Category: {spec['title']}\nRubric: {spec['criteria']}"
    )
    user = f"Prompt draft to review:\n\n{prompt_text}\n\nReturn JSON only."
    return [ChatMessage("system", system), ChatMessage("user", user)]


def _parse_score(text):
    """Parse the endpoint's reply into a (score, reasoning) tuple.

    The endpoint is asked for JSON, but small models are unpredictable, so a
    regex fallback extracts a score when JSON parsing fails.
    """
    try:
        data = json.loads(text)
        score = int(data["score"])
        reasoning = str(data.get("reasoning", "")).strip()
    except (ValueError, KeyError, TypeError):
        match = re.search(r"\bscore\b[^0-9]{0,20}?(\d)\b", text, re.IGNORECASE)
        score = int(match.group(1)) if match else 3
        reasoning = text.strip()
    return max(1, min(5, score)), reasoning


class Reviewer:
    def __init__(self, client: EndpointClient):
        self.client = client

    def review(self, prompt_text):
        """Review a draft across all rubric categories."""
        results = []
        for slug in CATEGORY_ORDER:
            messages = build_review_messages(prompt_text, slug)
            text = self.client.complete(messages)
            score, reasoning = _parse_score(text)
            spec = category_spec(slug)
            results.append(CategoryResult(slug, spec["title"], score, reasoning))
        return ReviewResult(prompt_text, results)
