from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup
import asyncio
import sqlite3
import random

TOKEN = "8456071403:AAGLhUJfuVV5gB8V-akAawWd8xNrcO_e0yU"
ADMIN_ID = 5620975465

bot = Bot(token=TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    uc INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY,
    count INTEGER
)
""")

cursor.execute("INSERT OR IGNORE INTO stats (id, count) VALUES (1, 0)")
conn.commit()

def get_balance(uid):
    cursor.execute("SELECT balance FROM users WHERE id=?", (uid,))
    res = cursor.fetchone()
    return res[0] if res else 0

def add_balance(uid, amount):
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, uid))
    conn.commit()

def minus_balance(uid, amount):
    cursor.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, uid))
    conn.commit()

def add_uc(uid, amount):
    cursor.execute("UPDATE users SET uc = uc + ? WHERE id=?", (amount, uid))
    conn.commit()

def get_uc(uid):
    cursor.execute("SELECT uc FROM users WHERE id=?", (uid,))
    res = cursor.fetchone()
    return res[0] if res else 0

def reset_uc(uid):
    cursor.execute("UPDATE users SET uc = 0 WHERE id=?", (uid,))
    conn.commit()

def add_global():
    cursor.execute("SELECT count FROM stats WHERE id=1")
    count = cursor.fetchone()[0] + 1
    cursor.execute("UPDATE stats SET count=? WHERE id=1", (count,))
    conn.commit()
    return count

waiting = {}

@dp.message(commands=['start'])
async def start(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎮 O‘YIN", "💰 BALANS")
    kb.add("🎁 YUTUQ")

    add_balance(msg.from_user.id, 0)

    await msg.answer(
        f"👋 Xush kelibsiz!\n\n"
        f"💰 Balans: {get_balance(msg.from_user.id)} so‘m",
        reply_markup=kb
    )

@dp.message(lambda msg: msg.text == "💰 BALANS")
async def bal(msg: types.Message):
    await msg.answer(f"💰 Balans: {get_balance(msg.from_user.id)} so‘m")

@dp.message(lambda msg: msg.text == "🎮 O‘YIN")
async def game(msg: types.Message):
    if get_balance(msg.from_user.id) < 3000:
        return await msg.answer("❌ Balans yetarli emas")

    minus_balance(msg.from_user.id, 3000)

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔴 ?", "🔵 ?")

    await msg.answer("Tanlang:", reply_markup=kb)

@dp.message(lambda msg: msg.text in ["🔴 ?", "🔵 ?"])
async def result(msg: types.Message):
    count = add_global()

    if count % 5 == 0:
        add_uc(msg.from_user.id, 60)
        total = get_uc(msg.from_user.id)

        await msg.answer(
            f"🎉 TABRIKLAYMIZ!\n\n"
            f"🎁 Siz 60 UC yutdingiz!\n"
            f"💼 Jami: {total} UC\n\n"
            f"🎁 Yig‘ish uchun: 🎁 YUTUQ"
        )
    else:
        await msg.answer(random.choice([
            "❌ Bu safar omad kelmadi",
            "😔 Yutuq yo‘q",
            "🎯 Yana urinib ko‘ring"
        ]))

@dp.message(lambda msg: msg.text == "🎁 YUTUQ")
async def get_reward(msg: types.Message):
    total = get_uc(msg.from_user.id)

    if total == 0:
        return await msg.answer("❌ Sizda yutuq yo‘q")

    waiting[msg.from_user.id] = total
    await msg.answer(f"🎁 {total} UC bor\n📩 ID yuboring")

@dp.message()
async def get_id(msg: types.Message):
    if msg.from_user.id in waiting:
        total = waiting[msg.from_user.id]

        await bot.send_message(
            ADMIN_ID,
            f"🎉 YUTGAN USER\n\nID: {msg.text}\nUC: {total}"
        )

        reset_uc(msg.from_user.id)
        del waiting[msg.from_user.id]

        await msg.answer("✅ Yuborildi")

@dp.message(commands=['add'])
async def add(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    try:
        _, uid, amount = msg.text.split()
        add_balance(int(uid), int(amount))
        await msg.answer("✅ Qo‘shildi")
    except:
        await msg.answer("Format: /add id summa")

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
