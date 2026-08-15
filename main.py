import asyncio
import sqlite3
import logging
from datetime import datetime, timedelta
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
BOT_USERNAME = "@Zarafshonuylar_24_bot"

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
    manzil TEXT,
    xonalar TEXT,
    metr TEXT,
    holat TEXT,
    savdo TEXT,
    rasm_file_id TEXT,
    media_type TEXT,
    qoshimcha TEXT,
    narx TEXT,
    telefon TEXT,
    message_id INTEGER,
    last_repost TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ========== HOLATLAR ==========
class ElonState(StatesGroup):
    turi = State()
    manzil = State()
    xonalar = State()
    xonalar_manual = State()
    metr = State()
    holat = State()
    savdo = State()
    rasm = State()
    qoshimcha = State()
    narx = State()
    telefon = State()

class TahrirState(StatesGroup):
    maydon = State()
    qiymat = State()
    elon_id = State()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def elon_matni_tekshir(data):
    return (
        f"📋 <b>E'loningizni tekshiring:</b>\n\n"
        f"🏠 Turi: {data.get('turi', '❌')}\n"
        f"📍 Manzil: {data.get('manzil', '❌')}\n"
        f"🛏 Xonalar: {data.get('xonalar', '❌')}\n"
        f"📐 Metr: {data.get('metr', '❌')} m²\n"
        f"🔧 Holat: {data.get('holat', '❌')}\n"
        f"💰 Savdo: {data.get('savdo', '❌')}\n"
        f"💵 Narx: {data.get('narx', '❌')}\n"
        f"📎 Qo'shimcha: {data.get('qoshimcha') or 'Yoq'}\n"
        f"📞 Telefon: {data.get('telefon', '❌')}"
    )

