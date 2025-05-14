"""
Модуль для создания reply-клавиатур.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает стартовую клавиатуру с кнопкой начала теста.
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопкой "Начать тест"
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Начать тест")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_onboarding_options_keyboard(options: list) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с вариантами ответов для вопросов онбординга.
    
    Args:
        options: Список вариантов ответов
        
    Returns:
        ReplyKeyboardMarkup: Клавиатура с вариантами ответов
    """
    buttons = []
    for option in options:
        buttons.append([KeyboardButton(text=option)])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard 