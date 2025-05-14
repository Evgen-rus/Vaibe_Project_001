"""
Обработчики для процесса онбординга пользователей.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from config import WELCOME_MESSAGE, ONBOARDING_QUESTIONS
from database import db
from keyboards.reply import get_start_keyboard, get_onboarding_options_keyboard
from keyboards.inline import get_tariff_selection_keyboard
from services.openai_api import analyze_onboarding_answers
from utils.states import OnboardingStates

# Инициализация логгера
logger = logging.getLogger(__name__)

# Создаем роутер для обработчиков онбординга
onboarding_router = Router()


@onboarding_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /start, начинает онбординг.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Сбрасываем состояние на случай, если пользователь начинает заново
    await state.clear()
    
    # Добавляем пользователя в базу данных или обновляем информацию
    await db.add_user(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Отправляем приветственное сообщение с клавиатурой
    await message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=get_start_keyboard()
    )
    
    # Устанавливаем состояние ожидания начала теста
    await state.set_state(OnboardingStates.waiting_for_start)


@onboarding_router.message(OnboardingStates.waiting_for_start, F.text == "Начать тест")
async def onboarding_start(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает нажатие кнопки "Начать тест", запускает первый вопрос.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Получаем первый вопрос
    first_question = ONBOARDING_QUESTIONS[0]
    
    # Подготавливаем клавиатуру, если есть варианты ответов
    reply_markup = None
    if first_question.get("type") == "options" and "options" in first_question:
        reply_markup = get_onboarding_options_keyboard(first_question["options"])
    
    # Отправляем первый вопрос
    await message.answer(
        text=first_question["text"],
        reply_markup=reply_markup
    )
    
    # Устанавливаем состояние первого вопроса
    await state.set_state(OnboardingStates.business_sphere)


@onboarding_router.message(OnboardingStates.business_sphere)
async def process_business_sphere(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ответ на вопрос о сфере бизнеса.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Получаем ответ пользователя
    user_answer = message.text
    
    # Сохраняем ответ в базу данных
    await db.save_onboarding_answer(
        user_id=message.from_user.id,
        question_id=1,  # ID вопроса о сфере бизнеса
        answer=user_answer
    )
    
    # Получаем следующий вопрос об объеме использования
    next_question = ONBOARDING_QUESTIONS[1]  # Вопрос об объеме использования
    
    # Подготавливаем клавиатуру с вариантами ответов
    reply_markup = get_onboarding_options_keyboard(next_question["options"])
    
    # Отправляем следующий вопрос
    await message.answer(
        text=next_question["text"],
        reply_markup=reply_markup
    )
    
    # Устанавливаем следующее состояние
    await state.set_state(OnboardingStates.usage_volume)


@onboarding_router.message(OnboardingStates.usage_volume)
async def process_usage_volume(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ответ на вопрос об объеме использования.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Получаем ответ пользователя
    user_answer = message.text
    
    # Сохраняем ответ в базу данных
    await db.save_onboarding_answer(
        user_id=message.from_user.id,
        question_id=2,  # ID вопроса об объеме использования
        answer=user_answer
    )
    
    # Получаем следующий вопрос о бюджете
    next_question = ONBOARDING_QUESTIONS[2]  # Вопрос о бюджете
    
    # Подготавливаем клавиатуру с вариантами ответов
    reply_markup = get_onboarding_options_keyboard(next_question["options"])
    
    # Отправляем следующий вопрос
    await message.answer(
        text=next_question["text"],
        reply_markup=reply_markup
    )
    
    # Устанавливаем следующее состояние
    await state.set_state(OnboardingStates.budget)


@onboarding_router.message(OnboardingStates.budget)
async def process_budget(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ответ на вопрос о бюджете.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Получаем ответ пользователя
    user_answer = message.text
    
    # Сохраняем ответ в базу данных
    await db.save_onboarding_answer(
        user_id=message.from_user.id,
        question_id=3,  # ID вопроса о бюджете
        answer=user_answer
    )
    
    # Получаем следующий вопрос о размере команды
    next_question = ONBOARDING_QUESTIONS[3]  # Вопрос о размере команды
    
    # Подготавливаем клавиатуру с вариантами ответов
    reply_markup = get_onboarding_options_keyboard(next_question["options"])
    
    # Отправляем следующий вопрос
    await message.answer(
        text=next_question["text"],
        reply_markup=reply_markup
    )
    
    # Устанавливаем следующее состояние
    await state.set_state(OnboardingStates.team_size)


@onboarding_router.message(OnboardingStates.team_size)
async def process_team_size(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ответ на вопрос о размере команды.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Получаем ответ пользователя
    user_answer = message.text
    
    # Сохраняем ответ в базу данных
    await db.save_onboarding_answer(
        user_id=message.from_user.id,
        question_id=4,  # ID вопроса о размере команды
        answer=user_answer
    )
    
    # Получаем следующий вопрос об используемых инструментах
    next_question = ONBOARDING_QUESTIONS[4]  # Вопрос об используемых инструментах
    
    # Отправляем следующий вопрос (текстовый ввод, без клавиатуры)
    await message.answer(text=next_question["text"])
    
    # Устанавливаем следующее состояние
    await state.set_state(OnboardingStates.current_tools)


@onboarding_router.message(OnboardingStates.current_tools)
async def process_current_tools(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ответ на вопрос об используемых инструментах.
    
    Args:
        message: Сообщение от пользователя
        state: Контекст FSM
    """
    # Получаем ответ пользователя
    user_answer = message.text
    
    # Сохраняем ответ в базу данных
    await db.save_onboarding_answer(
        user_id=message.from_user.id,
        question_id=5,  # ID вопроса об используемых инструментах
        answer=user_answer
    )
    
    # Отправляем сообщение о том, что анализируем ответы
    await message.answer(
        "Спасибо за ваши ответы! Анализирую информацию и подбираю оптимальный тариф..."
    )
    
    # Получаем все ответы пользователя
    user_answers = await db.get_user_answers(message.from_user.id)
    
    # Анализируем ответы и получаем рекомендации по тарифам
    tariff_data = await analyze_onboarding_answers(user_answers)
    
    # Сохраняем данные о тарифах в FSM контекст
    await state.update_data(tariff_data=tariff_data)
    
    # Формируем сообщение с рекомендацией
    if tariff_data:
        tariff_names = [tariff["name"] for tariff in tariff_data["tariffs"]]
        recommendation = tariff_data["recommendation"]
        explanation = tariff_data["explanation"]
        
        message_text = (
            f"Я рекомендую тариф «{recommendation}»!\n\n"
            f"{explanation}\n\n"
            "Выберите один из предложенных вариантов:"
        )
        
        # Клавиатура для выбора тарифа
        keyboard = get_tariff_selection_keyboard(tariff_names)
        
        # Отправляем сообщение с рекомендацией и клавиатурой
        await message.answer(text=message_text, reply_markup=keyboard)
        
        # Устанавливаем состояние выбора тарифа
        await state.set_state(OnboardingStates.tariff_selection)
    else:
        # Если произошла ошибка при анализе ответов
        await message.answer(
            "К сожалению, не удалось подобрать тариф на основе ваших ответов. "
            "Пожалуйста, свяжитесь с менеджером для получения персональной консультации."
        )


