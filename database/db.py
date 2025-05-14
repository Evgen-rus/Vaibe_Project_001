"""
Модуль для работы с базой данных SQLite.
"""
import sqlite3
import logging
import asyncio
import aiosqlite
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

from config import DATABASE_PATH, TRIAL_PERIOD_DAYS

# Инициализация логгера
logger = logging.getLogger(__name__)

# SQL-запросы для создания таблиц
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_end_date TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    tariff_id INTEGER,
    FOREIGN KEY (tariff_id) REFERENCES tariffs(id)
);
"""

CREATE_ONBOARDING_QUESTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS onboarding_questions (
    id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL
);
"""

CREATE_ONBOARDING_ANSWERS_TABLE = """
CREATE TABLE IF NOT EXISTS onboarding_answers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    answer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (question_id) REFERENCES onboarding_questions(id)
);
"""

CREATE_TARIFFS_TABLE = """
CREATE TABLE IF NOT EXISTS tariffs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL
);
"""

# Запросы для работы с пользователями
INSERT_USER = """
INSERT OR REPLACE INTO users (user_id, chat_id, username, first_name, last_name, trial_end_date, is_active) 
VALUES (?, ?, ?, ?, ?, ?, ?);
"""

GET_USER = """
SELECT * FROM users WHERE user_id = ?;
"""

UPDATE_TRIAL_END_DATE = """
UPDATE users SET trial_end_date = ? WHERE user_id = ?;
"""

UPDATE_USER_STATUS = """
UPDATE users SET is_active = ? WHERE user_id = ?;
"""

UPDATE_USER_TARIFF = """
UPDATE users SET tariff_id = ? WHERE user_id = ?;
"""

GET_USERS_WITH_ENDING_TRIAL = """
SELECT * FROM users 
WHERE trial_end_date IS NOT NULL 
AND date(trial_end_date) = date('now', '+' || ? || ' days')
AND is_active = TRUE;
"""

GET_USERS_WITH_ENDED_TRIAL = """
SELECT * FROM users 
WHERE trial_end_date IS NOT NULL 
AND date(trial_end_date) < date('now')
AND is_active = TRUE;
"""

# Запросы для онбординга
INSERT_ONBOARDING_ANSWER = """
INSERT INTO onboarding_answers (user_id, question_id, answer) 
VALUES (?, ?, ?);
"""

GET_USER_ANSWERS = """
SELECT q.id, q.question_text, a.answer 
FROM onboarding_answers a
JOIN onboarding_questions q ON a.question_id = q.id
WHERE a.user_id = ?
ORDER BY q.id;
"""

# Запросы для работы с тарифами
INSERT_TARIFF = """
INSERT INTO tariffs (name, description, price) 
VALUES (?, ?, ?);
"""

GET_TARIFF = """
SELECT * FROM tariffs WHERE id = ?;
"""

GET_ALL_TARIFFS = """
SELECT * FROM tariffs;
"""

# Запросы для админ-панели
GET_ACTIVE_USERS_COUNT = """
SELECT COUNT(*) FROM users WHERE is_active = TRUE;
"""

GET_CONVERSION_RATE = """
SELECT 
    (SELECT COUNT(*) FROM users WHERE tariff_id IS NOT NULL) * 100.0 / 
    (SELECT COUNT(*) FROM users) AS conversion_rate;
"""

GET_POPULAR_TARIFFS = """
SELECT t.name, COUNT(*) as user_count 
FROM users u
JOIN tariffs t ON u.tariff_id = t.id
GROUP BY t.id
ORDER BY user_count DESC;
"""


