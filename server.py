import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from survey_core import ensure_storage, save_submission, session_info, validate_payload

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"


class SurveyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/session":
            self.send_json(session_info())
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
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ReusableThreadingHTTPServer((host, port), SurveyHandler)
    ensure_storage()

    print(f"MyVillage Zoom Tracker running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
