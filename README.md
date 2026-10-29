# Prompt Quality Checker CLI

A friendly, local-first Python CLI that reads a prompt draft and reviews it for
**clarity, variables, bias, and safety**, then writes a Markdown report with a
score from 1 to 5 for each category. It talks to a local OpenAI-compatible
endpoint (Ollama by default) — no API keys, no cloud accounts, nothing uploaded.

Created by Dylan Asdale for **Asdale Dynamics, LLC** — beginner-friendly AI
education, books, and practical tools.

## What it does

You give it a text file containing a prompt draft. The tool sends that draft to
your local model endpoint and asks it to score the draft in four areas:

- **Clarity** — Is the task, audience, and desired output easy to understand?
- **Variables** — Are placeholder variables (like `{name}` or `{topic}`) used
  consistently and defined?
- **Bias** — Does the draft avoid harmful assumptions and stereotypes?
- **Safety** — Does the draft avoid asking for disallowed or risky content?

Each category gets a score of 1 (needs work) to 5 (great) plus a short
explanation, and the report shows an overall average score.

## Install

```bash
git clone <this repo>
cd prompt-quality-checker-cli
python3 -m venv .venv
.venv/bin/pip install -e .
```

This registers the `prompt-quality` command. You can also run it without
installing:

```bash
python -m prompt_quality prompts/draft.txt
```

## What you need

This tool doesn't run the AI model itself — it sends your draft to an endpoint
you already have running, defaulting to Ollama at
`http://localhost:11434/v1`.

1. Install Ollama from https://ollama.com if you haven't already.
2. Pull a model, for example:
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama (it usually runs automatically after install).

If you use another OpenAI-compatible endpoint (LM Studio, etc.), point the tool
at it with `--endpoint`.

## Usage

Review a draft and see the report in your terminal:

```bash
prompt-quality prompts/draft.txt
```

Write the report to a Markdown file:

```bash
prompt-quality prompts/draft.txt --output report.md
```

Use a different model or endpoint:

```bash
prompt-quality prompts/draft.txt --model phi3.5
prompt-quality prompts/draft.txt --endpoint http://localhost:1234/v1 --model llama3.2
```

Set defaults with environment variables instead of flags:

```bash
export PQC_ENDPOINT=http://localhost:11434/v1
export PQC_MODEL=llama3.2
prompt-quality prompts/draft.txt
```

If your endpoint requires an API key:

```bash
prompt-quality prompts/draft.txt --api-key "$PQC_API_KEY"
```

## Worked example

Save a draft to `prompts/welcome_email.txt`:

```
Write a short, friendly welcome email to {customer_name} about their recent
order. Include the order number and a thank-you message. Keep it under 100
words.
```

Run the checker:

```bash
prompt-quality prompts/welcome_email.txt --output welcome_email_report.md
```

You'll get a Markdown report like:

```markdown
# Prompt Quality Review

- **Source:** prompts/welcome_email.txt
- **Reviewed:** 2026-10-29T10:15:00Z
- **Endpoint:** http://localhost:11434/v1
- **Model:** llama3.2

## Summary

Overall score: **4.5 / 5**

| Category | Score |
|---|---|
| Clarity | 5 / 5 |
| Variables | 4 / 5 |
| Bias | 5 / 5 |
| Safety | 4 / 5 |

## Category details

### Clarity (5 / 5)

The task, audience, and output length are clear.

### Variables (4 / 5)

{customer_name} is used, but the order-number placeholder isn't defined.

### Bias (5 / 5)

Neutral, inclusive language throughout.

### Safety (4 / 5)

Requests general customer-service content only.

---

Reviewed with the Prompt Quality Checker CLI (Asdale Dynamics, LLC).
```

## Local-first

This tool runs on your machine. The only network call it makes is to your own
endpoint (Ollama by default). Nothing is uploaded, and no keys or personal
data are stored. The rubric used for scoring is bundled locally, so the
standard applied to your drafts is fixed and visible.

## Tests

The test suite uses a mock endpoint on localhost, so no network access or API
keys are required:

```bash
python -m unittest discover -s tests
```

## Troubleshooting

**`could not reach endpoint ... Connection refused`**
Ollama isn't running or isn't listening where the tool expects. Start Ollama,
or point the tool at your endpoint with `--endpoint`.

**`endpoint returned HTTP 404`**
The model name may not be installed. Run `ollama pull <model>` or change
`--model`.

**`file not found`**
Check the path to your draft file. Relative paths are resolved from where you
run the command.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.
