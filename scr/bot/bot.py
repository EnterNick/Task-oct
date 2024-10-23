import asyncio
import io
import logging
import sys
import os

import pymorphy3
import qrcode
import docx

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
    change = State()
    save_changes = State()
    input = State()
    analize = State()
    qr = State()


@dp.message(Command('отмена'))
async def cancel_input(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Отмена успешна!')


def make_qr_code(text: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


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
    if not all_texts:
        await message.answer('Сначала надо задать текст!')
        return
    await message.answer('\n\n'.join(all_texts))


@dp.message(F.text.lower() == 'анализ слова')
async def command_get_text_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.analize)
    await message.answer('Введите слово для анализа: ')


@dp.message(Form.analize)
async def analize_word(message: Message, state: FSMContext):
    await state.clear()
    analyzer = pymorphy3.MorphAnalyzer()
    word = analyzer.parse(message.text)[0]
    await message.answer(f'Слово: {word.word}\n'
                         f'Начальная форма: {word.normal_form} \n'
                         f'Грамеммы: {', '.join(word.tag.grammemes)}')


@dp.message(F.text.lower() == 'сделать qrcode')
async def command_get_text_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.qr)
    await message.answer('Введите слово для qr-cod`a: ')


@dp.message(Form.qr)
async def qr_code_handler(message: Message, state: FSMContext):
    await state.clear()
    img = make_qr_code(message.text).convert('L')
    buf = io.BytesIO()
    img.save(buf, format='png')
    buf.seek(0)
    photo = types.BufferedInputFile(buf.read(), 'photo.png')
    await message.answer_photo(photo)
    buf.close()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    db_sess = create_session()
    if not db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).all():
        user = users.User()
        user.name = message.from_user.full_name
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


@dp.message(F.text.lower() == 'заменить')
async def command_change_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Form.change)
    await message.answer('Введите слово, которое следует заменить: ')


@dp.message(Form.change)
async def change_text(message: Message, state: FSMContext):
    await find_handler(message)
    await message.answer('Введите номер файла и номер предложения через пробел, слово в которм надо заменить')
    db_sess = create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
    user.replace_word = message.text
    db_sess.commit()
    db_sess.close()
    await state.clear()
    await state.set_state(Form.input)


@dp.message(Form.input)
async def input_change_text(message: Message, state: FSMContext):
    db_sess = create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
    user_text = [i.split('🛅') for i in user.last_result.split('🛅🛅')]
    try:
        n = [*map(int, message.text.split())]
        if not (str(n[0]) in map(lambda x: x[-1], user_text) and
                any([str(n[1]) in i for i in user_text[n[0] - 1][0].split(', ')])):
            raise Exception
    except Exception:
        await message.answer('Введите номер файла и номер предложения через пробел, слово в которм надо заменить')
        db_sess.close()
        return
    file = [*filter(lambda x: x[1] == str(n[0]), user_text)][0][0].split('), (')
    file = [i.strip('[').strip(']').strip(')').strip('(') for i in file]
    sentence = [*filter(lambda x: x.split(', ')[1] == str(n[1]), file)][0]
    await state.clear()
    await message.answer('Введите слово, на которое надо заменить существующее: ')
    user.replace_word = sentence.split(', ')[0].strip("'")
    user.current_save = f'text_{n[0]}'
    db_sess.commit()
    db_sess.close()
    await state.set_state(Form.save_changes)


@dp.message(Form.save_changes)
async def save_replace(message: Message, state: FSMContext):
    db_sess = create_session()
    user = db_sess.query(users.User).filter(users.User.telegram_id == message.from_user.id).first()
    user.__setattr__(user.current_save,
                     user.__getattribute__(user.current_save).replace(user.replace_word, message.text))
    db_sess.commit()
    db_sess.close()
    await state.clear()
    await message.answer('Замена прошла успешно!')


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
    await callback.message.delete()
    await callback.message.answer('Введите текст или отправьте файл: ')


@dp.message(Form.save)
async def text_parser_handler(message: Message, state: FSMContext):
    text = ''
    if message.document is not None:
        try:
            file = await message.bot.get_file(message.document.file_id)
            file = await message.bot.download_file(file.file_path)
            if message.document.file_name.split('.')[1] in ['doc', 'docx']:
                file = docx.Document(file)
                for i in file.paragraphs:
                    text += '\n' + i.text
            else:
                text = file.read().decode()
        except Exception:
            await message.answer('К сожалению, я не могу прочитать файл такого формата.')
            return
    elif not message.text or not message.text.strip():
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
                all_finds.append((find(user.__dict__[f'text_{i}'], message.text,
                                       register=user.register, inaccuracies=user.inaccuracies), i))
        if not all_finds:
            await message.answer('Сначала необходимо задать текст!')
            return
        result = ''
        if ' ' not in message.text.strip():
            for i in all_finds:
                if i[0] != 'Слов не найдено!':
                    result += f'Файл №{i[1]}:\n\n' + '\n'.join(
                        [f'Слово: "{j[0]}", предложение№{j[1]}: "{j[2]}", оценка: {j[3]}' for j in i[0]]) + '\n\n'
                else:
                    result += f'Файл №{i[1]}:\n\n' + i[0] + '\n\n'
        else:
            for i in all_finds:
                result = f'Файл №{i[1]}:' + '\n\n'.join([f'Предложение№{j[0]}: "{j[1]}", оценка: {j[2]}' for j in i[0]])
        user.last_result = '🛅🛅'.join(['🛅'.join([*map(str, i)]) for i in all_finds])
        db_sess.commit()
        db_sess.close()
        await message.answer(result)
    else:
        await message.answer('Введите непустое сообщение!')


async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


def bot_setup():
    load_dotenv('scr/search/config.env')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
