import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

# ========== SOZLAMALAR ==========
BOT_TOKEN = "8786129118:AAFTOi93qcIhtuHiS3gdE2PPoPcOHP2dvmA"
GROUP_ID = -1003917578629
ADMIN_IDS = [5620975465]

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ========== DB ==========
conn = sqlite3.connect("elonlar.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS elonlar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    turi TEXT,
    xonalar TEXT,
    metr TEXT,
    holat TEXT,
    savdo TEXT,
    rasm_file_id TEXT,
    qoshimcha TEXT,
    telefon TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ========== HOLATLAR ==========
class ElonState(StatesGroup):
    turi = State()
    xonalar = State()
    xonalar_manual = State()
    metr = State()
    holat = State()
    savdo = State()
    rasm = State()
    qoshimcha = State()
    telefon = State()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def elon_matni(data):
    return (
        f"📋 <b>E'loningizni tekshiring:</b>\n\n"
        f"🏠 Turi: {data.get('turi', '❌')}\n"
        f"🛏 Xonalar: {data.get('xonalar', '❌')}\n"
        f"📐 Metr: {data.get('metr', '❌')} m²\n"
        f"🔧 Holat: {data.get('holat', '❌')}\n"
        f"💰 Savdo: {data.get('savdo', '❌')}\n"
        f"📎 Qo'shimcha: {data.get('qoshimcha') or 'Yoq'}\n"
        f"📞 Telefon: {data.get('telefon', '❌')}"
    )

def main_kb(user_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🏠 E'lon berish", callback_data="new_elon"))
    kb.add(types.InlineKeyboardButton("📋 Mening e'lonlarim", callback_data="my_elons"))
    kb.add(types.InlineKeyboardButton("📞 Admin bilan bog'lanish", callback_data="contact_admin"))
    if is_admin(user_id):
        kb.add(types.InlineKeyboardButton("⚙️ Admin panel", callback_data="admin_panel"))
    return kb

# ========== /START ==========
@dp.message_handler(commands=["start"], state="*")
async def start(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("🏘 Xush kelibsiz! Quyidagilardan birini tanlang:", reply_markup=main_kb(msg.from_user.id))

# ========== 1-QADAM: TURI ==========
@dp.callback_query_handler(lambda c: c.data == "new_elon", state="*")
async def new_elon(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("🏢 Ko'p qavatli", callback_data="turi_kop"),
        types.InlineKeyboardButton("🏡 Hovli", callback_data="turi_hovli")
    )
    await callback.message.edit_text("1/8: Uyingiz qanday turdagi?", reply_markup=kb)
    await ElonState.turi.set()

@dp.callback_query_handler(lambda c: c.data.startswith("turi_"), state=ElonState.turi)
async def turi_olish(callback: types.CallbackQuery, state: FSMContext):
    tur = "Ko'p qavatli" if "kop" in callback.data else "Hovli"
    await state.update_data(turi=tur)

    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("1", callback_data="xona_1"),
        types.InlineKeyboardButton("2", callback_data="xona_2"),
        types.InlineKeyboardButton("3", callback_data="xona_3")
    )
    kb.row(
        types.InlineKeyboardButton("4", callback_data="xona_4"),
        types.InlineKeyboardButton("5+", callback_data="xona_5")
    )
    if tur == "Hovli":
        kb.row(
            types.InlineKeyboardButton("🏠 1 xona qilingan", callback_data="xona_1room"),
            types.InlineKeyboardButton("🏠 2 xona qilingan", callback_data="xona_2room")
        )
    kb.add(types.InlineKeyboardButton("✏️ O'zim yozaman", callback_data="xona_manual"))
    await callback.message.edit_text("2/8: Xonalar sonini tanlang:", reply_markup=kb)
    await ElonState.xonalar.set()

# ========== 2-QADAM: XONALAR ==========
@dp.callback_query_handler(lambda c: c.data.startswith("xona_"), state=ElonState.xonalar)
async def xonalar_olish(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "xona_manual":
        await callback.message.edit_text("✏️ Xonalar sonini yozing:")
        await ElonState.xonalar_manual.set()
        return
    xona_map = {
        "xona_1": "1", "xona_2": "2", "xona_3": "3",
        "xona_4": "4", "xona_5": "5+",
        "xona_1room": "1 xona qilingan",
        "xona_2room": "2 xona qilingan"
    }
    await state.update_data(xonalar=xona_map.get(callback.data, callback.data))
    await callback.message.edit_text("3/8: Necha kvadrat metr?")
    await ElonState.metr.set()

@dp.message_handler(state=ElonState.xonalar_manual)
async def xonalar_manual(msg: types.Message, state: FSMContext):
    await state.update_data(xonalar=msg.text)
    await msg.answer("3/8: Necha kvadrat metr?")
    await ElonState.metr.set()

# ========== 3-QADAM: METR ==========
@dp.message_handler(state=ElonState.metr)
async def metr_olish(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Faqat raqam kiriting!")
        return
    await state.update_data(metr=msg.text)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✨ Evro remont", callback_data="holat_evro"))
    kb.add(types.InlineKeyboardButton("👍 Yaxshi", callback_data="holat_yaxshi"))
    kb.add(types.InlineKeyboardButton("👌 O'rta", callback_data="holat_orta"))
    kb.add(types.InlineKeyboardButton("🔧 Ta'mir kerak", callback_data="holat_tamir"))
    await msg.answer("4/8: Uyning holatini tanlang:", reply_markup=kb)
    await ElonState.holat.set()

# ========== 4-QADAM: HOLAT ==========
@dp.callback_query_handler(lambda c: c.data.startswith("holat_"), state=ElonState.holat)
async def holat_olish(callback: types.CallbackQuery, state: FSMContext):
    holat_map = {
        "holat_evro": "✨ Evro remont",
        "holat_yaxshi": "👍 Yaxshi",
        "holat_orta": "👌 O'rta",
        "holat_tamir": "🔧 Ta'mir kerak"
    }
    await state.update_data(holat=holat_map[callback.data])
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💰 Naqt", callback_data="savdo_naqt"))
    kb.add(types.InlineKeyboardButton("🏦 Ipoteka", callback_data="savdo_ipoteka"))
    kb.add(types.InlineKeyboardButton("📄 Subsidya", callback_data="savdo_subsidya"))
    await callback.message.edit_text("5/8: Savdo turini tanlang:", reply_markup=kb)
    await ElonState.savdo.set()

# ========== 5-QADAM: SAVDO ==========
@dp.callback_query_handler(lambda c: c.data.startswith("savdo_"), state=ElonState.savdo)
async def savdo_olish(callback: types.CallbackQuery, state: FSMContext):
    savdo_map = {
        "savdo_naqt": "💰 Naqt",
        "savdo_ipoteka": "🏦 Ipoteka",
        "savdo_subsidya": "📄 Subsidya"
    }
    await state.update_data(savdo=savdo_map[callback.data])
    await callback.message.edit_text("6/8: Rasm yoki video yuboring:")
    await ElonState.rasm.set()

# ========== 6-QADAM: RASM ==========
@dp.message_handler(content_types=["photo", "video"], state=ElonState.rasm)
async def rasm_olish(msg: types.Message, state: FSMContext):
    file_id = msg.photo[-1].file_id if msg.photo else msg.video.file_id
    media_type = "photo" if msg.photo else "video"
    await state.update_data(rasm=file_id, media_type=media_type)
    await msg.answer("7/8: Qo'shimcha ma'lumotlar (ixtiyoriy, 'yoq' deb yozing o'tkazib yuborish uchun):")
    await ElonState.qoshimcha.set()

@dp.message_handler(state=ElonState.rasm)
async def rasm_xato(msg: types.Message):
    await msg.answer("❌ Rasm yoki video yuboring!")

# ========== 7-QADAM: QOSHIMCHA ==========
@dp.message_handler(state=ElonState.qoshimcha)
async def qoshimcha_olish(msg: types.Message, state: FSMContext):
    qosh = "" if msg.text.lower() == "yoq" else msg.text
    await state.update_data(qoshimcha=qosh)
    await msg.answer("8/8: Telefon raqamingizni yozing:")
    await ElonState.telefon.set()

# ========== 8-QADAM: TELEFON ==========
@dp.message_handler(state=ElonState.telefon)
async def telefon_olish(msg: types.Message, state: FSMContext):
    await state.update_data(telefon=msg.text)
    data = await state.get_data()
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ E'lonni joylashtirish", callback_data="submit_elon"))
    kb.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    await msg.answer(elon_matni(data), reply_markup=kb)

# ========== JOYLASH ==========
@dp.callback_query_handler(lambda c: c.data == "submit_elon", state=ElonState.telefon)
async def submit_elon(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    cur.execute("""INSERT INTO elonlar
    (user_id, turi, xonalar, metr, holat, savdo, rasm_file_id, qoshimcha, telefon)
    VALUES (?,?,?,?,?,?,?,?,?)""",
    (callback.from_user.id, data.get('turi'), data.get('xonalar'), data.get('metr'),
     data.get('holat'), data.get('savdo'), data.get('rasm'), data.get('qoshimcha'), data.get('telefon')))
    conn.commit()

    guruh_matni = (
        f"🏡 <b>Yangi e'lon!</b>\n\n"
        f"🏠 Turi: {data.get('turi')}\n"
        f"🛏 Xonalar: {data.get('xonalar')}\n"
        f"📐 {data.get('metr')} m²\n"
        f"🔧 {data.get('holat')}\n"
        f"💰 {data.get('savdo')}\n"
        f"📞 {data.get('telefon')}\n"
        f"📎 {data.get('qoshimcha') or ''}"
    )

    try:
        rasm = data.get('rasm')
        media_type = data.get('media_type', 'photo')
        if rasm:
            if media_type == "photo":
                await bot.send_photo(GROUP_ID, rasm, caption=guruh_matni)
            else:
                await bot.send_video(GROUP_ID, rasm, caption=guruh_matni)
        else:
            await bot.send_message(GROUP_ID, guruh_matni)
        await callback.message.edit_text("✅ E'loningiz guruhga joylandi!")
    except Exception as e:
        await callback.message.edit_text(f"⚠️ Xatolik: {e}")

    await state.finish()

# ========== BEKOR ==========
@dp.callback_query_handler(lambda c: c.data == "cancel", state="*")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.message.answer("🏘 Bosh menyu:", reply_markup=main_kb(callback.from_user.id))

# ========== MENING ELONLARIM ==========
@dp.callback_query_handler(lambda c: c.data == "my_elons", state="*")
async def my_elons(callback: types.CallbackQuery):
    cur.execute("SELECT id, turi, xonalar, metr, telefon FROM elonlar WHERE user_id=? ORDER BY id DESC LIMIT 5",
                (callback.from_user.id,))
    elons = cur.fetchall()
    if not elons:
        await callback.answer("❌ Sizda hali e'lonlar yo'q", show_alert=True)
        return
    matn = "📋 <b>Sizning e'lonlaringiz:</b>\n\n"
    for e in elons:
        matn += f"#{e[0]} | {e[1]} | {e[2]} xona | {e[3]} m² | {e[4]}\n"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="back_main"))
    await callback.message.edit_text(matn, reply_markup=kb)

# ========== ADMIN BILAN ==========
@dp.callback_query_handler(lambda c: c.data == "contact_admin", state="*")
async def contact_admin(callback: types.CallbackQuery):
    await callback.answer("Admin: @elmurodov7777", show_alert=True)

# ========== BACK MAIN ==========
@dp.callback_query_handler(lambda c: c.data == "back_main", state="*")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("🏘 Bosh menyu:", reply_markup=main_kb(callback.from_user.id))

# ========== ADMIN PANEL ==========
@dp.callback_query_handler(lambda c: c.data == "admin_panel", state="*")
async def admin_panel(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cur.execute("SELECT COUNT(*) FROM elonlar")
    total = cur.fetchone()[0]
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📊 Statistika", callback_data="admin_stats"))
    kb.add(types.InlineKeyboardButton("📋 Barcha e'lonlar", callback_data="admin_all_elons"))
    kb.add(types.InlineKeyboardButton("🔙 Chiqish", callback_data="back_main"))
    await callback.message.edit_text(f"🔐 Admin panel\n\n📊 Jami e'lonlar: {total}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "admin_stats", state="*")
async def admin_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cur.execute("SELECT turi, COUNT(*) FROM elonlar GROUP BY turi")
    stats = cur.fetchall()
    matn = "📊 <b>Statistika:</b>\n\n"
    for tur, son in stats:
        matn += f"🏠 {tur}: {son} ta\n"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="admin_panel"))
    await callback.message.edit_text(matn, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "admin_all_elons", state="*")
async def admin_all_elons(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cur.execute("SELECT id, turi, xonalar, metr, telefon FROM elonlar ORDER BY id DESC LIMIT 10")
    elons = cur.fetchall()
    if not elons:
        await callback.message.edit_text("❌ Hozircha e'lonlar yo'q")
        return
    matn = "📋 <b>So'nggi e'lonlar:</b>\n\n"
    for e in elons:
        matn += f"#{e[0]} | {e[1]} | {e[2]} xona | {e[3]} m² | {e[4]}\n"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="admin_panel"))
    await callback.message.edit_text(matn, reply_markup=kb)

# ========== MAIN ==========
if __name__ == "__main__":
    print("🤖 Bot ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
