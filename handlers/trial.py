"""
Обработчики для управления триал-периодом.
"""
import logging
import asyncio
import datetime
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import REMINDER_DAYS_BEFORE
from database import db
from keyboards.inline import get_trial_ending_keyboard, get_trial_ended_keyboard

# Инициализация логгера
logger = logging.getLogger(__name__)

# Создаем роутер для обработчиков триал-периода
trial_router = Router()


@trial_router.callback_query(F.data == "upgrade_to_paid")
async def upgrade_to_paid(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на кнопку "Перейти на платную версию".
    
    Args:
        callback: Callback-запрос от нажатия на инлайн-кнопку
        state: Контекст FSM
    """
    await callback.message.edit_text(
        "Для перехода на платную версию, пожалуйста, свяжитесь с нашим менеджером: "
        "manager@example.com\n\n"
        "Укажите ваш ID в Telegram: {0}".format(callback.from_user.id)
    )
    await callback.answer()


@trial_router.callback_query(F.data == "remind_later")
async def remind_later(callback: CallbackQuery) -> None:
    """
    Обрабатывает нажатие на кнопку "Напомнить позже".
    
    Args:
        callback: Callback-запрос от нажатия на инлайн-кнопку
    """
    await callback.message.edit_text(
        "Хорошо, я напомню вам об окончании триал-периода в день его завершения."
    )
    await callback.answer()


async def send_trial_ending_notification(bot: Bot) -> None:
    """
    Отправляет уведомления пользователям, у которых скоро закончится триал-период.
    
    Args:
        bot: Экземпляр бота для отправки сообщений
    """
    try:
        # Получаем пользователей, у которых заканчивается триал
        users = await db.get_users_with_ending_trial(REMINDER_DAYS_BEFORE)
        
        for user in users:
            try:
                # Отправляем уведомление
                await bot.send_message(
                    chat_id=user["chat_id"],
                    text=(
                        "⚠️ Ваш триал-период заканчивается завтра!\n\n"
                        "Чтобы продолжить пользоваться всеми функциями, "
                        "пожалуйста, перейдите на платную версию."
                    ),
                    reply_markup=get_trial_ending_keyboard()
                )
                logger.info(f"Отправлено уведомление о скором окончании триала пользователю {user['user_id']}")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления пользователю {user['user_id']}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений о скором окончании триала: {e}")


async def handle_ended_trials(bot: Bot) -> None:
    """
    Обрабатывает пользователей, у которых закончился триал-период.
    
    Args:
        bot: Экземпляр бота для отправки сообщений
    """
    try:
        # Получаем пользователей, у которых закончился триал
        users = await db.get_users_with_ended_trial()
        
        for user in users:
            try:
                # Обновляем статус активности пользователя
                await db.update_trial_status(user["user_id"], False)
                
                # Отправляем уведомление
                await bot.send_message(
                    chat_id=user["chat_id"],
                    text=(
                        "⚠️ Ваш триал-период закончился!\n\n"
                        "Теперь доступ к функциям ограничен. "
                        "Для продолжения использования всех возможностей системы, "
                        "пожалуйста, перейдите на платную версию."
                    ),
                    reply_markup=get_trial_ended_keyboard()
                )
                logger.info(f"Отправлено уведомление о завершении триала пользователю {user['user_id']}")
            except Exception as e:
                logger.error(f"Ошибка при обработке завершения триала пользователя {user['user_id']}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при обработке пользователей с завершенным триалом: {e}")


async def start_trial_checker(bot: Bot) -> None:
    """
    Запускает периодическую проверку статуса триал-периодов.
    
    Args:
        bot: Экземпляр бота для отправки сообщений
    """
    while True:
        try:
            # Проверяем заканчивающиеся триалы
            await send_trial_ending_notification(bot)
            
            # Обрабатываем завершенные триалы
            await handle_ended_trials(bot)
            
            # Делаем паузу до следующей проверки (раз в день)
            await asyncio.sleep(86400)  # 24 часа в секундах
        except Exception as e:
            logger.error(f"Ошибка в процессе проверки триал-периодов: {e}")
            # При ошибке делаем небольшую паузу и пробуем снова
            await asyncio.sleep(3600)  # 1 час в секундах