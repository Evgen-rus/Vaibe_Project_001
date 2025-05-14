"""
Главный файл для запуска бота "Нейропродажник".
"""
import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database.db import init_db
from database.models import init_models
from handlers.onboarding import onboarding_router
from handlers.trial import trial_router, start_trial_checker
from handlers.admin import admin_router
from middlewares.trial_check import TrialMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Инициализация логгера
logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Главная функция для запуска бота.
    """
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация middleware
    dp.message.middleware(TrialMiddleware())
    dp.callback_query.middleware(TrialMiddleware())
    
    # Регистрация роутеров
    dp.include_router(onboarding_router)
    dp.include_router(trial_router)
    dp.include_router(admin_router)
    
    # Инициализация базы данных
    try:
        await init_db()
        await init_models()
        logger.info("База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        return
    
    # Запуск фоновой задачи для проверки триал-периода
    asyncio.create_task(start_trial_checker(bot))
    
    # Удаление webhook и запуск поллинга
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}") 