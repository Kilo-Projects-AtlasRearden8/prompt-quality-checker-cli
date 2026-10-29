"""Command line interface for the prompt quality checker."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .client import EndpointClient, EndpointError
from .reporter import build_report
from .reviewer import Reviewer

DEFAULT_ENDPOINT = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"


def build_parser():
    parser = argparse.ArgumentParser(
        prog="prompt-quality",
        description=(
            "Review a prompt draft for clarity, variables, bias, and safety "
            "using a local-first, OpenAI-compatible endpoint (default Ollama)."
        ),
    )
    parser.add_argument(
        "file", help="Path to the prompt draft text file to review"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write the Markdown report to this file instead of printing it",
    )
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("PQC_ENDPOINT", DEFAULT_ENDPOINT),
        help="OpenAI-compatible endpoint base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("PQC_MODEL", DEFAULT_MODEL),
        help="Model name (default: %(default)s)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("PQC_API_KEY", ""),
        help="API key, if the endpoint requires one (default: none)",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = Path(args.file)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    prompt_text = path.read_text(encoding="utf-8")
    client = EndpointClient(args.endpoint, args.model, args.api_key)
    reviewer = Reviewer(client)

    try:
        result = reviewer.review(prompt_text)
    except EndpointError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            "hint: start Ollama (or another OpenAI-compatible endpoint) and "
            "check PQC_ENDPOINT/PQC_MODEL",
            file=sys.stderr,
        )
        return 1

    report = build_report(result, str(path), args.endpoint, args.model)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"report written to {args.output}")
    else:
        print(report)
    return 0
