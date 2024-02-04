from aiogram import Router, Bot, F
from aiogram.enums import ParseMode
from settings import admins, logs
from bot_logic import *
import json
import os
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import config
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject
from bot_logic import *

# Инициализация бота
TKN = config.BOT_TOKEN
router: Router = Router()


# admin нажал ✅
@router.callback_query(Access(admins), F.data == 'admin_ok')
async def admin_ok(callback: CallbackQuery, bot: Bot):
    msg = callback.message

    # user = вытащить id из текста сообщения
    user = id_from_text(msg.text)


# админ что-то пишет
@router.message(Access(admins), F.content_type.in_({'text'}))
async def adm_msg(msg: Message, bot: Bot, state: FSMContext):
    admin = str(msg.from_user.id)
    txt = msg.text.lower()

    if txt == 'logs':
        pass
        # await bot.send_message(chat_id=admin, text=send_msg)

    else:
        await msg.answer('Команда не распознана')
        await log(logs, admin, f'wrong_command: \n{txt}')

