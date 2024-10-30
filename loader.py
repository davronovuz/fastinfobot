# loader.py: Telegram bot yuklash va modullardan foydalanish

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

# Modullarni import qilish
from utils.db_api.users import  UserDatabase
from utils.db_api.admins import AdminDatabase
from utils.db_api.groups import GroupDatabase
from utils.db_api.subscription_channel  import SubscriptionChannelDatabase

# Bot konfiguratsiyasi
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Ma'lumotlar bazasi sinflarini yaratish
user_db = UserDatabase(path_to_db="data/main.db")
admin_db = AdminDatabase(path_to_db="data/main.db")
group_db = GroupDatabase(path_to_db="data/main.db")
subscription_channel_db = SubscriptionChannelDatabase(path_to_db="data/main.db")


