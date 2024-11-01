from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, user_db
from keyboards.default.admin_keyboard import menu_kanal
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    # Foydalanuvchi bazada mavjudligini tekshirish
    user = user_db.select_user(telegram_id=telegram_id)
    if not user:
        # Yangi foydalanuvchini bazaga qo'shish
        user_db.add_user(telegram_id=telegram_id, username=username)
        welcome_text = (
            f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
            "Sizni <b>FastKinoBot</b> botida ko‘rib turganimizdan xursandmiz! 🎉\n\n"
            "<b>FastKinoBot</b> orqali siz quyidagi imkoniyatlardan foydalanishingiz mumkin:\n"
            "🎬 Eng yangi va qiziqarli kinolarni topish\n"
            "🔍 Kino kodi orqali qidirish\n"
            "📊 Eng ko‘p ko‘rilgan va mashhur kinolar ro‘yxati\n\n"
            "Botdan foydalanish uchun <b>kino kodini</b> kiriting va "
            "kinoni tez va oson yuklab oling! 😊\n\n"
            "📢 Yangiliklardan xabardor bo‘lish uchun bizning kanalga obuna bo‘lishni unutmang! "
        )
        await message.answer(welcome_text, parse_mode="HTML")
    else:
        # Foydalanuvchini qayta kelganligini yangilash va xush kelibsiz xabarini yuborish
        user_db.update_user_last_active(user_id=user[0])
        welcome_back_text = (
            f"Yana salom, {message.from_user.full_name}! 👋\n\n"
            "FastKinoBot’ga qaytganingizdan xursandmiz! 🎉\n\n"
            "Siz bot orqali kinolarni qidirishda davom etishingiz mumkin. "
            "Kino kodini kiriting va eng yaxshi filmlardan zavqlaning! 🎬"
        )
        await message.answer(welcome_back_text, parse_mode="HTML",reply_markup=menu_kanal)


@dp.message_handler(text='🎬Barcha Kinolar')
async def bot_start(message: types.Message):
    text="@tarjimakinolarfast"
    await message.answer(f"Barcha kinolar : {text}")