async def init_db() -> None:
    """
    Инициализирует базу данных, создает таблицы если они не существуют.
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(CREATE_USERS_TABLE)
            await db.execute(CREATE_ONBOARDING_QUESTIONS_TABLE)
            await db.execute(CREATE_ONBOARDING_ANSWERS_TABLE)
            await db.execute(CREATE_TARIFFS_TABLE)
            await db.commit()
            logger.info("База данных инициализирована успешно.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


async def add_user(user_id: int, chat_id: int, username: str = None, 
                  first_name: str = None, last_name: str = None) -> None:
    """
    Добавляет нового пользователя в базу данных или обновляет существующего.
    
    Args:
        user_id: ID пользователя в Telegram
        chat_id: ID чата с пользователем
        username: Имя пользователя в Telegram
        first_name: Имя пользователя
        last_name: Фамилия пользователя
    """
    # Рассчитываем дату окончания триала
    trial_end_date = (datetime.datetime.now() + 
                     datetime.timedelta(days=TRIAL_PERIOD_DAYS)).isoformat()
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                INSERT_USER,
                (user_id, chat_id, username, first_name, last_name, trial_end_date, True)
            )
            await db.commit()
            logger.info(f"Пользователь {user_id} добавлен/обновлен в базе данных.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
        raise


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает информацию о пользователе по его ID.
    
    Args:
        user_id: ID пользователя в Telegram
        
    Returns:
        Dict с информацией о пользователе или None, если пользователь не найден
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = sqlite3.Row
            async with db.execute(GET_USER, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя {user_id}: {e}")
        return None


async def save_onboarding_answer(user_id: int, question_id: int, answer: str) -> None:
    """
    Сохраняет ответ пользователя на вопрос онбординга.
    
    Args:
        user_id: ID пользователя
        question_id: ID вопроса
        answer: Ответ пользователя
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                INSERT_ONBOARDING_ANSWER,
                (user_id, question_id, answer)
            )
            await db.commit()
            logger.info(f"Ответ пользователя {user_id} на вопрос {question_id} сохранен.")
    except Exception as e:
        logger.error(f"Ошибка при сохранении ответа: {e}")
        raise


async def get_user_answers(user_id: int) -> List[Dict[str, Any]]:
    """
    Получает все ответы пользователя на вопросы онбординга.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Список словарей с ответами пользователя
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = sqlite3.Row
            async with db.execute(GET_USER_ANSWERS, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении ответов пользователя {user_id}: {e}")
        return []


async def update_trial_status(user_id: int, is_active: bool) -> None:
    """
    Обновляет статус активности пользователя (для управления триал-периодом).
    
    Args:
        user_id: ID пользователя
        is_active: Статус активности (True - активен, False - не активен)
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(UPDATE_USER_STATUS, (is_active, user_id))
            await db.commit()
            logger.info(f"Статус пользователя {user_id} обновлен на {is_active}.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса пользователя {user_id}: {e}")
        raise


async def update_user_tariff(user_id: int, tariff_id: int) -> None:
    """
    Обновляет выбранный тариф пользователя.
    
    Args:
        user_id: ID пользователя
        tariff_id: ID тарифа
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(UPDATE_USER_TARIFF, (tariff_id, user_id))
            await db.commit()
            logger.info(f"Тариф пользователя {user_id} обновлен на {tariff_id}.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении тарифа пользователя {user_id}: {e}")
        raise


async def get_users_with_ending_trial(days_before: int = 1) -> List[Dict[str, Any]]:
    """
    Получает список пользователей, у которых триал-период заканчивается через указанное количество дней.
    
    Args:
        days_before: За сколько дней до окончания триала выбирать пользователей
        
    Returns:
        Список словарей с информацией о пользователях
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = sqlite3.Row
            async with db.execute(GET_USERS_WITH_ENDING_TRIAL, (days_before,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении пользователей с заканчивающимся триалом: {e}")
        return []


async def get_users_with_ended_trial() -> List[Dict[str, Any]]:
    """
    Получает список пользователей, у которых триал-период уже закончился.
    
    Returns:
        Список словарей с информацией о пользователях
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = sqlite3.Row
            async with db.execute(GET_USERS_WITH_ENDED_TRIAL) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении пользователей с закончившимся триалом: {e}")
        return []


async def get_admin_stats() -> Dict[str, Any]:
    """
    Получает статистику для админ-панели.
    
    Returns:
        Словарь со статистикой
    """
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Активные пользователи
            async with db.execute(GET_ACTIVE_USERS_COUNT) as cursor:
                active_users = await cursor.fetchone()
                active_users_count = active_users[0] if active_users else 0
            
            # Конверсия в оплату
            async with db.execute(GET_CONVERSION_RATE) as cursor:
                conversion = await cursor.fetchone()
                conversion_rate = conversion[0] if conversion else 0
            
            # Популярные тарифы
            db.row_factory = sqlite3.Row
            async with db.execute(GET_POPULAR_TARIFFS) as cursor:
                tariff_rows = await cursor.fetchall()
                popular_tariffs = [dict(row) for row in tariff_rows]
            
            return {
                "active_users_count": active_users_count,
                "conversion_rate": conversion_rate,
                "popular_tariffs": popular_tariffs
            }
    except Exception as e:
        logger.error(f"Ошибка при получении статистики для админ-панели: {e}")
        return {
            "active_users_count": 0,
            "conversion_rate": 0,
            "popular_tariffs": []
        } 