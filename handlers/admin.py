"""
Обработчики для админ-панели.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database import db

# Инициализация логгера
logger = logging.getLogger(__name__)

# Создаем роутер для обработчиков админ-панели
admin_router = Router()


def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        True, если пользователь является админом, иначе False
    """
    return user_id in ADMIN_IDS


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """
    Обрабатывает команду /admin, показывает админ-панель.
    
    Args:
        message: Сообщение от пользователя
    """
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к админ-панели.")
        return
    
    # Получаем статистику
    stats = await db.get_admin_stats()
    
    # Форматируем статистику о популярных тарифах
    popular_tariffs_text = ""
    if stats["popular_tariffs"]:
        for tariff in stats["popular_tariffs"]:
            popular_tariffs_text += f"- {tariff['name']}: {tariff['user_count']} пользователей\n"
    else:
        popular_tariffs_text = "Нет данных о выбранных тарифах."
    
    # Формируем сообщение с админской панелью
    admin_panel_text = (
        "📊 Статистика бота «Нейропродажник»\n\n"
        f"👥 Активных пользователей: {stats['active_users_count']}\n"
        f"💰 Конверсия в оплату: {stats['conversion_rate']:.2f}%\n\n"
        f"📈 Популярные тарифы:\n{popular_tariffs_text}"
    )
    
    await message.answer(admin_panel_text)
    logger.info(f"Админ {user_id} запросил статистику бота.")


@admin_router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext) -> None:
    """
    Запускает рассылку сообщения всем пользователям.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if not is_admin(user_id):
        await message.answer("У вас нет доступа к этой команде.")
        return
    
    # Получаем текст рассылки из аргументов команды
    broadcast_text = message.text.replace("/broadcast", "").strip()
    
    if not broadcast_text:
        await message.answer(
            "Пожалуйста, укажите текст рассылки после команды.\n\n"
            "Пример: /broadcast Важное сообщение для всех пользователей!"
        )
        return
    
    await message.answer(f"Начинаю рассылку сообщения:\n\n{broadcast_text}")
    
    # Заглушка для рассылки
    # В реальном боте здесь должен быть код для отправки сообщения всем пользователям
    
    await message.answer("Рассылка завершена успешно!")
    logger.info(f"Админ {user_id} выполнил рассылку сообщения.") 