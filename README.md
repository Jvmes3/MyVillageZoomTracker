# MyVillage Zoom Tracker

Simple survey app for STEM class attendance and participation tracking.

## What it does

- Serves a MyVillage-inspired survey page
- Collects five participation prompts
- Saves every submission to both CSV and JSONL
- Creates a new timestamped data folder each time the server starts

## Run locally

```bash
HOST=127.0.0.1 python3 server.py
```

Or just:

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

## Deploy on Render

This project is ready to deploy as a Render web service.

Important:

- Render web services must listen on `0.0.0.0`
- Render files are ephemeral by default, so attach a persistent disk if you want survey data to survive restarts and redeploys
- Set `DATA_DIR` to your disk mount path, such as `/opt/render/project/src/data`

Suggested Render settings:

- Build command: `echo "No build step needed"`
- Start command: `python3 server.py`
- Environment variable: `DATA_DIR=/opt/render/project/src/data`

If you do not attach a disk, your CSV and JSONL files can be lost on redeploy.
