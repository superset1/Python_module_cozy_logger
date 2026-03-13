"""
Фикстуры для тестов
"""
import pytest
import os
import shutil
from cozy_logger.logger import Logger

@pytest.fixture(autouse=True)
def cleanup_logs():
    """
    Фикстура для очистки логов после тестов.
    Просто чистим файлы и сбрасываем синглтон.
    """
    # Сбрасываем синглтон перед тестом
    Logger._instance = None
    Logger._current_logger = None

    # Удаляем старые логи если есть
    if os.path.exists('logs'):
        shutil.rmtree('logs')

    yield  # здесь выполняется тест

    # Очищаем после теста
    if os.path.exists('logs'):
        shutil.rmtree('logs')

    # Снова сбрасываем синглтон
    Logger._instance = None
    Logger._current_logger = None
