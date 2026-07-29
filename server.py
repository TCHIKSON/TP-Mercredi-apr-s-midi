

import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST = "0.0.0.0"
PORT = 8080

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT = 120  # secondes, un modele local peut etre lent selon le hardware


def ask_ollama(question: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": question,
        "stream": False,
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT) as response:
        body = json.loads(response.read().decode("utf-8"))

    return body.get("response", "").strip()


class AskHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_text(self, status: int, text: str) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path != "/ask":
            self._send_text(404, "Not found. Utiliser /ask?question=...")
            return

        params = parse_qs(parsed.query, keep_blank_values=True)
        question = params.get("question", [""])[0]

        if not question.strip():
            self._send_text(400, "Parametre 'question' manquant ou vide.")
            return

        try:
            answer = ask_ollama(question)
        except urllib.error.URLError:
            self._send_text(502, "Impossible de contacter Ollama (verifier qu'il tourne sur le port 11434).")
            return
        except TimeoutError:
            self._send_text(504, "Timeout: Ollama a mis trop de temps a repondre.")
            return

        self._send_text(200, answer)

    def log_message(self, format: str, *args) -> None:
        print("[%s] %s" % (self.address_string(), format % args))


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AskHandler)
    print(f"API REST disponible sur http://localhost:{PORT}/ask?question=...")
    print(f"Modele Ollama utilise: {OLLAMA_MODEL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArret du serveur.")
        server.shutdown()


if __name__ == "__main__":
    main()
