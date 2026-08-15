import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ========== SOZLAMALAR ==========
BOT_TOKEN = "8786129118:AAFTOi93qcIhtuHiS3gdE2PPoPcOHP2dvmA"  # @BotFather dan oling
GROUP_ID = -1003917578629  # Guruh ID si
ADMIN_IDS = [5620975465]  # Sizning ID

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# ========== MA'LUMOTLAR BAZASI ==========
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
    tahrir_qadam = State()

# ========== YORDAMCHI FUNKSIYA ==========
def elon_matni(data):
    return f"""📋 <b>E'loningizni tekshiring:</b>

🏠 Turi: {data.get('turi', '❌')}
🛏 Xonalar: {data.get('xonalar', '❌')}
📐 Metr: {data.get('metr', '❌')} m²
🔧 Holat: {data.get('holat', '❌')}
💰 Savdo: {data.get('savdo', '❌')}
📎 Qo'shimcha: {data.get('qoshimcha', 'Yoq')}
📞 Telefon: {data.get('telefon', '❌')}
"""

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== /START ==========
@dp.message(lambda msg: msg.text == "/start")
async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 E'lon berish", callback_data="new_elon")],
        [InlineKeyboardButton(text="📋 Mening e'lonlarim", callback_data="my_elons")],
        [InlineKeyboardButton(text="📞 Admin bilan bog'lanish", callback_data="contact_admin")]
    ])
    if is_admin(msg.from_user.id):
        kb.inline_keyboard.append([InlineKeyboardButton(text="⚙️ Admin panel", callback_data="admin_panel")])
    await msg.answer("🏘 Xush kelibsiz! Quyidagilardan birini tanlang:", reply_markup=kb)

# ========== 1-QADAM ==========
@dp.callback_query(lambda c: c.data == "new_elon")
async def new_elon(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Ko'p qavatli", callback_data="turi_kop"),
         InlineKeyboardButton(text="🏡 Hovli", callback_data="turi_hovli")]
    ])
    await callback.message.delete()
    await callback.message.answer("1/8: Uyingiz qanday turdagi?", reply_markup=kb)
    await state.set_state(ElonState.turi)

@dp.callback_query(lambda c: c.data.startswith("turi_"), ElonState.turi)
async def turi_olish(callback: types.CallbackQuery, state: FSMContext):
    tur = "Ko'p qavatli" if "kop" in callback.data else "Hovli"
    await state.update_data(turi=tur)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="xona_1"),
         InlineKeyboardButton(text="2", callback_data="xona_2"),
         InlineKeyboardButton(text="3", callback_data="xona_3")],
        [InlineKeyboardButton(text="4", callback_data="xona_4"),
         InlineKeyboardButton(text="5+", callback_data="xona_5")],
        [InlineKeyboardButton(text="✏️ O'zim yozaman", callback_data="xona_manual")]
    ])
    if tur == "Hovli":
        kb.inline_keyboard.insert(2, [
            InlineKeyboardButton(text="🏠 1 xona qilingan", callback_data="xona_1room"),
            InlineKeyboardButton(text="🏠 2 xona qilingan", callback_data="xona_2room")
        ])
    await callback.message.edit_text("2/8: Xonalar sonini tanlang:", reply_markup=kb)
    await state.set_state(ElonState.xonalar)

