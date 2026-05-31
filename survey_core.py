import csv
import json
import os
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = "/tmp/myvillage-zoom-tracker-data" if os.environ.get("VERCEL") else str(BASE_DIR / "data")
DATA_DIR = Path(os.environ.get("DATA_DIR", DEFAULT_DATA_DIR))

SESSION_STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
SESSION_DIR = DATA_DIR / f"session-{SESSION_STAMP}"
CSV_PATH = SESSION_DIR / "responses.csv"
JSONL_PATH = SESSION_DIR / "responses.jsonl"
META_PATH = SESSION_DIR / "session.json"

FIELDNAMES = [
    "submitted_at",
    "student_name",
    "student_branch",
    "presenting_team",
    "learned_something_new",
    "new_learning_details",
    "current_focus",
]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def ensure_storage() -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
            writer.writeheader()

    if not META_PATH.exists():
        session_details = {
            "created_at": datetime.now().isoformat(),
            "session_directory": display_path(SESSION_DIR),
            "csv_path": display_path(CSV_PATH),
            "jsonl_path": display_path(JSONL_PATH),
        }
        with META_PATH.open("w", encoding="utf-8") as meta_file:
            json.dump(session_details, meta_file, indent=2)


def save_submission(payload: dict) -> None:
    ensure_storage()

    record = {
        "submitted_at": datetime.now().isoformat(),
        "student_name": payload["student_name"].strip(),
        "student_branch": payload["student_branch"].strip(),
        "presenting_team": payload["presenting_team"].strip(),
        "learned_something_new": payload["learned_something_new"].strip(),
        "new_learning_details": payload["new_learning_details"].strip(),
        "current_focus": payload["current_focus"].strip(),
    }

    with CSV_PATH.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writerow(record)

    with JSONL_PATH.open("a", encoding="utf-8") as jsonl_file:
        jsonl_file.write(json.dumps(record) + "\n")


def validate_payload(payload: dict) -> tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "Invalid JSON payload"

    required_fields = [
        "student_name",
        "student_branch",
        "presenting_team",
        "learned_something_new",
        "new_learning_details",
        "current_focus",
    ]
    missing = [field for field in required_fields if not str(payload.get(field, "")).strip()]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    allowed_branches = {"AI/Dev team", "Graphic design", "Game Design"}
    allowed_yes_no = {"Yes", "No"}

    if payload["student_branch"] not in allowed_branches:
        return False, "Invalid student branch"
    if payload["presenting_team"] not in allowed_branches:
        return False, "Invalid presenting team"
    if payload["learned_something_new"] not in allowed_yes_no:
        return False, "Invalid learning response"

    return True, ""


def session_info() -> dict:
    ensure_storage()
    return {
        "session_directory": display_path(SESSION_DIR),
        "csv_path": display_path(CSV_PATH),
        "jsonl_path": display_path(JSONL_PATH),
    }
