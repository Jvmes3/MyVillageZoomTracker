import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from survey_core import session_info


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_json(session_info())
        except OSError:
            self.send_json(
                {"ok": False, "error": "Unable to load session details right now."},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

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
