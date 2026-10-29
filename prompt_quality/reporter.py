"""Markdown report generation for review results."""

from __future__ import annotations

import datetime

from .reviewer import ReviewResult


def build_report(result: ReviewResult, source: str, endpoint: str, model: str) -> str:
    """Render a Markdown report for a review result."""
    lines = []
    lines.append("# Prompt Quality Review")
    lines.append("")
    lines.append(f"- **Source:** {source}")
    lines.append(f"- **Reviewed:** {_now()}")
    lines.append(f"- **Endpoint:** {endpoint}")
    lines.append(f"- **Model:** {model}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"Overall score: **{result.overall:.1f} / 5**")
    lines.append("")
    lines.append("| Category | Score |")
    lines.append("|---|---|")
    for cat in result.categories:
        lines.append(f"| {cat.title} | {cat.score} / 5 |")
    lines.append("")
    lines.append("## Category details")
    lines.append("")
    for cat in result.categories:
        lines.append(f"### {cat.title} ({cat.score} / 5)")
        lines.append("")
        lines.append(cat.reasoning or "No reasoning returned by the reviewer.")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "Reviewed with the Prompt Quality Checker CLI (Asdale Dynamics, LLC)."
    )
    lines.append("")
    return "\n".join(lines)


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
