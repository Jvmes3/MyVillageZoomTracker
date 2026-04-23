import csv
import json
import os
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
DATA_DIR = BASE_DIR / "data"

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


def ensure_storage() -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
            writer.writeheader()

    if not META_PATH.exists():
        session_details = {
            "created_at": datetime.now().isoformat(),
            "session_directory": str(SESSION_DIR.relative_to(BASE_DIR)),
            "csv_path": str(CSV_PATH.relative_to(BASE_DIR)),
            "jsonl_path": str(JSONL_PATH.relative_to(BASE_DIR)),
        }
        with META_PATH.open("w", encoding="utf-8") as meta_file:
            json.dump(session_details, meta_file, indent=2)


def save_submission(payload: dict) -> None:
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


class SurveyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/session":
            self.send_json(
                {
                    "session_directory": str(SESSION_DIR.relative_to(BASE_DIR)),
                    "csv_path": str(CSV_PATH.relative_to(BASE_DIR)),
                    "jsonl_path": str(JSONL_PATH.relative_to(BASE_DIR)),
                }
            )
            return

        if parsed.path == "/":
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/surveys":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_json({"ok": False, "error": "Invalid JSON payload"}, status=HTTPStatus.BAD_REQUEST)
            return

        is_valid, error = validate_payload(payload)
        if not is_valid:
            self.send_json({"ok": False, "error": error}, status=HTTPStatus.BAD_REQUEST)
            return

        save_submission(payload)
        self.send_json({"ok": True})

    def log_message(self, format, *args):
        return

    def send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def run_server():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ReusableThreadingHTTPServer((host, port), SurveyHandler)
    ensure_storage()

    print(f"MyVillage Zoom Tracker running at http://{host}:{port}")
    print(f"Session data directory: {SESSION_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
