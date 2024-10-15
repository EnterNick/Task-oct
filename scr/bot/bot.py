import asyncio
import logging
import sys
import os

from search.search import find

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv

from data import db_session
from data import users


TOKEN = os.getenv('BOT_TOKEN')
dp = Dispatcher()


@dp.message(Command('set_text'))
async def command_set_text_handler(message: Message, command: CommandObject) -> None:
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
    user.text = command.args
    db_sess.commit()
    db_sess.close()
    await message.answer('Текст успешно задан!')


@dp.message(Command('get_text'))
async def command_get_text_handler(message: Message) -> None:
    db_sess = db_session.create_session()
    text = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first().text
    db_sess.commit()
    db_sess.close()
    await message.answer(f'Текущий текст: {text}')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    db_sess = db_session.create_session()
    user = users.User()
    user.telegram_id = message.from_user.id
    db_sess.add(user)
    db_sess.commit()
    db_sess.close()
    kb = [
        [
            types.KeyboardButton(text="Настройки"),
            types.KeyboardButton(text="Задать текст")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await message.answer(f'Привет, <b>{message.from_user.full_name}</b>', parse_mode=ParseMode.HTML, reply_markup=keyboard)


@dp.message(F.text.lower() == 'настройки')
async def settings_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Регистр',
        callback_data='settings_register')
    )
    builder.add(types.InlineKeyboardButton(
        text='Опечатки',
        callback_data='settings_inaccuracies')
    )
    await message.answer('Настройки бота', reply_markup=builder.as_markup())


@dp.message(F.text.lower() == 'задать текст')
async def settings_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Регистр',
        callback_data='settings_register')
    )
    builder.add(types.InlineKeyboardButton(
        text='Опечатки',
        callback_data='settings_inaccuracies')
    )
    await message.answer('Настройки бота', reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'settings_register')
async def settings_register_handler(callback: types.CallbackQuery):
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == callback.from_user.id).first()
    if user.register:
        user.register = False
        await callback.message.answer('Бот теперь учитывает регистр.')
    else:
        user.register = True
        await callback.message.answer('Бот теперь не учитывает регистр.')
    db_sess.commit()
    await callback.answer()


@dp.callback_query(F.data == 'settings_inaccuracies')
async def settings_register_handler(callback: types.CallbackQuery):
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == callback.from_user.id).first()
    if user.inaccuracies:
        user.inaccuracies = False
        await callback.message.answer('Бот теперь не учитывает опечатки.')
    else:
        user.inaccuracies = True
        await callback.message.answer('Бот теперь учитывает опечатки.')
    db_sess.commit()
    await callback.answer()


@dp.message()
async def find_handler(message: types.Message) -> None:
    db_sess = db_session.create_session()
    text = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first().text
    db_sess.close()
    await message.answer(''.join(find(text, message.text)))


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


def bot_setup():
    load_dotenv('scr/search/config.env')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
