"""
Модуль с определением FSM-состояний для бота.
"""
from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """
    Группа состояний для процесса онбординга.
    """
    # Ожидание начала онбординга
    waiting_for_start = State()
    
    # Вопросы онбординга
    business_sphere = State()
    usage_volume = State()
    budget = State()
    team_size = State()
    current_tools = State()
    
    # Подбор тарифа
    tariff_selection = State()
    
    # Дополнительные действия
    contact_manager = State()
    show_details = State()


class TrialStates(StatesGroup):
    """
    Группа состояний для управления триал-периодом.
    """
    # Активный триал
    active_trial = State()
    
    # Триал заканчивается
    ending_trial = State()
    
    # Триал закончился
    ended_trial = State()
    
    # Переход на платную версию
    upgrade_to_paid = State() 