"""
Middleware для проверки триал-периода пользователей.
"""
import datetime
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from database import db

# Инициализация логгера
logger = logging.getLogger(__name__)


class TrialMiddleware(BaseMiddleware):
    """
    Middleware для проверки статуса триал-периода пользователя.
    """
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обрабатывает событие и проверяет статус триал-периода.
        
        Args:
            handler: Функция-обработчик события
            event: Сообщение или колбэк-запрос
            data: Словарь с данными события
            
        Returns:
            Результат выполнения обработчика
        """
        # Получаем user_id в зависимости от типа события
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            # Для других типов событий пропускаем проверку
            return await handler(event, data)
        
        # Получаем информацию о пользователе
        user = await db.get_user(user_id)
        
        # Если пользователя нет в базе, пропускаем проверку
        if not user:
            return await handler(event, data)
        
        # Проверяем статус активности пользователя
        if not user.get("is_active", True):
            # Пользователь неактивен, проверяем причину
            if user.get("tariff_id"):
                # У пользователя есть тариф, активируем его
                await db.update_trial_status(user_id, True)
            else:
                # Триал закончился, ограничиваем функционал
                # Добавляем флаг о закончившемся триале в data
                data["trial_ended"] = True
        
        # Проверяем дату окончания триала
        trial_end_date = user.get("trial_end_date")
        if trial_end_date:
            # Преобразуем строку в datetime
            if isinstance(trial_end_date, str):
                trial_end_date = datetime.datetime.fromisoformat(trial_end_date)
            
            # Проверяем, закончился ли триал
            now = datetime.datetime.now()
            if now > trial_end_date and not user.get("tariff_id"):
                # Триал закончился и нет выбранного тарифа
                # Устанавливаем пользователя неактивным
                await db.update_trial_status(user_id, False)
                # Добавляем флаг о закончившемся триале в data
                data["trial_ended"] = True
        
        # Вызываем следующий обработчик
        return await handler(event, data) 