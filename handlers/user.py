import os
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram.types import CallbackQuery, Message, URLInputFile, Poll, PollAnswer
from pprint import pprint
import requests
from utils import *
from toloka_scripts import url_test, check_html, yndx_2609
from psql import top_countries, rm_duplicates
# Инициализация
router: Router = Router()


# команда /start
@router.message(Command(commands=['start']))
async def command(msg: Message, bot):
    user = str(msg.from_user.id)
    await log(logs, user, '/start', bot=bot)
    await msg.answer('Привет')

    # сообщить админу, кто стартанул бота
    alert = f'➕ user {contact_user(msg.from_user)}'
    await bot.send_message(text=alert, chat_id=admins[0], disable_notification=True, parse_mode='HTML')


# команда /help
@router.message(Command(commands=['help']))
async def command(msg: Message, bot):
    user = str(msg.from_user.id)
    await log(logs, user, '/help', bot=bot)
    await msg.answer('no help')


# команда /check_html
@router.message(Command(commands=['check_html']))
async def check_html_command(msg: Message, bot, state):
    user = str(msg.from_user.id)
    await log(logs, user, '/check_html', bot=bot)
    await msg.answer('Отправь ссылку на проект для проверки полей HTML')
    await state.set_state(FSM.html)


# юзер указал проект для проверки html
@router.message(StateFilter(FSM.html))
async def checking_html(msg: Message, bot, state):
    user = str(msg.from_user.id)
    result = check_html.check_html(msg.text.lower())

    await log(logs, user, result, bot=bot)
    await msg.answer(result)
    await state.clear()


# юзер создает тест
@router.message(Command(commands=['url_test', 'sbs_test']))
async def set_test(msg: Message, state, bot):
    user = str(msg.from_user.id)
    txt = msg.text.replace('/', '')

    if txt == 'url_test':
        await msg.answer('Отправь данные для нового пула')
        await state.set_state(FSM.url_test)
    elif txt == 'sbs_test':
        await msg.answer('Отправь архив для нового пула')
        await state.set_state(FSM.sbs_test)
    await log(logs, user, msg.text, bot=bot)


# юзер указал данные теста
@router.message(StateFilter(FSM.url_test))
async def url_test_request(msg: Message, bot: Bot, state: FSMContext):
    """
    Одним сообщением запускается пул тестов. На каждый пул должно быть указано:
        1. Аудитория - в любом месте сообщения ключевое слово 'пк', 'десктоп' или 'веб' для ПК, либо "моб" для мобилок
        2. Число респондентов - слово 'чел' или 'респ' - и в этой же строке само число
        3. Ссылки на тест и его код. Их может быть любое число, главное 1 тест = 1 новая строчка, и чтобы код для каждого теста был в этой же строчке через пробел
    """
    await state.clear()

    # проверить правильность запроса
    pool_params = url_test.validate_url_test_request(msg_text=msg.text)
    if not isinstance(pool_params, dict):
        await msg.answer(f'Ошибка:\n{pool_params}')
        return

    # доп параметры
    pool_params.setdefault('user_fullname', msg.from_user.full_name)
    pool_params.setdefault('user_username', msg.from_user.username)
    pool_params.setdefault('user_id', msg.from_user.id)
    pool_params.setdefault('date', str(msg.date.date()))
    pprint(pool_params)

    # создать пул
    result = await url_test.start_test(pool_params=pool_params)

    print(result)
    await msg.answer(text=result, disable_web_page_preview=True, parse_mode='HTML')


# скрипты проектов
@router.message(Command("141070", '154569', '2609', prefix="!"),)
async def p(msg: Message, bot):
    user = str(msg.from_user.id)
    project = msg.text.strip('!')
    await msg.answer(text='Скрипт запущен')
    res = ''
    try:
        if project == '154569':
            res = project_154569.main()
        elif project == '141070':
            res = project_141070.main()
        elif project == '2609':
            res = yndx_2609.read_pool(pool='1763442')

    except Exception as e:
        res = f'Ошибка\n{e}'
    await msg.answer(text=res if res else 'Ошибка')
    await log(logs, user, msg.text+res, bot=bot)


# юзер что-то еще пишет
@router.message(F.content_type.in_({'text'}))
async def usr_txt2(msg: Message, bot: Bot):
    await log(logs, msg.from_user.id, f'msg not handled: {msg.text}')

    await msg.answer(text='Команда не распознана')