# Prompt Quality Checker CLI

A local-first Python CLI that reviews prompt drafts for **clarity, variables,
bias, and safety** using a configurable OpenAI-compatible endpoint (default
Ollama). It applies a local rubric and writes a Markdown report. No API keys
required by default.

Created by Dylan Asdale for **Asdale Dynamics, LLC** — beginner-friendly AI
education, books, and practical tools.

## Features

- Reviews any prompt draft text file against four rubric categories:
  Clarity, Variables, Bias, Safety
- Each category is scored 1–5 with short reasoning, plus an overall score
- Configurable endpoint via `--endpoint` or the `PQC_ENDPOINT` environment
  variable; default is Ollama at `http://localhost:11434/v1`
- Works with any OpenAI-compatible API (Ollama, LM Studio, and similar)
- Markdown report printed to stdout or written with `--output`
- Standard library only — nothing to `pip install` beyond the package itself
- Tested against a local mock endpoint: no network access or API keys needed
  to run the test suite

## Install

```bash
git clone <this repo>
cd prompt-quality-checker-cli
pip install -e .
```

This registers the `prompt-quality` command. You can also run it without
installing:

```bash
python -m prompt_quality prompts/draft.txt
```

## Usage

```bash
# Review a draft against the local Ollama endpoint
prompt-quality prompts/draft.txt

# Write a Markdown report to a file
prompt-quality prompts/draft.txt --output report.md

# Use a different model or endpoint
PQC_MODEL=phi3.5 prompt-quality prompts/draft.txt
prompt-quality prompts/draft.txt --endpoint http://localhost:1234/v1 --model llama3.2

# If your endpoint requires a key
prompt-quality prompts/draft.txt --api-key "$PQC_API_KEY"
```

### Example report

```markdown
# Prompt Quality Review

- **Source:** prompts/draft.txt
- **Reviewed:** 2026-10-29T09:30:00Z
- **Endpoint:** http://localhost:11434/v1
- **Model:** llama3.2

## Summary

Overall score: **4.3 / 5**

| Category | Score |
|---|---|
| Clarity | 5 / 5 |
| Variables | 3 / 5 |
| Bias | 5 / 5 |
| Safety | 4 / 5 |

## Category details

### Clarity (5 / 5)

Task and output format are clear.

...
```

## Local-first

This tool runs on your machine. The only network call it makes is to your own
endpoint (Ollama by default). Nothing is uploaded, and no keys or personal
data are stored. The rubric is bundled locally, so the standard used for
reviewing is fixed and visible.

## Tests

The suite uses a mock endpoint on localhost, so no network access or API keys
are required:

```bash
python -m unittest discover -s tests
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.
