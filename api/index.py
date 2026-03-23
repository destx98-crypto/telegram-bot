from http.server import BaseHTTPRequestHandler
import json
import requests

TOKEN = "8456071403:AAGLhUJfuVV5gB8V-akAawWd8xNrcO_e0yU"
ADMIN_ID = 5620975465

global_count = 0
balances = {}

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        global global_count, balances

        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)
        update = json.loads(body)

        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            # START
            if text == "/start":
                balances.setdefault(chat_id, 0)
                send(chat_id,
                     f"👋 Xush kelibsiz!\n\n"
                     f"💰 Balans: {balances[chat_id]} so‘m\n\n"
                     f"🎮 O‘ynash uchun 🎮 yozing")

            # ADMIN ADD
            elif text.startswith("/add"):
                if chat_id != ADMIN_ID:
                    return

                try:
                    _, uid, amount = text.split()
                    uid = int(uid)
                    amount = int(amount)
                    balances[uid] = balances.get(uid, 0) + amount
                    send(chat_id, "✅ Pul qo‘shildi")
                except:
                    send(chat_id, "Format: /add id summa")

            # BALANS
            elif text.lower() == "balans":
                send(chat_id, f"💰 Balans: {balances.get(chat_id,0)} so‘m")

            # O‘YIN
            elif text == "🎮":
                if balances.get(chat_id, 0) < 3000:
                    send(chat_id, "❌ Balans yetarli emas")
                else:
                    balances[chat_id] -= 3000
                    send(chat_id, "Tanlang:\n🔴 yoki 🔵")

            # TANLASH
            elif text in ["🔴", "🔵"]:
                global_count += 1

                if global_count % 5 == 0:
                    send(chat_id,
                         "🎉 TABRIKLAYMIZ!\n\n"
                         "🎁 Siz 60 UC yutdingiz!\n\n"
                         "📩 ID yuboring")
                else:
                    send(chat_id,
                         "❌ Yutuq yo‘q\n\n"
                         "🔁 Yana urinib ko‘ring")

        self.send_response(200)
        self.end_headers()