@onboarding_router.callback_query(OnboardingStates.tariff_selection, F.data.startswith("select_tariff:"))
async def select_tariff(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает выбор тарифа пользователем.
    
    Args:
        callback: Callback-запрос от нажатия на инлайн-кнопку
        state: Контекст FSM
    """
    # Получаем индекс выбранного тарифа
    tariff_index = int(callback.data.split(":")[1])
    
    # Получаем данные о тарифах из FSM контекста
    data = await state.get_data()
    tariff_data = data.get("tariff_data")
    
    if tariff_data and tariff_index < len(tariff_data["tariffs"]):
        selected_tariff = tariff_data["tariffs"][tariff_index]
        
        # Отправляем сообщение о выбранном тарифе
        await callback.message.edit_text(
            f"Вы выбрали тариф «{selected_tariff['name']}»!\n\n"
            f"Стоимость: {selected_tariff['price']} руб./мес.\n\n"
            "Ваш триал-период активирован на 14 дней. За это время вы сможете оценить все возможности системы.\n\n"
            "По любым вопросам обращайтесь к нашему менеджеру."
        )
        
        # Сбрасываем состояние FSM
        await state.clear()
    else:
        await callback.answer("Произошла ошибка при выборе тарифа. Попробуйте еще раз.")


@onboarding_router.callback_query(OnboardingStates.tariff_selection, F.data.startswith("tariff_details:"))
async def show_tariff_details(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Показывает подробную информацию о выбранном тарифе.
    
    Args:
        callback: Callback-запрос от нажатия на инлайн-кнопку
        state: Контекст FSM
    """
    # Получаем индекс выбранного тарифа
    tariff_index = int(callback.data.split(":")[1])
    
    # Получаем данные о тарифах из FSM контекста
    data = await state.get_data()
    tariff_data = data.get("tariff_data")
    
    if tariff_data and tariff_index < len(tariff_data["tariffs"]):
        selected_tariff = tariff_data["tariffs"][tariff_index]
        
        # Формируем список функций
        features_list = "\n".join([f"✅ {feature}" for feature in selected_tariff["features"]])
        
        # Формируем текст с подробностями о тарифе
        details_text = (
            f"🔍 Подробная информация о тарифе «{selected_tariff['name']}»\n\n"
            f"💰 Стоимость: {selected_tariff['price']} руб./мес.\n\n"
            f"📝 Описание: {selected_tariff['description']}\n\n"
            f"📋 Включенные функции:\n{features_list}"
        )
        
        # Отправляем сообщение с подробностями и клавиатурой для выбора тарифа
        from keyboards.inline import get_tariff_details_keyboard
        await callback.message.edit_text(
            text=details_text,
            reply_markup=get_tariff_details_keyboard(tariff_index)
        )
    else:
        await callback.answer("Произошла ошибка при получении информации о тарифе. Попробуйте еще раз.")


@onboarding_router.callback_query(OnboardingStates.tariff_selection, F.data == "back_to_tariffs")
async def back_to_tariffs(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает пользователя к списку тарифов.
    
    Args:
        callback: Callback-запрос от нажатия на инлайн-кнопку
        state: Контекст FSM
    """
    # Получаем данные о тарифах из FSM контекста
    data = await state.get_data()
    tariff_data = data.get("tariff_data")
    
    if tariff_data:
        tariff_names = [tariff["name"] for tariff in tariff_data["tariffs"]]
        recommendation = tariff_data["recommendation"]
        explanation = tariff_data["explanation"]
        
        message_text = (
            f"Я рекомендую тариф «{recommendation}»!\n\n"
            f"{explanation}\n\n"
            "Выберите один из предложенных вариантов:"
        )
        
        # Клавиатура для выбора тарифа
        keyboard = get_tariff_selection_keyboard(tariff_names)
        
        # Отправляем сообщение с рекомендацией и клавиатурой
        await callback.message.edit_text(text=message_text, reply_markup=keyboard)
    else:
        await callback.answer("Произошла ошибка при возвращении к списку тарифов. Попробуйте заново.")


@onboarding_router.callback_query(F.data == "contact_manager")
async def contact_manager(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает запрос на связь с менеджером.
    
    Args:
        callback: Callback-запрос от нажатия на инлайн-кнопку
        state: Контекст FSM
    """
    await callback.message.edit_text(
        "Наш менеджер свяжется с вами в ближайшее время!\n\n"
        "Также вы можете напрямую написать нам по адресу: manager@example.com"
    )
    
    # Сбрасываем состояние FSM
    await state.clear() 