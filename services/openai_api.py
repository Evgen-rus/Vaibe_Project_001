"""
Модуль для интеграции с OpenAI API.
"""
import json
import logging
from typing import Dict, List, Any, Optional

import openai
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TARIFF_PROMPT

# Инициализация логгера
logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def analyze_onboarding_answers(answers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Анализирует ответы пользователя на вопросы онбординга и рекомендует тариф.
    
    Args:
        answers: Список словарей с ответами пользователя
        
    Returns:
        Словарь с рекомендованными тарифами и объяснением выбора
    """
    try:
        # Форматируем ответы для запроса к OpenAI
        formatted_answers = "\n".join([f"Вопрос: {answer['question_text']}\nОтвет: {answer['answer']}" 
                                  for answer in answers])
        
        # Подготавливаем промпт
        prompt = OPENAI_TARIFF_PROMPT.format(answers=formatted_answers)
        
        # Создаем запрос к OpenAI API с structured outputs
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Ты аналитик по подбору тарифов для бизнеса."},
                {"role": "user", "content": prompt}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "recommend_tariff",
                    "description": "Рекомендует тарифы на основе ответов пользователя",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tariffs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "price": {"type": "number"},
                                        "features": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    },
                                    "required": ["name", "description", "price", "features"]
                                }
                            },
                            "recommendation": {"type": "string"},
                            "explanation": {"type": "string"}
                        },
                        "required": ["tariffs", "recommendation", "explanation"]
                    }
                }
            }],
            tool_choice={"type": "function", "function": {"name": "recommend_tariff"}}
        )
        
        # Извлекаем ответ
        tool_call = response.choices[0].message.tool_calls[0]
        tariff_data = json.loads(tool_call.function.arguments)
        
        logger.info(f"OpenAI успешно проанализировал ответы и предложил тарифы.")
        return tariff_data
    except Exception as e:
        logger.error(f"Ошибка при анализе ответов через OpenAI: {e}")
        return None 