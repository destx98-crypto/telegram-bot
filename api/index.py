from http.server import BaseHTTPRequestHandler
import json
import requests

TOKEN = "TOKENINGNI_QOY"

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
                send(chat_id, f"👋 Xush kelibsiz!\n💰 Balans: {balances[chat_id]} so‘m\n\n🎮 O‘yin uchun 🎮 yozing")

            # ADMIN ADD
            elif text.startswith("/add"):
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
                send(chat_id, f"💰 Sizning balans: {balances.get(chat_id,0)} so‘m")

            # O‘YIN BOSHLASH
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
                    send(chat_id, "🎉 TABRIKLAYMAN! Siz 60 UC yutdingiz!\n\n📩 ID yuboring")
                else:
                    send(chat_id, "❌ Yutqazdingiz\nYana urinib ko‘ring!")

        self.send_response(200)
        self.end_headers()