# ========== 2-QADAM ==========
@dp.callback_query(lambda c: c.data.startswith("xona_"), ElonState.xonalar)
async def xonalar_olish(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    if data == "xona_manual":
        await callback.message.edit_text("✏️ Xonalar sonini yozing:")
        await state.set_state(ElonState.xonalar_manual)
        return

    xona_map = {
        "xona_1": "1", "xona_2": "2", "xona_3": "3",
        "xona_4": "4", "xona_5": "5+",
        "xona_1room": "1 xona qilingan",
        "xona_2room": "2 xona qilingan"
    }
    await state.update_data(xonalar=xona_map.get(data, data))
    await callback.message.edit_text("3/8: Necha kvadrat metr?")
    await state.set_state(ElonState.metr)

@dp.message(ElonState.xonalar_manual)
async def xonalar_manual(msg: types.Message, state: FSMContext):
    await state.update_data(xonalar=msg.text)
    await msg.answer("3/8: Necha kvadrat metr?")
    await state.set_state(ElonState.metr)

@dp.message(ElonState.xonalar)
async def xonalar_text(msg: types.Message, state: FSMContext):
    await state.update_data(xonalar=msg.text)
    await msg.answer("3/8: Necha kvadrat metr?")
    await state.set_state(ElonState.metr)

# ========== 3-QADAM ==========
@dp.message(ElonState.metr)
async def metr_olish(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❌ Faqat raqam kiriting!")
        return
    await state.update_data(metr=msg.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Evro remont", callback_data="holat_evro")],
        [InlineKeyboardButton(text="👍 Yaxshi", callback_data="holat_yaxshi")],
        [InlineKeyboardButton(text="👌 O'rta", callback_data="holat_orta")],
        [InlineKeyboardButton(text="🔧 Ta'mir kerak", callback_data="holat_tamir")]
    ])
    await msg.answer("4/8: Uyning holatini tanlang:", reply_markup=kb)
    await state.set_state(ElonState.holat)

# ========== 4-QADAM ==========
@dp.callback_query(lambda c: c.data.startswith("holat_"), ElonState.holat)
async def holat_olish(callback: types.CallbackQuery, state: FSMContext):
    holat_map = {
        "evro": "✨ Evro remont",
        "yaxshi": "👍 Yaxshi",
        "orta": "👌 O'rta",
        "tamir": "🔧 Ta'mir kerak"
    }
    await state.update_data(holat=holat_map[callback.data.split("_")[1]])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Naqt", callback_data="savdo_naqt")],
        [InlineKeyboardButton(text="🏦 Ipoteka", callback_data="savdo_ipoteka")],
        [InlineKeyboardButton(text="📄 Subsidya", callback_data="savdo_subsidya")]
    ])
    await callback.message.edit_text("5/8: Savdo turini tanlang:", reply_markup=kb)
    await state.set_state(ElonState.savdo)

# ========== 5-QADAM ==========
@dp.callback_query(lambda c: c.data.startswith("savdo_"), ElonState.savdo)
async def savdo_olish(callback: types.CallbackQuery, state: FSMContext):
    savdo_map = {
        "naqt": "💰 Naqt",
        "ipoteka": "🏦 Ipoteka",
        "subsidya": "📄 Subsidya"
    }
    await state.update_data(savdo=savdo_map[callback.data.split("_")[1]])
    await callback.message.edit_text("6/8: Rasm yoki video yuboring:")
    await state.set_state(ElonState.rasm)

# ========== 6-QADAM ==========
@dp.message(ElonState.rasm)
async def rasm_olish(msg: types.Message, state: FSMContext):
    if not msg.photo and not msg.video:
        await msg.answer("❌ Rasm yoki video yuboring!")
        return
    file_id = msg.photo[-1].file_id if msg.photo else msg.video.file_id
    await state.update_data(rasm=file_id)
    await msg.answer("7/8: Qo'shimcha ma'lumotlar (ixtiyoriy, 'yoq' deb yozing o'tkazib yuborish uchun):")
    await state.set_state(ElonState.qoshimcha)

# ========== 7-QADAM ==========
@dp.message(ElonState.qoshimcha)
async def qoshimcha_olish(msg: types.Message, state: FSMContext):
    qosh = msg.text if msg.text.lower() != "yoq" else ""
    await state.update_data(qoshimcha=qosh)
    await msg.answer("8/8: Telefon raqamingizni yozing:")
    await state.set_state(ElonState.telefon)

# ========== 8-QADAM ==========
@dp.message(ElonState.telefon)
async def telefon_olish(msg: types.Message, state: FSMContext):
    await state.update_data(telefon=msg.text)
    data = await state.get_data()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ E'lonni joylashtirish", callback_data="submit_elon")],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_elon")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    await msg.answer(elon_matni(data), reply_markup=kb)

# ========== TAHRIRLASH ==========
@dp.callback_query(lambda c: c.data == "edit_elon")
async def edit_menu(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1. Uy turi", callback_data="edit_turi")],
        [InlineKeyboardButton(text="2. Xonalar", callback_data="edit_xonalar")],
        [InlineKeyboardButton(text="3. Metr", callback_data="edit_metr")],
        [InlineKeyboardButton(text="4. Holat", callback_data="edit_holat")],
        [InlineKeyboardButton(text="5. Savdo", callback_data="edit_savdo")],
        [InlineKeyboardButton(text="6. Rasm", callback_data="edit_rasm")],
        [InlineKeyboardButton(text="7. Qo'shimcha", callback_data="edit_qoshimcha")],
        [InlineKeyboardButton(text="8. Telefon", callback_data="edit_telefon")],
        [InlineKeyboardButton(text="🔙 Ortga", callback_data="back_to_check")]
    ])
    await callback.message.edit_text("Qaysi qadamni tahrirlaysiz?", reply_markup=kb)
    await state.set_state(ElonState.tahrir_qadam)

