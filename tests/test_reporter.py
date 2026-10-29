"""Tests for the Markdown report builder."""

from __future__ import annotations

import unittest

from prompt_quality.reporter import build_report
from prompt_quality.reviewer import CategoryResult, ReviewResult


class ReporterTests(unittest.TestCase):
    def test_report_structure_and_content(self):
        result = ReviewResult(
            "Say hello.",
            [
                CategoryResult("clarity", "Clarity", 5, "Clear task."),
                CategoryResult("variables", "Variables", 3, "No variables defined."),
                CategoryResult("bias", "Bias", 5, "Neutral."),
                CategoryResult("safety", "Safety", 5, "Safe."),
            ],
        )
        report = build_report(
            result, "drafts/hello.txt", "http://localhost:11434/v1", "llama3.2"
        )

        self.assertIn("# Prompt Quality Review", report)
        self.assertIn("drafts/hello.txt", report)
        self.assertIn("http://localhost:11434/v1", report)
        self.assertIn("llama3.2", report)
        self.assertIn("Overall score: **4.5 / 5**", report)
        self.assertIn("| Clarity | 5 / 5 |", report)
        self.assertIn("| Variables | 3 / 5 |", report)
        self.assertIn("### Clarity (5 / 5)", report)
        self.assertIn("Clear task.", report)
        self.assertIn("Asdale Dynamics, LLC", report)

    def test_report_contains_all_four_categories(self):
        result = ReviewResult(
            "x",
            [
                CategoryResult("clarity", "Clarity", 1, "r"),
                CategoryResult("variables", "Variables", 1, "r"),
                CategoryResult("bias", "Bias", 1, "r"),
                CategoryResult("safety", "Safety", 1, "r"),
            ],
        )
        report = build_report(result, "f.txt", "http://localhost:11434/v1", "m")
        for title in ("Clarity", "Variables", "Bias", "Safety"):
            self.assertIn(f"### {title} (1 / 5)", report)
