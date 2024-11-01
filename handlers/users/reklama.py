# reklama.py: Foydalanuvchilarga reklama yuborish handleri
from data.config import ADMINS
from loader import bot, dp, user_db
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, RetryAfter, Unauthorized
import asyncio

# Reklama jarayonini nazorat qilish uchun global flag
advertisement_running = False
advertisement_content = None

# Reklama yuborish komandasi handleri
async def advertisement_command_handler(message: types.Message):
    global advertisement_running
    # Admin yoki superadmin ekanligini tekshirish
    admin = user_db.select_user(telegram_id=message.from_user.id)
    if admin and (admin[3] == 'admin' or message.from_user.id in ADMINS):  # 'admin' roliga ega ekanligini yoki ADMINS ro'yxatida ekanligini tekshirish
        if advertisement_running:
            await message.reply("Hozirda reklama yuborilmoqda. Iltimos, jarayon yakunlanishini kuting yoki uni to'xtating.")
        else:
            await message.reply("Reklama yuboriladigan kontentni kiriting (matn, rasm, video, va hokazo):", reply_markup=get_cancel_keyboard())
            dp.register_message_handler(receive_advertisement_content, content_types=types.ContentTypes.ANY, state=None)
    else:
        await message.reply("Sizda ushbu komandadan foydalanish uchun huquq yo'q.")

# Reklamani to'xtatish tugmasi uchun keyboard
def get_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("❌ To'xtatish"))
    return keyboard

# Reklamani tasdiqlash yoki rad etish uchun keyboard
def get_confirm_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_ad"))
    keyboard.add(types.InlineKeyboardButton("❌ Rad etish", callback_data="cancel_ad"))
    return keyboard

# Reklama kontentini qabul qilish
async def receive_advertisement_content(message: types.Message):
    global advertisement_content
    advertisement_content = message
    await message.reply("Reklamani yuborishni tasdiqlaysizmi?", reply_markup=get_confirm_keyboard())
    dp.register_callback_query_handler(handle_confirm_callback, lambda c: c.data in ["confirm_ad", "cancel_ad"], state=None)

# Tasdiqlash yoki rad etish tugmalarini boshqarish
async def handle_confirm_callback(callback_query: types.CallbackQuery):
    global advertisement_running, advertisement_content
    if callback_query.data == "confirm_ad":
        advertisement_running = True
        await callback_query.message.edit_text("Reklama yuborish tasdiqlandi. Yuborish jarayoni boshlandi...", reply_markup=None)
        await start_sending_advertisement(callback_query.message)
    elif callback_query.data == "cancel_ad":
        advertisement_content = None
        await callback_query.message.edit_text("Reklama yuborish rad etildi.", reply_markup=None)

# Reklama yuborish jarayonini boshlash
async def start_sending_advertisement(message: types.Message):
    global advertisement_running, advertisement_content
    users = user_db.select_all_users()  # Barcha foydalanuvchilarni olish
    total_users = len(users)
    sent_count = 0
    failed_count = 0
    in_progress_message = await message.reply(f"Reklama yuborish boshlandi. Jami foydalanuvchilar: {total_users}", reply_markup=get_cancel_keyboard())

    for index, user in enumerate(users, start=1):
        if not advertisement_running:
            await in_progress_message.edit_text(
                f"Reklama to'xtatildi:\n"
                f"Jami foydalanuvchilar: {total_users}\n"
                f"Muvaffaqiyatli yuborildi: {sent_count}\n"
                f"Xatolar: {failed_count}"
            )
            return

        try:
            # Reklama turiga qarab tegishli xabar yuborish
            if advertisement_content.content_type == types.ContentType.TEXT:
                await bot.send_message(chat_id=user[1], text=advertisement_content.text)
            elif advertisement_content.content_type == types.ContentType.PHOTO:
                await bot.send_photo(chat_id=user[1], photo=advertisement_content.photo[-1].file_id, caption=advertisement_content.caption)
            elif advertisement_content.content_type == types.ContentType.VIDEO:
                await bot.send_video(chat_id=user[1], video=advertisement_content.video.file_id, caption=advertisement_content.caption)
            elif advertisement_content.content_type == types.ContentType.DOCUMENT:
                await bot.send_document(chat_id=user[1], document=advertisement_content.document.file_id, caption=advertisement_content.caption)
            elif advertisement_content.content_type == types.ContentType.AUDIO:
                await bot.send_audio(chat_id=user[1], audio=advertisement_content.audio.file_id, caption=advertisement_content.caption)
            else:
                print(f"Yuborish uchun noma'lum kontent turi: {advertisement_content.content_type}")
                failed_count += 1
                continue

            sent_count += 1
        except (BotBlocked, ChatNotFound, Unauthorized):
            # Agar foydalanuvchi botni bloklagan yoki chat topilmasa
            failed_count += 1
        except RetryAfter as e:
            # Telegram spamdan himoya qilish uchun vaqtincha to'xtatgan
            await asyncio.sleep(e.timeout)
            continue
        except Exception as e:
            print(f"Xatolik: {e}")
            failed_count += 1

        # Har 10ta yuborilgan xabardan so'ng jarayon haqida ma'lumot yangilash
        if index % 10 == 0:
            await in_progress_message.edit_text(f"Reklama yuborilishi davom etmoqda: {index}/{total_users} ta foydalanuvchiga yuborildi...")

        await asyncio.sleep(0.1)  # Spamdan saqlanish uchun qisqa vaqt

    # Jarayon yakunlandi, statistika bilan xabar
    advertisement_running = False
    await in_progress_message.edit_text(
        f"Reklama yakunlandi:\n"
        f"Jami foydalanuvchilar: {total_users}\n"
        f"Muvaffaqiyatli yuborildi: {sent_count}\n"
        f"Xatolar: {failed_count}"
    )

# Reklama jarayonini to'xtatish handleri
async def cancel_advertisement_handler(message: types.Message):
    global advertisement_running
    if advertisement_running and message.text == "❌ To'xtatish":
        advertisement_running = False
        await message.reply("Reklama yuborish jarayoni to'xtatildi.", reply_markup=types.ReplyKeyboardRemove())

# `advertisement_command_handler` funksiyasini /advertisement komandasiga ulash
async def register_handlers_advertisement(dp: Dispatcher):
    dp.register_message_handler(advertisement_command_handler, commands=['advertisement'])
    dp.register_message_handler(cancel_advertisement_handler, text="❌ To'xtatish")
