import asyncio
import logging
import sys
import os

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import hbold

from scr.search.search import find

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from dotenv import load_dotenv

from .data.db_session import create_session
from .data import users
from .kb import start_keyboard, settings_keyboard, change_text_keyboard

load_dotenv('scr/search/config.env')
TOKEN = os.getenv('BOT_TOKEN')
dp = Dispatcher()


class Form(StatesGroup):
    state = State()
    save = State()


@dp.message(F.text.lower() == 'смотреть текст')
async def command_get_text_handler(message: Message) -> None:
    db_sess = create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
    all_texts = []
    for i in range(1, 11):
        if user.__getattribute__(f'text_{i}') is not None:
            all_texts.append(f'Файл №{i}:\n\n' + user.__getattribute__(f'text_{i}'))
    db_sess.commit()
    db_sess.close()
    await message.answer('\n\n'.join(all_texts))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    db_sess = create_session()
    if not db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).all():
        user = users.User()
        user.telegram_id = message.from_user.id
        user.current_save = 'text_1'
        db_sess.add(user)
    db_sess.commit()
    db_sess.close()

    await message.answer(f'Привет, {hbold(message.from_user.full_name)}',
                         reply_markup=start_keyboard(), parse_mode=ParseMode.HTML)


@dp.message(F.text.lower() == 'настройки')
async def settings_handler(message: types.Message):
    await message.answer('Настройки бота', reply_markup=settings_keyboard().as_markup())


@dp.message(F.text.lower() == 'задать текст')
async def command_set_text_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.state)
    await message.answer('Какой сохранённый файл перезаписать?', reply_markup=change_text_keyboard().as_markup())


# @dp.message(F.text.lower() == 'заменить')
# async def command_set_text_handler(message: Message, state: FSMContext) -> None:



@dp.message(F.text.lower() == 'инфо')
async def command_info_handler(message: Message) -> None:
    await message.answer('''<b>Настройки</b> - можете выбрать настройки, которые будет учитывать бот при поиске текста.
<b>Задать текст</b> - используется для изменения теста, в котором будет происходить поиск. 
Сначала выбеите сохранение (используется для поиска сразу по нескольким текстам), а затем отправьте боту файл или текст.
<b>Смотреть текст</b> - отображает непустые сохранения.''', parse_mode=ParseMode.HTML)


@dp.callback_query(Form.state)
async def db_text_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    db_sess = create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == callback.from_user.id).first()
    user.current_save = callback.data
    db_sess.commit()
    db_sess.close()
    await state.set_state(Form.save)
    await callback.message.answer('Введите текст или отправьте файл: ')


@dp.message(Form.save)
async def text_parser(message: Message, state: FSMContext):
    if message.document is not None:
        try:
            text = await message.bot.get_file(message.document.file_id)
            text = await message.bot.download_file(text.file_path)
            text = text.read().decode()
        except Exception:
            await message.answer('К сожалению, я не могу прочитать файл такого формата.')
    elif not message.text.strip():
        await message.answer('Ноебходимо ввести непустой текст!')
        return
    else:
        text = message.text
    db_sess = create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
    user.__setattr__(user.current_save, text)
    db_sess.commit()
    db_sess.close()
    await state.clear()
    await message.answer('Текст успешно задан!')


@dp.callback_query(F.data == 'settings_register')
async def settings_register_handler(callback: types.CallbackQuery):
    db_sess = create_session()
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
    db_sess = create_session()
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
    if message.text is not None:
        db_sess = create_session()
        user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
        all_finds = []
        for i in range(1, 11):
            if user.__dict__[f'text_{i}'] is not None:
                all_finds.append(find(user.__dict__[f'text_{i}'], message.text,
                                      register=user.register, inaccuracies=user.inaccuracies))
        if not all_finds:
            await message.answer('Сначала необходимо задать текст!')
            return
        db_sess.close()
        await message.answer('\n\n'.join([f'Файл №{i + 1}:\n\n' + '\n'.join(all_finds[i])
                                          for i in range(len(all_finds))]))
    else:
        await message.answer('Введите непустое сообщение!')


async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


def bot_setup():
    load_dotenv('scr/search/config.env')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
