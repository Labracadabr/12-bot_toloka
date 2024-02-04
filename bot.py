import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from config import config
from handlers import admin, user
import settings

# Инициализация бота
bot: Bot = Bot(token=config.BOT_TOKEN)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(storage=storage)


async def main():
    settings.check_files()
    # Регистрируем роутеры в диспетчере
    dp.include_router(user.router)
    # dp.include_router(admin.router)
    # dp.include_router(test.router)

    # polling
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
