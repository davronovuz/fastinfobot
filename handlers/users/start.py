from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp,db
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    user = db.select_user(telegram_id=telegram_id)
    if not user:
        # Add new user to the database
        db.add_user(telegram_id=telegram_id, username=username)
        await message.answer(
            f"Salom, {message.from_user.full_name}! \n"
            "Siz ushbu bot orqali o'z harajatlaringizni kuzatishingiz mumkin. \n"
            "Svet, gaz, chiqindi pullari kabi xarajatlarni boshqarish va nazorat qilish imkoniyatiga egasiz."
        )
    else:
        # Update user's last active time
        db.update_user_last_active(user_id=user[0])
        await message.answer(
            f"Yana salom, {message.from_user.full_name}! \n"
            "Qaytganingizdan xursandmiz. Bot orqali siz svet, gaz, chiqindi kabi xarajatlaringizni kuzatishda davom etishingiz mumkin."
        )
