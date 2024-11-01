from aiogram.types import ReplyKeyboardMarkup,KeyboardButton



# Admin paneli uchun tugmalar
menu_admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📊 Statistika'),
            KeyboardButton(text='📢 Kanallar'),
        ],
        [
            KeyboardButton(text='👥 Adminlar'),
            KeyboardButton(text='📣 Reklama yuborish'),
        ],
        [
            KeyboardButton(text='📄 Yordam'),
            KeyboardButton(text='🔙 Asosiy menyuga qaytish')
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

menu_ichki_admin = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='➕ Admin qo\'shish'),
            KeyboardButton(text='❌ Adminni o\'chirish'),
        ],
        [
            KeyboardButton(text='👥 Barcha adminlar'),
            KeyboardButton(text='🔙 Ortga qaytish'),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

menu_ichki_kanal = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='➕ Kanal qo\'shish'),
            KeyboardButton(text='❌ Kanal o\'chirish'),
        ],
        [
            KeyboardButton(text='📋 Barcha kanallar'),
            KeyboardButton(text='🔙 Ortga qaytish'),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)







def admin_btn():
    btn = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=3)
    statistika = KeyboardButton("Statistika 📊")
    movies = KeyboardButton("Kinolar 🎬")
    reklama = KeyboardButton("Reklama 🎁")
    add_chanell = KeyboardButton("Kanallar 🖇")
    return btn.add(statistika, movies, reklama, add_chanell)


def movies_btn():
    btn = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
    statistika = KeyboardButton("Kino Statistika 📊")
    add_movie = KeyboardButton("Kino qo'shish 📥")
    delete_movie = KeyboardButton("Kino o'chirish 🗑")
    exits = KeyboardButton("❌")
    return btn.add(statistika, add_movie, delete_movie, exits)


def channels_btn():
    btn = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
    add_channel = KeyboardButton("Kanal qo'shish ⚙️")
    delete_channel = KeyboardButton("Kanal o'chirish 🗑")
    exits = KeyboardButton("❌")
    return btn.add(add_channel, delete_channel, exits)


def exit_btn():
    btn = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
    return btn.add("❌")
