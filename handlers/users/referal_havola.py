from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.deep_linking import get_start_link
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from loader import dp,user_db,bot


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    # Check if the user is using a referral link
    referrer_id = None
    if len(message.get_args()) > 0:
        try:
            referrer_id = int(message.get_args())
            # Ensure referrer exists in the database
            referrer = user_db.select_user(id=referrer_id)
            if not referrer:
                referrer_id = None
        except ValueError:
            referrer_id = None

    # Check if the user is already in the database
    user = user_db.select_user(telegram_id=telegram_id)
    if not user:
        # Add new user to the database
        user_db.add_user(telegram_id=telegram_id, username=username, referrer_id=referrer_id)
        await message.answer(
            f"Salom, {message.from_user.full_name}! \n"
            "Siz ushbu bot orqali o'z harajatlaringizni kuzatishingiz mumkin. \n"
            "Svet, gaz, chiqindi pullari kabi xarajatlarni boshqarish va nazorat qilish imkoniyatiga egasiz.",
            reply_markup=main_menu_keyboard()
        )

        # If the user joined using a referral link, update referral rewards
        if referrer_id:
            user_db.update_referral_reward(referrer_id=referrer_id, reward_amount=1000.0)  # Example reward amount
            await message.answer("Sizni taklif qilgan foydalanuvchiga mukofot berildi!")
    else:
        # Update user's last active time
        user_db.update_user_last_active(user_id=user[0])
        await message.answer(
            f"Yana salom, {message.from_user.full_name}! \n"
            "Qaytganingizdan xursandmiz. Bot orqali siz svet, gaz, chiqindi kabi xarajatlaringizni kuzatishda davom etishingiz mumkin.",
            reply_markup=main_menu_keyboard()
        )

@dp.message_handler(lambda message: message.text == "Referal havolam")
async def get_referral_link(message: types.Message):
    telegram_id = message.from_user.id
    user = user_db.select_user(telegram_id=telegram_id)
    if user:
        referral_link = await get_start_link(payload=user[0])
        await message.answer(
            f"Sizning referal havolangiz: {referral_link}\n"
            "Do'stlaringizni ushbu havola orqali taklif qiling va mukofotlarga ega bo'ling!"
        )
    else:
        await message.answer("Iltimos, avval botga qo'shiling!")

@dp.message_handler(lambda message: message.text == "Mening referallarim")
async def my_referrals(message: types.Message):
    telegram_id = message.from_user.id
    user = user_db.select_user(telegram_id=telegram_id)
    if user:
        referral_summary = user_db.get_user_referral_summary(user_id=user[0])
        if referral_summary:
            reward_amount, referrals_count = referral_summary
            await message.answer(
                f"Sizning takliflaringiz soni: {referrals_count}\n"
                f"Umumiy mukofot miqdori: {reward_amount} so'm"
            )
        else:
            await message.answer("Hozircha hech kimni taklif qilmagansiz.")
    else:
        await message.answer("Iltimos, avval botga qo'shiling!")

@dp.message_handler(lambda message: message.text == "Balansim")
async def my_balance(message: types.Message):
    telegram_id = message.from_user.id
    user = user_db.select_user(telegram_id=telegram_id)
    if user:
        balance = user[4]  # Assuming balance is the 5th field
        await message.answer(f"Sizning balansingiz: {balance} so'm")
    else:
        await message.answer("Iltimos, avval botga qo'shiling!")

@dp.message_handler(lambda message: message.text == "Pulni yechib olish")
async def withdraw_balance(message: types.Message):
    telegram_id = message.from_user.id
    user = user_db.select_user(telegram_id=telegram_id)
    if user:
        balance = user[4]  # Assuming balance is the 5th field
        if balance > 0:
            user_db.withdraw_user_balance(user_id=user[0], amount=balance)
            await message.answer(f"Siz {balance} so'm yechib oldingiz. Balansingiz 0 so'mga teng.")
        else:
            await message.answer("Sizda yechib olish uchun yetarli mablag' mavjud emas.")
    else:
        await message.answer("Iltimos, avval botga qo'shiling! /start")

def main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Referal havolam"))
    keyboard.add(KeyboardButton("Mening referallarim"))
    keyboard.add(KeyboardButton("Balan"))
    keyboard.add(KeyboardButton("Pulni yechib olish"))
    return keyboard
