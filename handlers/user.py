import os
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from aiogram.types import CallbackQuery, Message, URLInputFile, Poll, PollAnswer
from pprint import pprint
import requests
from bot_logic import *
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


# проверить сколько машин в БД
@router.message(lambda msg: msg.text.lower().startswith('car top'))
async def command(msg: Message, bot: Bot):
    user = str(msg.from_user.id)
    await log(logs, user, msg.text, bot=bot)

    # проверить ввод
    top_num = msg.text.split()[-1]
    if not top_num.isnumeric():
        await msg.answer('Не задано число')
        return
    edit_msg = await msg.answer(f'Считаю топ {top_num} стран')

    # sql
    rm_duplicates()
    top_list = top_countries(num=top_num)

    # вывод списка
    print(f'{top_list = }')
    output = ''
    for i, country in enumerate(top_list, start=1):
        output += f'{i}. {country[0]}: {country[1]}\n'

    print(f'{output = }')

    await bot.edit_message_text(chat_id=user, message_id=edit_msg.message_id, text=output)


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
    if user in admins:
        if txt == 'url_test':
            await msg.answer('Отправь данные для нового пула')
            await state.set_state(FSM.url_test)
        elif txt == 'sbs_test':
            await msg.answer('Отправь архив для нового пула')
            await state.set_state(FSM.sbs_test)
        await log(logs, user, msg.text, bot=bot)

    else:
        await msg.answer('Нет доступа')
        await log(logs, user, msg.text+' no_access', bot=bot)


# юзер отправил архив для SBS
# @router.message()
@router.message(StateFilter(FSM.sbs_test))
async def sbs_test_request(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    pprint(msg)
    if not msg.document or 'zip' not in msg.document.mime_type:
        await msg.answer(f'Ошибка: я ожидаю Zip архив')
        await state.clear()
        return
    os.makedirs(name='tmp_sbs', exist_ok=True)
    file_id = msg.document.file_id

    # получить ссылку для скачивания архива
    try:
        file_info = await bot.get_file(file_id)
        file_url = file_info.file_path
        url = f'https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file_url}'
        print('zip url ok:', url)
    except Exception as e:
        await msg.answer(f'Произошла ошибка при получении архива:\n{e}')
        await state.clear()
        return

    # скачать архив
    response = requests.get(url=url)
    try:
        # создать файл
        zip_name = os.path.join(tmp_sbs, f'{msg.document.file_name}.zip')
        with open(zip_name, 'wb') as media:
            media.write(response.content)
    except Exception as e:
        await msg.answer(f'Произошла ошибка при скачивании архива:\n{e}')
        await state.clear()
        return

    # распаковать скачанный архив
    sbs_pics = []
    with zipfile.ZipFile(zip_name, mode="r") as archive:
        for file_info in archive.infolist():
            file = file_info.filename.encode('cp437').decode('utf-8')  # декодинг кириллицы
            if file.endswith((".jpg", '.png')) and '/' not in file:
                sbs_pics.append(file)
                archive.extract(file_info, f"{tmp_sbs}/")
                try:
                    path = f"{tmp_sbs}/{file_info}"
                    os.rename(dst=path, src=path.replace(file_info.filename, file))
                    print('file renamed')
                except Exception as e:
                    print(e)
                    pass

    if sbs_pics:
        pics_list_txt = [f'№ {i}: {f}\n' for i, f in enumerate(sbs_pics, start=1)]
        await msg.answer(text=f'Архив распакован. Найдены файлы:\n{"".join(pics_list_txt)}'
          f'\nУкажи через пробел номера файлов, который нужно использовать как хороший и плохой ханипот, например: "2 3". Либо напиши "нет", если ханипот не нужен')
        await state.set_state(FSM.sbs_wait)


# юзер указал ханипоты
# @router.message()
@router.message(StateFilter(FSM.sbs_wait))
async def sbs_honey(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
    await state.clear()


# юзер указал данные теста
@router.message(StateFilter(FSM.url_test))
async def url_test_request(msg: Message, bot: Bot, state: FSMContext):
    user = str(msg.from_user.id)
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
    result = await simp_test.start_test(pool_params=pool_params)

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
@router.message(~Access(admins), F.content_type.in_({'text'}))
async def usr_txt2(msg: Message, bot: Bot):
    await log(logs, msg.from_user.id, f'msg_to_admin: {msg.text}')

    # показать админам
    for i in admins:
        await bot.send_message(chat_id=i, text=f'Сообщение от {contact_user(msg.from_user)}: \n\n{msg.text}', parse_mode='HTML')
