"""
Модуль для инициализации моделей базы данных и загрузки начальных данных.
"""
import asyncio
import logging
import aiosqlite
from config import DATABASE_PATH, ONBOARDING_QUESTIONS

logger = logging.getLogger(__name__)

# Предустановленные тарифы
DEFAULT_TARIFFS = [
    {
        "name": "Базовый",
        "description": "Тариф для небольших компаний и индивидуальных предпринимателей. Включает основной функционал без дополнительных опций.",
        "price": 1990.0
    },
    {
        "name": "Стандарт",
        "description": "Оптимальный выбор для среднего бизнеса. Включает расширенный функционал и приоритетную поддержку.",
        "price": 4990.0
    },
    {
        "name": "Премиум",
        "description": "Полный набор функций для крупного бизнеса. Включает все возможности системы, персонального менеджера и круглосуточную поддержку.",
        "price": 9990.0
    }
]


async def load_onboarding_questions() -> None:
    """
    Загружает вопросы для онбординга из конфигурации в базу данных.
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Сначала удаляем все существующие вопросы
            await db.execute("DELETE FROM onboarding_questions")
            
            # Добавляем вопросы из конфигурации
            for question in ONBOARDING_QUESTIONS:
                await db.execute(
                    "INSERT INTO onboarding_questions (id, question_text, question_type) VALUES (?, ?, ?)",
                    (question["id"], question["text"], question["type"])
                )
            
            await db.commit()
            logger.info("Вопросы для онбординга загружены успешно.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке вопросов для онбординга: {e}")
        raise


async def load_default_tariffs() -> None:
    """
    Загружает предустановленные тарифы в базу данных, если они еще не существуют.
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Проверяем, есть ли уже тарифы в базе
            async with db.execute("SELECT COUNT(*) FROM tariffs") as cursor:
                count = await cursor.fetchone()
                if count and count[0] > 0:
                    logger.info("Тарифы уже существуют в базе данных.")
                    return
            
            # Добавляем предустановленные тарифы
            for tariff in DEFAULT_TARIFFS:
                await db.execute(
                    "INSERT INTO tariffs (name, description, price) VALUES (?, ?, ?)",
                    (tariff["name"], tariff["description"], tariff["price"])
                )
            
            await db.commit()
            logger.info("Предустановленные тарифы загружены успешно.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке предустановленных тарифов: {e}")
        raise


async def init_models() -> None:
    """
    Инициализирует модели базы данных и загружает начальные данные.
    """
    try:
        # Загружаем вопросы для онбординга
        await load_onboarding_questions()
        
        # Загружаем предустановленные тарифы
        await load_default_tariffs()
        
        logger.info("Модели базы данных инициализированы успешно.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации моделей базы данных: {e}")
        raise