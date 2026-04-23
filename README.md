# MyVillage Zoom Tracker

Simple survey app for STEM class attendance and participation tracking.

## What it does

- Serves a MyVillage-inspired survey page
- Collects five participation prompts
- Saves every submission to both CSV and JSONL
- Creates a new timestamped data folder each time the server starts

## Run locally

```bash
python3 server.py
```

Then open `http://127.0.0.1:8000`.

## Data output

Each app run creates a folder like:

```text
data/session-20260423-171500/
```

Inside that folder:

- `responses.csv`
- `responses.jsonl`
- `session.json`

This makes it easy to review survey data in Excel or feed the JSONL into later model workflows.
