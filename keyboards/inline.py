"""
Модуль для создания inline-клавиатур.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_tariff_selection_keyboard(tariff_names: list) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора тарифа.
    
    Args:
        tariff_names: Список названий тарифов
        
    Returns:
        InlineKeyboardMarkup: Клавиатура для выбора тарифа
    """
    builder = InlineKeyboardBuilder()
    
    for i, name in enumerate(tariff_names):
        builder.button(text=f"Выбрать «{name}»", callback_data=f"select_tariff:{i}")
        builder.button(text=f"Подробнее о «{name}»", callback_data=f"tariff_details:{i}")
    
    builder.button(text="Связаться с менеджером", callback_data="contact_manager")
    
    # Устанавливаем по 1 кнопке в ряду
    builder.adjust(1)
    
    return builder.as_markup()


def get_trial_ending_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для уведомления о скором окончании триала.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками продления
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Перейти на платную версию", callback_data="upgrade_to_paid")
    builder.button(text="Напомнить позже", callback_data="remind_later")
    builder.button(text="Связаться с менеджером", callback_data="contact_manager")
    
    # Устанавливаем по 1 кнопке в ряду
    builder.adjust(1)
    
    return builder.as_markup()


def get_trial_ended_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для уведомления об окончании триала.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой перехода на платную версию
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Перейти на платную версию", callback_data="upgrade_to_paid")
    builder.button(text="Связаться с менеджером", callback_data="contact_manager")
    
    # Устанавливаем по 1 кнопке в ряду
    builder.adjust(1)
    
    return builder.as_markup()


def get_tariff_details_keyboard(tariff_index: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для просмотра подробностей о тарифе.
    
    Args:
        tariff_index: Индекс выбранного тарифа
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками выбора и возврата
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Выбрать этот тариф", callback_data=f"select_tariff:{tariff_index}")
    builder.button(text="Вернуться к списку тарифов", callback_data="back_to_tariffs")
    builder.button(text="Связаться с менеджером", callback_data="contact_manager")
    
    # Устанавливаем по 1 кнопке в ряду
    builder.adjust(1)
    
    return builder.as_markup() 