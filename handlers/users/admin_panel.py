# admin_panel.py: Admin paneli uchun barcha handlerlar
from aiogram import types
from aiogram.dispatcher import Dispatcher
from loader import dp, user_db, subscription_channel_db, admin_db
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime, timedelta
from keyboards.default.admin_keyboard import menu_admin, menu_ichki_kanal, menu_ichki_admin


# Admin menyusi handleri
async def admin_menu_handler(message: types.Message):
    await message.reply("👋 Admin paneliga xush kelibsiz! Kerakli bo'limni tanlang:", reply_markup=menu_admin)

# Statistika handleri
async def statistics_handler(message: types.Message):
    total_users = user_db.count_users()
    total_channels = len(subscription_channel_db.get_subscription_channels())
    total_admins = len(admin_db.get_all_admins())

    # Oxirgi 24 soatda qo'shilgan foydalanuvchilar
    last_24_hours = datetime.now() - timedelta(hours=24)
    last_24_hours_users = user_db.count_users_added_since(last_24_hours)

    # Bir haftalik qo'shilgan foydalanuvchilar
    last_week = datetime.now() - timedelta(weeks=1)
    last_week_users = user_db.count_active_users_since(last_week)

    # Oylik qo'shilgan foydalanuvchilar
    last_month = datetime.now() - timedelta(weeks=4)
    last_month_users = user_db.count_active_users_since(last_month)

    # Aktiv foydalanuvchilar (so'nggi 7 kun ichida faol bo'lganlar)
    active_users = user_db.count_active_users_since(last_week)

    await message.reply(
        "📊 <b>Bot statistikasi:</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_users}\n"
        f"📢 <b>Jami kanallar:</b> {total_channels}\n"
        f"👮‍♂️ <b>Jami adminlar:</b> {total_admins}\n\n"
        f"🕒 <b>Oxirgi 24 soatda qo'shilganlar:</b> {last_24_hours_users}\n"
        f"📅 <b>Bir haftalik qo'shilganlar:</b> {last_week_users}\n"
        f"📆 <b>Oylik qo'shilganlar:</b> {last_month_users}\n\n"
        f"🚀 <b>Aktiv foydalanuvchilar (so'nggi 7 kun):</b> {active_users}"
    )

# Kanallar bo'limi handleri
async def channels_menu_handler(message: types.Message):
    await message.reply("📢 Kanallar bo'limi. Kerakli amalni tanlang:", reply_markup=menu_ichki_kanal)

# Adminlar bo'limi handleri
async def admins_menu_handler(message: types.Message):
    await message.reply("👮‍♂️ Adminlar bo'limi. Kerakli amalni tanlang:", reply_markup=menu_ichki_admin)

# Reklama yuborish handleri
async def advertisement_menu_handler(message: types.Message):
    await message.reply("📣 Reklama yuborish bo'limi. Reklama yuborish uchun /advertisement komandasini yuboring.")

# Barcha adminlar ro'yxatini ko'rish handleri
async def all_admins_handler(message: types.Message):
    admins = admin_db.get_all_admins()
    if admins:
        admin_list = "👥 <b>Barcha adminlar:</b>\n" + "\n".join([f"- {admin[2]} ({admin[1]})" for admin in admins])
        await message.reply(admin_list, parse_mode='HTML')
    else:
        await message.reply("Hozirda birorta ham admin mavjud emas.")

# Admin qo'shish handler
async def add_admin_handler(message: types.Message):
    await message.reply("➕ Yangi admin qo'shish uchun uning Telegram ID raqamini kiriting:", reply_markup=ReplyKeyboardRemove())
    dp.register_message_handler(add_admin_process_handler, state=None, content_types=types.ContentTypes.TEXT)

async def add_admin_process_handler(message: types.Message):
    telegram_id = message.text
    if telegram_id.isdigit():
        admin_db.add_admin(telegram_id=int(telegram_id), username=message.from_user.username)
        await message.reply("✅ Admin muvaffaqiyatli qo'shildi.", reply_markup=menu_ichki_admin)
    else:
        await message.reply("❌ Noto'g'ri Telegram ID. Iltimos, raqam kiriting.")

# Admin o'chirish handleri
async def delete_admin_handler(message: types.Message):
    await message.reply("❌ Adminni o'chirish uchun uning Telegram ID raqamini kiriting:", reply_markup=ReplyKeyboardRemove())
    dp.register_message_handler(delete_admin_process_handler, state=None, content_types=types.ContentTypes.TEXT)

