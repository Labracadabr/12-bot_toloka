from aiogram.filters import BaseFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, FSInputFile, User, URLInputFile
from aiogram import Bot, Dispatcher
from datetime import datetime
import importlib

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
    ask_sheet = State()
    ask_channel = State()
    confirm = State()
    password = State()
    simp_test = State()


# Запись данных item в указанный csv file по ключу key
async def log(file, key, item, bot: Bot = None):
    t = str(datetime.now()).split('.')[0]
    # сохранить в csv
    try:
        with open(file, 'a', encoding='utf-8') as f:
            print('\t'.join((t, str(key), repr(item))), file=f)
        # with open(file, encoding='utf-8') as f:  # старая версия с json
        #     data = json.load(f)
        # data.setdefault(str(key), []).append(item)
        # with open(file, 'w', encoding='utf-8') as f:
        #     json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        item += f'\n🔴Ошибка записи:\n{e}'

    # дублировать логи в консоль
    log_text = str(key)+' '+str(item)
    print(log_text)
    # дублировать логи в тг-канал
    if bot and log_channel_id:
        try:
            await bot.send_message(chat_id=log_channel_id, text=log_text)
        except Exception as e:
            print('channel error', e)


# айди из текста
def id_from_text(text: str) -> str:
    user_id = ''
    for word in text.split():
        if word.lower().startswith('id'):
            for symbol in word:
                if symbol.isnumeric():
                    user_id += symbol
            break
    return user_id


# написать имя и ссылку на юзера, даже если он без username
def contact_user(user: User) -> str:
    tg_url = f'<a href="tg://user?id={user.id}">{user.full_name}</a>'
    text = f'{tg_url} id{user.id} @{user.username}'
    return text


# получить значение
def get_pers_info(user: str, key: str):
    with open(users_data, 'r', encoding='utf-8') as f:
        data: dict = json.load(f)
    user_data: dict = data.get(user)
    if not user_data:
        print(user, f'user not found', key)
        return None
    value = user_data.get(key)
    return value


# задать значение
def set_pers_info(user: str, key: str, val):
    # прочитать бд
    with open(users_data, 'r', encoding='utf-8') as f:
        data: dict = json.load(f)
    user_data: dict = data.get(user)
    if not user_data:
        print(user, f'user not found', key, val)
        return None
    old_val = user_data.get(key)

    # сохр изменение
    user_data[key] = val
    data.setdefault(user, user_data)
    with open(users_data, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(user, f'{key}: {old_val} => {val}')
