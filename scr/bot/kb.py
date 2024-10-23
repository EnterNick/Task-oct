from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard():
    kb = [
        [
            types.KeyboardButton(text="Настройки"),
            types.KeyboardButton(text="Задать текст"),
            types.KeyboardButton(text='Смотреть текст'),
            types.KeyboardButton(text='Инфо'),
            types.KeyboardButton(text='Заменить'),
            types.KeyboardButton(text='Сделать QrCode'),
            types.KeyboardButton(text='Анализ слова')
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard


def settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Регистр',
        callback_data='settings_register')
    )
    builder.add(types.InlineKeyboardButton(
        text='Опечатки',
        callback_data='settings_inaccuracies')
    )
    return builder


def change_text_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 11):
        builder.add(types.InlineKeyboardButton(
            text=str(i),
            callback_data=f'text_{i}')
        )
    return builder
