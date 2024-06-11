import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import config
from handlers import user
import settings

# Инициализация бота
bot: Bot = Bot(token=config.BOT_TOKEN)
storage: MemoryStorage = MemoryStorage()
dp: Dispatcher = Dispatcher(storage=storage)


async def main():
    # Регистрируем роутеры в диспетчере
    dp.include_router(user.router)
    await on_start(bot=bot)

    # polling
    await bot.delete_webhook()
    await dp.start_polling(bot)

# при запуске: создать команды в меню и написать ссылку в консоль
async def on_start(bot: Bot) -> None:
    command_list = [BotCommand(command=item[0], description=item[1]) for item in settings.commands.items()]
    await bot.set_my_commands(commands=command_list)
    print('Команды созданы:', len(command_list), 'шт')

    # ссылка на бота
    bot_info = await bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}"
    print(f'{bot_link = }')


if __name__ == '__main__':
    asyncio.run(main())
