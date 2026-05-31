import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from survey_core import save_submission, validate_payload


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json({"ok": False, "error": "Invalid JSON payload"}, HTTPStatus.BAD_REQUEST)
            return

        is_valid, error = validate_payload(payload)
        if not is_valid:
            self.send_json({"ok": False, "error": error}, HTTPStatus.BAD_REQUEST)
            return

        try:
            save_submission(payload)
        except OSError:
            self.send_json(
                {"ok": False, "error": "Unable to save your response right now."},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        self.send_json({"ok": True})

    def do_GET(self):
        self.send_json({"ok": False, "error": "Method not allowed"}, HTTPStatus.METHOD_NOT_ALLOWED)

    def send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return