# ========== BACK TO CHECK ==========
@dp.callback_query(lambda c: c.data == "back_to_check")
async def back_to_check(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ E'lonni joylashtirish", callback_data="submit_elon")],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_elon")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])
    await callback.message.edit_text(elon_matni(data), reply_markup=kb)

# ========== ELONNI JOYLASH ==========
@dp.callback_query(lambda c: c.data == "submit_elon")
async def submit_elon(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    cur.execute("""INSERT INTO elonlar
    (user_id, turi, xonalar, metr, holat, savdo, rasm_file_id, qoshimcha, telefon)
    VALUES (?,?,?,?,?,?,?,?,?)""",
    (callback.from_user.id, data['turi'], data['xonalar'], data['metr'],
     data['holat'], data['savdo'], data.get('rasm'), data.get('qoshimcha'), data['telefon']))
    conn.commit()

    elon_matni_guruh = f"""🏡 <b>Yangi elon!</b>

🏠 Turi: {data['turi']}
🛏 Xonalar: {data['xonalar']}
📐 {data['metr']} m²
🔧 {data['holat']}
💰 {data['savdo']}
📞 {data['telefon']}
📎 {data.get('qoshimcha', '')}
"""

    try:
        if data.get('rasm'):
            await bot.send_photo(chat_id=GROUP_ID, photo=data['rasm'], caption=elon_matni_guruh, parse_mode="HTML")
        else:
            await bot.send_message(chat_id=GROUP_ID, text=elon_matni_guruh, parse_mode="HTML")
        await callback.message.edit_text("✅ E'loningiz guruhga joylandi!")
    except Exception as e:
        await callback.message.edit_text(f"⚠️ Xatolik: {e}\n\nGuruh ID sini tekshiring!")

    await state.clear()

# ========== BEKOR QILISH ==========
@dp.callback_query(lambda c: c.data == "cancel")
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await start(callback.message, state)

# ========== MENING ELONLARIM ==========
@dp.callback_query(lambda c: c.data == "my_elons")
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
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Ortga", callback_data="back_main")]])
    await callback.message.edit_text(matn, reply_markup=kb, parse_mode="HTML")

# ========== ADMIN BILAN BOG'LANISH ==========
@dp.callback_query(lambda c: c.data == "contact_admin")
async def contact_admin(callback: types.CallbackQuery):
    await callback.answer("Admin: @elmurodov7777", show_alert=True)

# ========== BACK MAIN ==========
@dp.callback_query(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 E'lon berish", callback_data="new_elon")],
        [InlineKeyboardButton(text="📋 Mening e'lonlarim", callback_data="my_elons")],
        [InlineKeyboardButton(text="📞 Admin bilan bog'lanish", callback_data="contact_admin")]
    ])
    if is_admin(callback.from_user.id):
        kb.inline_keyboard.append([InlineKeyboardButton(text="⚙️ Admin panel", callback_data="admin_panel")])
    await callback.message.edit_text("🏘 Xush kelibsiz! Quyidagilardan birini tanlang:", reply_markup=kb)

# ========== ADMIN PANEL ==========
@dp.callback_query(lambda c: c.data == "admin_panel" and is_admin(c.from_user.id))
async def admin_panel(callback: types.CallbackQuery):
    cur.execute("SELECT COUNT(*) FROM elonlar")
    total = cur.fetchone()[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Barcha elonlar", callback_data="admin_all_elons")],
        [InlineKeyboardButton(text="🔙 Chiqish", callback_data="back_main")]
    ])
    await callback.message.edit_text(f"🔐 Admin panel\n\n📊 Jami elonlar: {total}", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "admin_stats" and is_admin(c.from_user.id))
async def admin_stats(callback: types.CallbackQuery):
    cur.execute("SELECT turi, COUNT(*) FROM elonlar GROUP BY turi")
    stats = cur.fetchall()
    matn = "📊 <b>Statistika:</b>\n\n"
    for tur, son in stats:
        matn += f"🏠 {tur}: {son} ta\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_panel")]])
    await callback.message.edit_text(matn, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "admin_all_elons" and is_admin(c.from_user.id))
async def admin_all_elons(callback: types.CallbackQuery):
    cur.execute("SELECT id, turi, xonalar, metr, telefon FROM elonlar ORDER BY id DESC LIMIT 10")
    elons = cur.fetchall()
    if not elons:
        await callback.message.edit_text("❌ Hozircha elonlar yo'q")
        return
    matn = "📋 <b>So'nggi elonlar:</b>\n\n"
    for elon in elons:
        matn += f"#{elon[0]} | {elon[1]} | {elon[2]} xona | {elon[3]} m² | {elon[4]}\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_panel")]])
    await callback.message.edit_text(matn, reply_markup=kb, parse_mode="HTML")

# ========== ASOSIY ==========
async def main():
    print("🤖 Bot ishga tushdi!")
    print(f"👤 Admin ID: {ADMIN_IDS}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
