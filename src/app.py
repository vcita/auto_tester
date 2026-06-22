"""
Minimal HTTP server for k8s liveness/readiness probes.
Exposes GET /health/check.json → 200 {"status": "healthy"}.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health/check.json":
            body = json.dumps({"status": "healthy"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # silence access logs


def run(port: int = 8080):
    server = HTTPServer(("", port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