async def delete_admin_process_handler(message: types.Message):
    telegram_id = message.text
    if telegram_id.isdigit():
        admin_db.delete_admin(telegram_id=int(telegram_id))
        await message.reply("✅ Admin muvaffaqiyatli o'chirildi.", reply_markup=menu_ichki_admin)
    else:
        await message.reply("❌ Noto'g'ri Telegram ID. Iltimos, raqam kiriting.")

# Barcha kanallar ro'yxatini ko'rish handleri
async def all_channels_handler(message: types.Message):
    channels = subscription_channel_db.get_subscription_channels()
    if channels:
        channel_list = "📋 <b>Barcha kanallar:</b>\n" + "\n".join([f"- {channel[2]} ({channel[1]})" for channel in channels])
        await message.reply(channel_list, parse_mode='HTML')
    else:
        await message.reply("Hozirda birorta ham kanal mavjud emas.")

# Kanal qo'shish handleri
async def add_channel_handler(message: types.Message):
    await message.reply("➕ Yangi kanal qo'shish uchun kanal ID va nomini quyidagi formatda kiriting: ID - Nomi:", reply_markup=ReplyKeyboardRemove())
    dp.register_message_handler(add_channel_process_handler, state=None, content_types=types.ContentTypes.TEXT)

async def add_channel_process_handler(message: types.Message):
    try:
        parts = message.text.split(' - ', 1)
        if len(parts) != 2:
            raise ValueError("Noto'g'ri format")
        channel_id, channel_name = parts
        if channel_id.lstrip('-').isdigit():
            subscription_channel_db.add_subscription_channel(channel_id=int(channel_id), channel_name=channel_name)
            await message.reply("✅ Kanal muvaffaqiyatli qo'shildi.", reply_markup=menu_ichki_kanal)
        else:
            await message.reply("❌ Noto'g'ri kanal ID. Iltimos, raqam kiriting.")
    except ValueError:
        await message.reply("❌ Noto'g'ri format. Iltimos, ID va nomini quyidagi formatda kiriting: -1001234567890 - Kanal nomi")

# Kanal o'chirish handleri
async def delete_channel_handler(message: types.Message):
    await message.reply("❌ Kanalni o'chirish uchun uning Telegram ID raqamini kiriting:", reply_markup=ReplyKeyboardRemove())
    dp.register_message_handler(delete_channel_process_handler, state=None, content_types=types.ContentTypes.TEXT)

async def delete_channel_process_handler(message: types.Message):
    channel_id = message.text
    if channel_id.isdigit():
        subscription_channel_db.delete_subscription_channel(channel_id=int(channel_id))
        await message.reply("✅ Kanal muvaffaqiyatli o'chirildi.", reply_markup=menu_ichki_kanal)
    else:
        await message.reply("❌ Noto'g'ri kanal ID. Iltimos, raqam kiriting.")

# Ortga qaytish handleri
async def back_to_main_menu_handler(message: types.Message):
    await message.reply("🔙 Asosiy admin menyusiga qaytdingiz:", reply_markup=menu_admin)

# Handlerlarni ro'yxatga olish
async def register_handlers_admin_panel(dp: Dispatcher):
    dp.register_message_handler(admin_menu_handler, commands=['admin'])
    dp.register_message_handler(statistics_handler, text="📊 Statistika")
    dp.register_message_handler(channels_menu_handler, text="📢 Kanallar")
    dp.register_message_handler(admins_menu_handler, text="👥 Adminlar")
    dp.register_message_handler(advertisement_menu_handler, text="📣 Reklama yuborish")
    dp.register_message_handler(all_admins_handler, text="👥 Barcha adminlar")
    dp.register_message_handler(add_admin_handler, text="➕ Admin qo'shish")
    dp.register_message_handler(delete_admin_handler, text="❌ Adminni o'chirish")
    dp.register_message_handler(all_channels_handler, text="📋 Barcha kanallar")
    dp.register_message_handler(add_channel_handler, text="➕ Kanal qo'shish")
    dp.register_message_handler(delete_channel_handler, text="❌ Kanal o'chirish")
    dp.register_message_handler(back_to_main_menu_handler, text=["🔙 Ortga qaytish", "🔙 Asosiy menyuga qaytish"])
