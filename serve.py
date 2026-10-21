"""Local preview: serves site/ and maps /data.json to the repo's data.json.

Run:  python serve.py   then open http://localhost:8099
"""
import http.server
import socketserver
from functools import partial
from pathlib import Path

ROOT = Path(__file__).parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def translate_path(self, path):
        if path.split("?")[0] == "/data.json":
            return str(ROOT / "data.json")
        return super().translate_path(path)


socketserver.ThreadingTCPServer.allow_reuse_address = True


if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("127.0.0.1", 8099), partial(Handler, directory=str(ROOT / "site"))) as s:
        print("http://localhost:8099  (Ctrl+C to stop)")
        s.serve_forever()
