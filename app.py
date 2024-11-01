from aiogram import executor

from loader import dp,user_db,group_db,subscription_channel_db,admin_db,kino_db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from handlers.users.reklama import register_handlers_advertisement
from handlers.users.admin_panel import register_handlers_admin_panel
from handlers.users.kino_handler import register_handlers_kino


async def on_startup(dispatcher):
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    # Ma'lumotlar bazasini yaratamiz:
    try:
        user_db.create_table_users()
        user_db.create_table_referral_rewards()
        user_db.create_table_transaction_history()
        admin_db.create_table_admins()
        subscription_channel_db.create_table_subscription_channels()
        group_db.create_table_groups()
        kino_db.create_table_kino()
    except Exception as err:
        print(err)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)

    await register_handlers_advertisement(dispatcher)
    await register_handlers_admin_panel(dispatcher)
    register_handlers_kino(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)