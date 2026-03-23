from http.server import BaseHTTPRequestHandler
import json
import requests

TOKEN = "8456071403:AAGLhUJfuVV5gB8V-akAawWd8xNrcO_e0yU"

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)
        update = json.loads(body)

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")

            if text == "/start":
                send(chat_id, "🔥 Bot ishladi!")

        self.send_response(200)
        self.end_headers()
