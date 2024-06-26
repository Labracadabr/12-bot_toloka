from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, User, URLInputFile
from aiogram import Bot, Dispatcher
from datetime import datetime
from settings import *

# Фильтр, проверяющий доступ юзера
class Access(BaseFilter):
    def __init__(self, access: list[str]) -> None:
        # В качестве параметра фильтр принимает список со строками
        self.access = access

    async def __call__(self, message: Message) -> bool:
        user_id_str = str(message.from_user.id)
        return user_id_str in self.access


# Состояния FSM
class FSM(StatesGroup):
    # Состояния, в которых будет находиться бот в разные моменты взаимодействия с юзером
    html = State()
    url_test = State()
    sbs_test = State()
    sbs_wait = State()


# Запись данных item в указанный csv file по ключу key
async def log(file, key, item, bot: Bot = None):
    t = str(datetime.now()).split('.')[0]
    # сохранить в csv
    try:
        with open(file, 'a', encoding='utf-8') as f:
            print('\t'.join((t, str(key), repr(item))), file=f)

    except Exception as e:
        item += f'\n🔴Ошибка записи:\n{e}'

    # дублировать логи в консоль
    log_text = str(key)+' '+str(item)
    print(log_text)
    if bot and log_channel_id:
        try:
            await bot.send_message(chat_id=log_channel_id, text=log_text)
        except Exception as e:
            print('channel error', e)


# написать имя и ссылку на юзера, даже если он без username
def contact_user(user: User) -> str:
    tg_url = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
    text = f'{tg_url} id{user.id} @{user.username}'
    return text
