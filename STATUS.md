# Status

## What was built

Prompt Quality Checker CLI — a local-first Python tool that reviews prompt
drafts for clarity, variables, bias, and safety using a bundled local rubric
and a configurable OpenAI-compatible endpoint (default Ollama), then emits a
Markdown report. No API keys or third-party network calls by default.

## Package contents

- `prompt_quality/client.py` — stdlib `urllib` client for `POST
  /chat/completions` on OpenAI-compatible endpoints
- `prompt_quality/rubric.py` — local four-category rubric: Clarity, Variables,
  Bias, Safety (1–5 scoring with criteria text)
- `prompt_quality/reviewer.py` — orchestrates one scored check per category;
  JSON-preferred parsing with a free-text regex fallback
- `prompt_quality/reporter.py` — Markdown report with summary table and per-
  category detail sections
- `prompt_quality/cli.py` / `__main__.py` — `prompt-quality` command and
  `python -m prompt_quality`; `--endpoint`, `--model`, `--api-key`, `--output`
- `tests/` — 10 unit tests backed by local mock endpoints (no network, no
  keys): client payload/auth/error handling, reviewer scoring, reporter
  structure, CLI end-to-end
- `pyproject.toml` — package metadata and `prompt-quality` console script
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — install, usage, local-first policy, credits Asdale Dynamics,
  LLC

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
prompt-quality drafts/myprompt.txt
prompt-quality drafts/myprompt.txt --output report.md
PQC_MODEL=phi3.5 PQC_ENDPOINT=http://localhost:1234/v1 prompt-quality drafts/myprompt.txt
python -m prompt_quality drafts/myprompt.txt   # without installing
python -m unittest discover -s tests          # mock endpoints, offline
```

## Verification results

- `pip install -e . --no-deps` succeeds in a fresh venv (system Python is
  PEP 668 externally managed)
- `python -m unittest discover -s tests`: 10 tests OK
- CLI end-to-end through a mock endpoint writes a Markdown report with the
  overall score and all four categories
- Unreachable endpoint yields a friendly error message and exit code 1, with
  no keys, secrets, or personal data anywhere in the repo

## Known gaps

- One LLM call per rubric category; no batching or concurrent checks
- Small models may not return pure JSON; a regex fallback extracts the score
  from free text
- Ollama (or another endpoint) is not bundled — the user runs their own
  endpoint, defaulting to `http://localhost:11434/v1`
- No GitHub Actions workflows; CI is not configured
- Report timestamps use UTC; no localization
