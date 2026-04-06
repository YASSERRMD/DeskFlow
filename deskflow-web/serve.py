#!/usr/bin/env python3
import http.server, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        super().end_headers()
    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
print(f"Serving deskflow-web on http://0.0.0.0:{port}", flush=True)
http.server.HTTPServer(("0.0.0.0", port), Handler).serve_forever()
