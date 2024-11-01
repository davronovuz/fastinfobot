# kino_handlers.py: Kinolar bilan bog'liq barcha handlerlar
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from datetime import datetime
from loader import dp,bot,kino_db
from keyboards.default.admin_keyboard import admin_btn, movies_btn, exit_btn  # Tugmalar uchun import
from data.config import ADMINS
from states.kino_state import AddMedia, DeleteMovieState

# /start buyrug'i: Botga kirish va salomlashish

@dp.message_handler(commands="panel")
async def admin_handler(msg: types.Message):
    if msg.from_user.id in ADMINS:
        await msg.answer(f"Xush kelibsiz {msg.from_user.first_name}, admin panelga kirdingiz ⚙️", reply_markup=admin_btn())
    else:
        await msg.answer("Siz admin emassiz ❌", reply_markup=types.ReplyKeyboardRemove())

# Statistika ko'rish

# Kinolar statistikasi
@dp.message_handler(Text("Kino Statistika 📊"))
async def kino_statistika_handler(msg: types.Message):
    if msg.from_user.id in ADMINS:
        await msg.answer(text=kino_db.statistika_movie(), reply_markup=movies_btn())
    else:
        await msg.answer("Siz admin emassiz ❌", reply_markup=types.ReplyKeyboardRemove())

# Kino qo'shish jarayonini boshlash
@dp.message_handler(commands='kino_add')
async def kino_add_handler(msg: types.Message):
    if msg.from_user.id in ADMINS:
        await AddMedia.media.set()
        await msg.answer("Kinoni yuboring 🎬", reply_markup=exit_btn())
    else:
        await msg.answer("Siz admin emassiz ❌", reply_markup=types.ReplyKeyboardRemove())

# Kino faylini qabul qilish
@dp.message_handler(state=AddMedia.media, content_types=types.ContentType.VIDEO)
async def handle_video(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['file_id'] = msg.video.file_id
        data['caption'] = msg.caption
    await AddMedia.media_id.set()
    await msg.answer("Kino uchun ID kiriting:", reply_markup=exit_btn())

# Kino uchun post_id ni qabul qilish va bazaga qo'shish
@dp.message_handler(state=AddMedia.media_id, content_types=types.ContentType.TEXT)
async def handle_media_id(msg: types.Message, state: FSMContext):
    try:
        post_id = int(msg.text)
        async with state.proxy() as data:
            data['post_id'] = post_id
            kino_db.add_kino(post_id=post_id, file_id=data['file_id'], caption=data['caption'])
        await msg.answer("Kino muvaffaqiyatli qo'shildi ✅", reply_markup=movies_btn())
        await state.finish()
    except ValueError:
        await msg.answer("Iltimos, kino ID sifatida raqam kiriting!", reply_markup=exit_btn())

# Kino qidirish


# Kino o'chirish
@dp.message_handler(commands="delete_kino")
async def delete_kino_handler(msg: types.Message):
    if msg.from_user.id in ADMINS:
        await DeleteMovieState.post_id.set()
        await msg.answer("O'chirmoqchi bo'lgan kinoning ID sini kiriting:", reply_markup=exit_btn())
    else:
        await msg.answer("Siz admin emassiz ❌", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=DeleteMovieState.post_id)
async def handle_delete_kino(msg: types.Message, state: FSMContext):
    try:
        post_id = int(msg.text)
        kino_db.delete_movie(post_id)
        await msg.answer("Kino muvaffaqiyatli o'chirildi 🗑", reply_markup=movies_btn())
        await state.finish()
    except ValueError:
        await msg.answer("Iltimos, kino ID sifatida raqam kiriting!", reply_markup=exit_btn())

# Barcha kinolarni ko'rish
@dp.message_handler(commands="get_all_kinos")
async def get_all_kinos_handler(msg: types.Message):
    kinos = kino_db.get_all_kinos()
    if kinos:
        # Natijalarni tuple indekslari orqali olish
        response = "\n".join([f"Kino ID: {kino[0]}, Fayl ID: {kino[1]}, Tavsif: {kino[2]}" for kino in kinos])
        await msg.answer(f"Barcha kinolar:\n{response}")
    else:
        await msg.answer("Hozircha hech qanday kino mavjud emas.")


# So'nggi kinolarni ko'rish
@dp.message_handler(commands="recent_kinos")
async def get_recent_kinos_handler(msg: types.Message):
    days = int(msg.get_args()) if msg.get_args().isdigit() else 7
    kinos = kino_db.get_recent_kinos(days)
    if kinos:
        # Natijalarni tuple indekslari orqali olish
        response = "\n".join([
            f"Kino ID: {kino[0]},  Tavsif: {kino[3]}\n"
            for kino in kinos
        ])
        await msg.answer(f"So'nggi {days} kunda qo'shilgan kinolar:\n{response}\n\n")
    else:
        await msg.answer(f"So'nggi {days} kunda qo'shilgan kinolar mavjud emas.")

# Jami kinolar sonini ko'rsatish
@dp.message_handler(commands="count_kinos")
async def count_kinos_handler(msg: types.Message):
    count = len(kino_db.get_all_kinos())
    await msg.answer(f"Jami kinolar soni: {count} ta")


@dp.message_handler(lambda x: x.text.isdigit())
async def forward_last_video(msg: types.Message):
    if msg.text.isdigit():  # Xabar faqat raqam ekanligini tekshirish
        post_id = int(msg.text)
        data = kino_db.get_kino_by_post_id(post_id)

        if data:
            try:
                await bot.send_video(
                    chat_id=msg.from_user.id,
                    video=data['file_id'],  # file_id
                    caption = f"{data['caption']}\n\n🎬 Ko'proq kinolar uchun: @fastkinoobot"

                )
            except Exception as e:
                await msg.reply(f"Kino topildi, ammo jo'natishda xatolik yuz berdi ❌\nXatolik: {e}")
        else:
            await msg.reply(f"{msg.text} - ID bilan hech qanday kino topilmadi ❌")
    else:
        await msg.reply("Iltimos, faqat Kino kodini  kiriting.")


# Handlerlarni ro'yxatdan o'tkazish
def register_handlers_kino(dp: Dispatcher):

    dp.register_message_handler(admin_handler, commands="panel")
    dp.register_message_handler(kino_statistika_handler, Text("Kino Statistika 📊"))
    dp.register_message_handler(kino_add_handler, Text("Kino qo'shish 📥"))
    dp.register_message_handler(forward_last_video)
    dp.register_message_handler(delete_kino_handler, Text("Kino o'chirish 🗑"))
    dp.register_message_handler(get_all_kinos_handler, commands="get_all_kinos")
    dp.register_message_handler(get_recent_kinos_handler, commands="recent_kinos")
    dp.register_message_handler(count_kinos_handler, commands="count_kinos")