def elon_matni_guruh(data, user_id=None):
    return (
        f"🏡 <b>Uy sotiladi!</b>\n\n"
        f"🏠 Turi: {data.get('turi')}\n"
        f"📍 Manzil: {data.get('manzil')}\n"
        f"🛏 Xonalar: {data.get('xonalar')}\n"
        f"📐 {data.get('metr')} m²\n"
        f"🔧 {data.get('holat')}\n"
        f"💰 {data.get('savdo')}\n"
        f"💵 Narx: {data.get('narx')}\n"
        f"📞 {data.get('telefon')}\n"
        f"📎 {data.get('qoshimcha') or ''}\n\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"📢 E'lon berish uchun {BOT_USERNAME} ga murojaat qiling\n"
        f"💰 E'lon berish — TEKIN!"
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
    await callback.message.edit_text("1/10: Uyingiz qanday turdagi?", reply_markup=kb)
    await ElonState.turi.set()

@dp.callback_query_handler(lambda c: c.data.startswith("turi_"), state=ElonState.turi)
async def turi_olish(callback: types.CallbackQuery, state: FSMContext):
    tur = "Ko'p qavatli" if "kop" in callback.data else "Hovli"
    await state.update_data(turi=tur)
    await callback.message.edit_text("2/10: Uyingiz manzilini yozing:\n(Shahar, tuman, ko'cha)")
    await ElonState.manzil.set()

# ========== 2-QADAM: MANZIL ==========
@dp.message_handler(state=ElonState.manzil)
async def manzil_olish(msg: types.Message, state: FSMContext):
    await state.update_data(manzil=msg.text)
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
    data = await state.get_data()
    if data.get('turi') == "Hovli":
        kb.row(
            types.InlineKeyboardButton("🏠 1 xona qilingan", callback_data="xona_1room"),
            types.InlineKeyboardButton("🏠 2 xona qilingan", callback_data="xona_2room")
        )
    kb.add(types.InlineKeyboardButton("✏️ O'zim yozaman", callback_data="xona_manual"))
    await msg.answer("3/10: Xonalar sonini tanlang:", reply_markup=kb)
    await ElonState.xonalar.set()

# ========== 3-QADAM: XONALAR ==========
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
    await callback.message.edit_text("4/10: Necha kvadrat metr?")
    await ElonState.metr.set()

@dp.message_handler(state=ElonState.xonalar_manual)
async def xonalar_manual(msg: types.Message, state: FSMContext):
    await state.update_data(xonalar=msg.text)
    await msg.answer("4/10: Necha kvadrat metr?")
    await ElonState.metr.set()

# ========== 4-QADAM: METR ==========
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
    await msg.answer("5/10: Uyning holatini tanlang:", reply_markup=kb)
    await ElonState.holat.set()

# ========== 5-QADAM: HOLAT ==========
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
    await callback.message.edit_text("6/10: Savdo turini tanlang:", reply_markup=kb)
    await ElonState.savdo.set()

# ========== 6-QADAM: SAVDO ==========
@dp.callback_query_handler(lambda c: c.data.startswith("savdo_"), state=ElonState.savdo)
async def savdo_olish(callback: types.CallbackQuery, state: FSMContext):
    savdo_map = {
        "savdo_naqt": "💰 Naqt",
        "savdo_ipoteka": "🏦 Ipoteka",
        "savdo_subsidya": "📄 Subsidya"
    }
    await state.update_data(savdo=savdo_map[callback.data])
    await callback.message.edit_text("7/10: Rasm yoki video yuboring:")
    await ElonState.rasm.set()

# ========== 7-QADAM: RASM ==========
@dp.message_handler(content_types=["photo", "video"], state=ElonState.rasm)
async def rasm_olish(msg: types.Message, state: FSMContext):
    file_id = msg.photo[-1].file_id if msg.photo else msg.video.file_id
    media_type = "photo" if msg.photo else "video"
    await state.update_data(rasm=file_id, media_type=media_type)
    await msg.answer("8/10: Qo'shimcha ma'lumotlar:\n('yoq' deb yozing o'tkazib yuborish uchun)")
    await ElonState.qoshimcha.set()

@dp.message_handler(state=ElonState.rasm)
async def rasm_xato(msg: types.Message):
    await msg.answer("❌ Rasm yoki video yuboring!")

# ========== 8-QADAM: QOSHIMCHA ==========
@dp.message_handler(state=ElonState.qoshimcha)
async def qoshimcha_olish(msg: types.Message, state: FSMContext):
    qosh = "" if msg.text.lower() == "yoq" else msg.text
    await state.update_data(qoshimcha=qosh)
    await msg.answer("9/10: Narxni yozing:\n(masalan: 45 000 $, 150 000 000 so'm)")
    await ElonState.narx.set()

# ========== 9-QADAM: NARX ==========
@dp.message_handler(state=ElonState.narx)
async def narx_olish(msg: types.Message, state: FSMContext):
    await state.update_data(narx=msg.text)
    await msg.answer("10/10: Telefon raqamingizni yozing:")
    await ElonState.telefon.set()

# ========== 10-QADAM: TELEFON ==========
@dp.message_handler(state=ElonState.telefon)
async def telefon_olish(msg: types.Message, state: FSMContext):
    await state.update_data(telefon=msg.text)
    data = await state.get_data()
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ E'lonni joylashtirish", callback_data="submit_elon"))
    kb.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    await msg.answer(elon_matni_tekshir(data), reply_markup=kb)

# ========== JOYLASH ==========
@dp.callback_query_handler(lambda c: c.data == "submit_elon", state=ElonState.telefon)
async def submit_elon(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    guruh_matni = elon_matni_guruh(data)

    try:
        rasm = data.get('rasm')
        media_type = data.get('media_type', 'photo')
        if rasm:
            if media_type == "photo":
                sent = await bot.send_photo(GROUP_ID, rasm, caption=guruh_matni)
            else:
                sent = await bot.send_video(GROUP_ID, rasm, caption=guruh_matni)
        else:
            sent = await bot.send_message(GROUP_ID, guruh_matni)

        message_id = sent.message_id

        cur.execute("""INSERT INTO elonlar
        (user_id, turi, manzil, xonalar, metr, holat, savdo, rasm_file_id, media_type, qoshimcha, narx, telefon, message_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (callback.from_user.id, data.get('turi'), data.get('manzil'), data.get('xonalar'),
         data.get('metr'), data.get('holat'), data.get('savdo'), data.get('rasm'),
         data.get('media_type'), data.get('qoshimcha'), data.get('narx'), data.get('telefon'), message_id))
        conn.commit()

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

# ========== MENING E'LONLARIM ==========
@dp.callback_query_handler(lambda c: c.data == "my_elons", state="*")
async def my_elons(callback: types.CallbackQuery):
    cur.execute("""SELECT id, turi, manzil, xonalar, narx FROM elonlar
                WHERE user_id=? ORDER BY id DESC LIMIT 10""",
                (callback.from_user.id,))
    elons = cur.fetchall()
    if not elons:
        await callback.answer("❌ Sizda hali e'lonlar yo'q", show_alert=True)
        return
    kb = types.InlineKeyboardMarkup()
    for e in elons:
        kb.add(types.InlineKeyboardButton(
            f"🏠 #{e[0]} | {e[1]} | {e[3]} xona | {e[4]}",
            callback_data=f"my_elon_{e[0]}"
        ))
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="back_main"))
    await callback.message.edit_text("📋 <b>Sizning e'lonlaringiz:</b>\nBirini tanlang:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("my_elon_"), state="*")
async def my_elon_detail(callback: types.CallbackQuery):
    elon_id = int(callback.data.split("_")[2])
    cur.execute("SELECT * FROM elonlar WHERE id=? AND user_id=?", (elon_id, callback.from_user.id))
    e = cur.fetchone()
    if not e:
        await callback.answer("❌ E'lon topilmadi", show_alert=True)
        return

    # Columns: 0=id, 1=user_id, 2=turi, 3=manzil, 4=xonalar, 5=metr, 6=holat,
    #          7=savdo, 8=rasm_file_id, 9=media_type, 10=qoshimcha, 11=narx,
    #          12=telefon, 13=message_id, 14=last_repost, 15=created_at

    matn = (
        f"📋 <b>E'lon #{e[0]}</b>\n\n"
        f"🏠 Turi: {e[2]}\n"
        f"📍 Manzil: {e[3]}\n"
        f"🛏 Xonalar: {e[4]}\n"
        f"📐 {e[5]} m²\n"
        f"🔧 {e[6]}\n"
        f"💰 {e[7]}\n"
        f"💵 Narx: {e[11]}\n"
        f"📞 {e[12]}\n"
        f"📎 {e[10] or 'Yoq'}"
    )

    # Qayta e'lon berish — 24 soat tekshirish
    can_repost = True
    last_repost = e[14]
    if last_repost:
        last_time = datetime.strptime(last_repost, "%Y-%m-%d %H:%M:%S.%f") if "." in str(last_repost) else datetime.strptime(str(last_repost), "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - last_time
        if diff < timedelta(hours=24):
            remaining = timedelta(hours=24) - diff
            hours = int(remaining.seconds // 3600)
            minutes = int((remaining.seconds % 3600) // 60)
            can_repost = False

    kb = types.InlineKeyboardMarkup()
    if can_repost:
        kb.add(types.InlineKeyboardButton("🔄 Qayta e'lon berish", callback_data=f"repost_{elon_id}"))
    else:
        kb.add(types.InlineKeyboardButton(f"⏳ {hours}s {minutes}d dan keyin qayta e'lon", callback_data="cant_repost"))
    kb.row(
        types.InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"edit_elon_{elon_id}"),
        types.InlineKeyboardButton("🗑 O'chirish", callback_data=f"del_elon_{elon_id}")
    )
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="my_elons"))
    await callback.message.edit_text(matn, reply_markup=kb)

# ========== QAYTA E'LON ==========
@dp.callback_query_handler(lambda c: c.data == "cant_repost", state="*")
async def cant_repost(callback: types.CallbackQuery):
    await callback.answer("⏳ Hali vaqt bo'lmadi!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith("repost_"), state="*")
async def repost_elon(callback: types.CallbackQuery):
    elon_id = int(callback.data.split("_")[1])
    cur.execute("SELECT * FROM elonlar WHERE id=?", (elon_id,))
    e = cur.fetchone()
    if not e:
        await callback.answer("❌ E'lon topilmadi", show_alert=True)
        return

    # 24 soat tekshir
    last_repost = e[14]
    if last_repost:
        last_time = datetime.strptime(last_repost, "%Y-%m-%d %H:%M:%S.%f") if "." in str(last_repost) else datetime.strptime(str(last_repost), "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_time < timedelta(hours=24):
            await callback.answer("⏳ 24 soatda 1 marta qayta e'lon berish mumkin!", show_alert=True)
            return

    data = {
        'turi': e[2], 'manzil': e[3], 'xonalar': e[4], 'metr': e[5],
        'holat': e[6], 'savdo': e[7], 'rasm': e[8], 'media_type': e[9],
        'qoshimcha': e[10], 'narx': e[11], 'telefon': e[12]
    }
    guruh_matni = elon_matni_guruh(data)

    try:
        # Eski xabarni o'chirish
        old_msg_id = e[13]
        if old_msg_id:
            try:
                await bot.delete_message(GROUP_ID, old_msg_id)
            except:
                pass

        # Yangi joylash
        rasm = e[8]
        media_type = e[9] or 'photo'
        if rasm:
            if media_type == "photo":
                sent = await bot.send_photo(GROUP_ID, rasm, caption=guruh_matni)
            else:
                sent = await bot.send_video(GROUP_ID, rasm, caption=guruh_matni)
        else:
            sent = await bot.send_message(GROUP_ID, guruh_matni)

        # DB yangilash
        cur.execute("UPDATE elonlar SET message_id=?, last_repost=? WHERE id=?",
                    (sent.message_id, datetime.now(), elon_id))
        conn.commit()

        await callback.answer("✅ E'lon qayta joylandi!", show_alert=True)
        await my_elon_detail(callback)
    except Exception as ex:
        await callback.answer(f"⚠️ Xatolik: {ex}", show_alert=True)

# ========== O'CHIRISH (USER) ==========
@dp.callback_query_handler(lambda c: c.data.startswith("del_elon_"), state="*")
async def del_elon_confirm(callback: types.CallbackQuery):
    elon_id = int(callback.data.split("_")[2])
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"del_confirm_{elon_id}"),
        types.InlineKeyboardButton("❌ Yo'q", callback_data=f"my_elon_{elon_id}")
    )
    await callback.message.edit_text("⚠️ E'lonni o'chirishni tasdiqlaysizmi?\nGuruhdan ham o'chiriladi!", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("del_confirm_"), state="*")
async def del_elon(callback: types.CallbackQuery):
    elon_id = int(callback.data.split("_")[2])

    # Foydalanuvchi faqat o'z e'lonini o'chira oladi
    if is_admin(callback.from_user.id):
        cur.execute("SELECT * FROM elonlar WHERE id=?", (elon_id,))
    else:
        cur.execute("SELECT * FROM elonlar WHERE id=? AND user_id=?", (elon_id, callback.from_user.id))
    e = cur.fetchone()

    if not e:
        await callback.answer("❌ E'lon topilmadi", show_alert=True)
        return

    # Guruhdan o'chirish
    if e[13]:
        try:
            await bot.delete_message(GROUP_ID, e[13])
        except:
            pass

    cur.execute("DELETE FROM elonlar WHERE id=?", (elon_id,))
    conn.commit()

    await callback.message.edit_text("✅ E'lon o'chirildi!")
    await asyncio.sleep(1)
    await callback.message.answer("🏘 Bosh menyu:", reply_markup=main_kb(callback.from_user.id))

# ========== TAHRIRLASH ==========
@dp.callback_query_handler(lambda c: c.data.startswith("edit_elon_"), state="*")
async def edit_elon_menu(callback: types.CallbackQuery, state: FSMContext):
    elon_id = int(callback.data.split("_")[2])
    await state.update_data(edit_elon_id=elon_id)
    kb = types.InlineKeyboardMarkup()
    maydonlar = [
        ("🏠 Turi", "turi"), ("📍 Manzil", "manzil"), ("🛏 Xonalar", "xonalar"),
        ("📐 Metr", "metr"), ("🔧 Holat", "holat"), ("💰 Savdo", "savdo"),
        ("💵 Narx", "narx"), ("📎 Qo'shimcha", "qoshimcha"), ("📞 Telefon", "telefon")
    ]
    for nom, kod in maydonlar:
        kb.add(types.InlineKeyboardButton(nom, callback_data=f"edit_field_{kod}"))
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"my_elon_{elon_id}"))
    await callback.message.edit_text("✏️ Qaysi maydonni tahrirlaysiz?", reply_markup=kb)
    await TahrirState.maydon.set()

@dp.callback_query_handler(lambda c: c.data.startswith("edit_field_"), state=TahrirState.maydon)
async def edit_field_select(callback: types.CallbackQuery, state: FSMContext):
    maydon = callback.data.replace("edit_field_", "")
    await state.update_data(edit_maydon=maydon)

    maydon_nomi = {
        "turi": "Uy turi (Ko'p qavatli / Hovli)",
        "manzil": "Yangi manzilni yozing",
        "xonalar": "Yangi xonalar sonini yozing",
        "metr": "Yangi metrni yozing (faqat raqam)",
        "holat": "Yangi holatni yozing",
        "savdo": "Yangi savdo turini yozing",
        "narx": "Yangi narxni yozing",
        "qoshimcha": "Qo'shimcha ma'lumot yozing ('yoq' = bo'sh)",
        "telefon": "Yangi telefon raqamini yozing"
    }
    await callback.message.edit_text(f"✏️ {maydon_nomi.get(maydon, maydon)}:")
    await TahrirState.qiymat.set()

@dp.message_handler(state=TahrirState.qiymat)
async def edit_field_save(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    elon_id = data.get('edit_elon_id')
    maydon = data.get('edit_maydon')
    qiymat = msg.text

    if maydon == "qoshimcha" and qiymat.lower() == "yoq":
        qiymat = ""
    if maydon == "metr" and not qiymat.isdigit():
        await msg.answer("❌ Faqat raqam kiriting!")
        return

    # DB ustun nomini aniqlash
    ustun_map = {
        "turi": "turi", "manzil": "manzil", "xonalar": "xonalar",
        "metr": "metr", "holat": "holat", "savdo": "savdo",
        "narx": "narx", "qoshimcha": "qoshimcha", "telefon": "telefon"
    }
    ustun = ustun_map.get(maydon)
    cur.execute(f"UPDATE elonlar SET {ustun}=? WHERE id=?", (qiymat, elon_id))
    conn.commit()

    await state.finish()
    await msg.answer("✅ Saqlandi! E'lonni ko'rish:")

    # Yangilangan e'lonni guruhda ham yangilash
    cur.execute("SELECT * FROM elonlar WHERE id=?", (elon_id,))
    e = cur.fetchone()
    if e and e[13]:
        new_data = {
            'turi': e[2], 'manzil': e[3], 'xonalar': e[4], 'metr': e[5],
            'holat': e[6], 'savdo': e[7], 'qoshimcha': e[10], 'narx': e[11], 'telefon': e[12]
        }
        try:
            await bot.edit_message_caption(
                chat_id=GROUP_ID,
                message_id=e[13],
                caption=elon_matni_guruh(new_data)
            )
        except:
            pass

    # E'lon detayiga qaytish
    class FakeCallback:
        class from_user:
            id = msg.from_user.id
        class message:
            pass
        data = f"my_elon_{elon_id}"

    fake = types.CallbackQuery
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(f"📋 E'lon #{elon_id} ni ko'rish", callback_data=f"my_elon_{elon_id}"))
    kb.add(types.InlineKeyboardButton("🏘 Bosh menyu", callback_data="back_main"))
    await msg.answer("Quyidagi tugmani bosing:", reply_markup=kb)

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
    await callback.message.edit_text(
        f"🔐 <b>Admin panel</b>\n\n📊 Jami e'lonlar: {total}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "admin_stats", state="*")
async def admin_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cur.execute("SELECT COUNT(*) FROM elonlar")
    total = cur.fetchone()[0]
    cur.execute("SELECT turi, COUNT(*) FROM elonlar GROUP BY turi")
    stats = cur.fetchall()
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM elonlar")
    users = cur.fetchone()[0]
    matn = f"📊 <b>Statistika:</b>\n\n👥 Foydalanuvchilar: {users}\n📋 Jami e'lonlar: {total}\n\n"
    for tur, son in stats:
        matn += f"🏠 {tur}: {son} ta\n"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="admin_panel"))
    await callback.message.edit_text(matn, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "admin_all_elons", state="*")
async def admin_all_elons(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cur.execute("SELECT id, turi, manzil, xonalar, narx, user_id FROM elonlar ORDER BY id DESC LIMIT 10")
    elons = cur.fetchall()
    if not elons:
        await callback.message.edit_text("❌ Hozircha e'lonlar yo'q")
        return
    kb = types.InlineKeyboardMarkup()
    for e in elons:
        kb.add(types.InlineKeyboardButton(
            f"#{e[0]} | {e[1]} | {e[3]}x | {e[4]}",
            callback_data=f"admin_elon_{e[0]}"
        ))
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="admin_panel"))
    await callback.message.edit_text("📋 <b>So'nggi e'lonlar:</b>", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("admin_elon_"), state="*")
async def admin_elon_detail(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    elon_id = int(callback.data.split("_")[2])
    cur.execute("SELECT * FROM elonlar WHERE id=?", (elon_id,))
    e = cur.fetchone()
    if not e:
        await callback.answer("❌ Topilmadi", show_alert=True)
        return

    matn = (
        f"📋 <b>E'lon #{e[0]}</b>\n\n"
        f"👤 User ID: {e[1]}\n"
        f"🏠 Turi: {e[2]}\n"
        f"📍 Manzil: {e[3]}\n"
        f"🛏 Xonalar: {e[4]}\n"
        f"📐 {e[5]} m²\n"
        f"🔧 {e[6]}\n"
        f"💰 {e[7]}\n"
        f"💵 Narx: {e[11]}\n"
        f"📞 {e[12]}\n"
        f"📎 {e[10] or 'Yoq'}\n"
        f"📅 {e[15]}"
    )
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"admin_edit_{elon_id}"),
        types.InlineKeyboardButton("🗑 O'chirish", callback_data=f"admin_del_{elon_id}")
    )
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="admin_all_elons"))
    await callback.message.edit_text(matn, reply_markup=kb)

# ========== ADMIN O'CHIRISH ==========
@dp.callback_query_handler(lambda c: c.data.startswith("admin_del_"), state="*")
async def admin_del_confirm(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    elon_id = int(callback.data.split("_")[2])
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("✅ Ha, o'chirish", callback_data=f"admin_del_confirm_{elon_id}"),
        types.InlineKeyboardButton("❌ Yo'q", callback_data=f"admin_elon_{elon_id}")
    )
    await callback.message.edit_text("⚠️ E'lonni o'chirishni tasdiqlaysizmi?", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("admin_del_confirm_"), state="*")
async def admin_del_elon(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    elon_id = int(callback.data.split("_")[3])
    cur.execute("SELECT * FROM elonlar WHERE id=?", (elon_id,))
    e = cur.fetchone()
    if e and e[13]:
        try:
            await bot.delete_message(GROUP_ID, e[13])
        except:
            pass
    cur.execute("DELETE FROM elonlar WHERE id=?", (elon_id,))
    conn.commit()
    await callback.message.edit_text("✅ E'lon o'chirildi!")
    await asyncio.sleep(1)
    await admin_all_elons(callback)

# ========== ADMIN TAHRIRLASH ==========
@dp.callback_query_handler(lambda c: c.data.startswith("admin_edit_"), state="*")
async def admin_edit_menu(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    elon_id = int(callback.data.split("_")[2])
    await state.update_data(edit_elon_id=elon_id)
    kb = types.InlineKeyboardMarkup()
    maydonlar = [
        ("🏠 Turi", "turi"), ("📍 Manzil", "manzil"), ("🛏 Xonalar", "xonalar"),
        ("📐 Metr", "metr"), ("🔧 Holat", "holat"), ("💰 Savdo", "savdo"),
        ("💵 Narx", "narx"), ("📎 Qo'shimcha", "qoshimcha"), ("📞 Telefon", "telefon")
    ]
    for nom, kod in maydonlar:
        kb.add(types.InlineKeyboardButton(nom, callback_data=f"edit_field_{kod}"))
    kb.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"admin_elon_{elon_id}"))
    await callback.message.edit_text("✏️ Qaysi maydonni tahrirlaysiz?", reply_markup=kb)
    await TahrirState.maydon.set()

# ========== MAIN ==========
if __name__ == "__main__":
    print("🤖 Bot ishga tushdi!")
    print(f"👤 Admin IDs: {ADMIN_IDS}")
    executor.start_polling(dp, skip_updates=True)
