"""
Инициализационный файл для пакета handlers.
Импортирует все роутеры для обработчиков сообщений.
"""
from .onboarding import onboarding_router
from .trial import trial_router
from .admin import admin_router

__all__ = ["onboarding_router", "trial_router", "admin_router"] 