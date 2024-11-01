from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env faylidan qiymatlarni o'qish
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
ADMINS = list(map(int, env.list("ADMINS")))  # adminlar ro'yxati (int ga aylantirilgan)
IP = env.str("IP")  # Xosting IP manzili
