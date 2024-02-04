from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram.types import CallbackQuery, Message, URLInputFile, Poll, PollAnswer
from pprint import pprint
import requests
from bot_logic import *
from toloka_scripts import project_141070, project_154569, simp_test
from g_sheet import g_sheet_report
# Инициализация
router: Router = Router()


def validate_simp_test_request(msg_text: str):
    """
    Пример что должно быть на выходе
    {'account': 'avito',
     'date': '2024-01-29',
     'device': 'pc',
     'overlap': '300',
     'tasks': [{'input_values': {'code': '573', 'img_url': 'https://usabi.li/do/49e0d8d070c1/7439'}},
               {'input_values': {'code': '574', 'img_url': 'https://usabi.li/do/49e0d8d070c1/7440'}}],
     # 'user_fullname': 'Dmitrii Minokin',
     # 'user_id': 992863889,
     # 'user_username': 'its_dmitrii'
     }
    """
    session = requests.session()
    pool_params = {}
    pool_params.setdefault('account', 'avito')
    # pool_params.setdefault('input_values', {})
    try:
        print('Проверка сообщения')
        for line in msg_text.lower().split('\n'):
            # сами задания
            if 'http' in line:
                task_suite = {}
                for word in line.split():
                    # проверочный код
                    if word.isnumeric():
                        task_suite['code'] = word
                    # ссылка на тест
                    elif 'http' in word:
                        url = word
                        resp = session.get(url)  # проверить ссылку
                        print(url, resp.status_code)
                        if not resp.ok:
                            return f'Нерабочая ссылка: {url}, status_code {resp.status_code}'
                        task_suite['img_url'] = url

                if not len(task_suite) == 2:
                    return f'Нет кода или нет ссылки: {task_suite}'
                pool_params.setdefault('tasks', []).append({"input_values": task_suite})

            # overlap
            elif 'чел' in line or 'респ' in line:
                for word in line.split():
                    if word.isnumeric():
                        pool_params['overlap'] = word

            # device type
            if 'пк' in line or 'десктоп' in line or 'веб' in line:
                pool_params['device'] = 'pc'
            elif 'моб' in line:
                pool_params['device'] = 'mob'

    except Exception as e:
        print(e)
        return repr(e)
    if 'overlap' not in pool_params:
        return 'Не задано число респондентов'
    return pool_params

# команда /start
@router.message(Command(commands=['start']))
async def command(msg: Message):
    user = str(msg.from_user.id)
    await log(logs, user, '/start')
    await msg.answer('Привет')


# команда /help
@router.message(Command(commands=['help']))
async def command(msg: Message):
    user = str(msg.from_user.id)
    await log(logs, user, '/help')
    await msg.answer('no help')


# юзер создает тест
@router.message(Command(commands=['simp_test']))
async def alb(msg: Message, state):
    user = str(msg.from_user.id)
    if user in admins:
        await msg.answer('Отправь данные для нового пула')
        await state.set_state(FSM.simp_test)
        await log(logs, user, msg.text)
    else:
        await msg.answer('Нет доступа')
        await log(logs, user, msg.text+'_no_access')


# юзер указал данные теста
# @router.message()
@router.message(StateFilter(FSM.simp_test))
async def simp_test_request(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await state.clear()
    # проверить правильность запроса
    pool_params = validate_simp_test_request(msg_text=msg.text)
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
    result = await simp_test.start_test(pool_params=pool_params)

    # внести в таблицу
    if 'ошибка' not in result.lower():
        result += g_sheet_report(pool_params=pool_params)
    print(result)
    await msg.answer(text=result, disable_web_page_preview=True, parse_mode='HTML')


# скрипты проектов
@router.message(Command("141070", '154569', prefix="!"),)
async def p(msg: Message):
    user = str(msg.from_user.id)
    project = msg.text.strip('!')
    await msg.answer(text='Скрипт запущен')
    res = ''
    try:
        if project == '154569':
            res = project_154569.main()
        elif project == '141070':
            res = project_141070.main()
    except Exception as e:
        res = f'Ошибка\n{e}'
    await msg.answer(text=res if res else 'Ошибка')
    await log(logs, user, msg.text+'_'+res)


# юзер что-то еще пишет
@router.message(~Access(admins), F.content_type.in_({'text'}))
async def usr_txt2(msg: Message, bot: Bot):
    await log(logs, msg.from_user.id, f'msg_to_admin: {msg.text}')

    # показать админам
    for i in admins:
        await bot.send_message(chat_id=i, text=f'Сообщение от {contact_user(msg.from_user)}: \n\n{msg.text}', parse_mode='HTML')
