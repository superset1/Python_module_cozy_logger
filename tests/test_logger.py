"""
Тесты для модуля cozy_logger.logger
"""
import pytest
import os
import logging
import time
from cozy_logger.logger import Logger

class TestLogger:
    """Тесты для класса Logger"""

    @pytest.mark.smoke
    def test_singleton_pattern(self):
        """Тест паттерна Singleton"""
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2
        assert id(logger1) == id(logger2)

    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_default_log_file_creation(self):
        """Тест создания логгера с файлом по умолчанию"""
        logger_instance = Logger()
        logger = logger_instance.get_logger()

        assert logger is not None
        assert isinstance(logger, logging.Logger)

        # Принудительно сбрасываем handlers чтобы гарантировать запись
        for handler in logger.handlers:
            handler.flush()

        # Небольшая задержка для записи на диск
        time.sleep(0.1)

        # Проверяем, что файл лога создался
        assert os.path.exists('logs')
        log_files = os.listdir('logs')
        assert len(log_files) == 1
        assert log_files[0].endswith('.log')
        assert log_files[0].startswith('test_')  # test_ потому что файл теста называется test_logger.py

    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_custom_log_file(self):
        """Тест создания логгера с пользовательским именем файла"""
        logger_instance = Logger()
        custom_log_name = "custom_test.log"
        logger = logger_instance.get_logger(log_file=custom_log_name)

        # Принудительно сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        assert os.path.exists(f'logs/{custom_log_name}')

        # Проверяем, что других файлов нет
        log_files = os.listdir('logs')
        assert len(log_files) == 1
        assert log_files[0] == custom_log_name

    @pytest.mark.unit
    def test_empty_log_file(self):
        """Тест с пустым именем файла (логи только в консоль)"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file="")

        assert logger is not None
        # Папка logs не должна создаваться
        assert not os.path.exists('logs')

    @pytest.mark.integration
    @pytest.mark.filesystem
    @pytest.mark.parametrize("verbose", [True, False])
    def test_verbose_mode(self, verbose):
        """Тест verbose режима"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(verbose=verbose)

        # Логируем сообщение
        test_message = "Test verbose message"
        logger.info(test_message)

        # Принудительно сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        # Читаем лог файл
        log_files = os.listdir('logs')
        assert len(log_files) > 0

        with open(f'logs/{log_files[0]}', 'r') as f:
            log_content = f.read()

        if verbose:
            assert 'Debug:' in log_content
        else:
            assert 'Debug:' not in log_content
        assert test_message in log_content

    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_log_levels(self):
        """Тест различных уровней логирования"""
        logger_instance = Logger()
        logger = logger_instance.get_logger()

        test_messages = {
            'debug': 'Debug message',
            'info': 'Info message',
            'warning': 'Warning message',
            'error': 'Error message',
            'critical': 'Critical message'
        }

        # Логируем сообщения
        logger.debug(test_messages['debug'])
        logger.info(test_messages['info'])
        logger.warning(test_messages['warning'])
        logger.error(test_messages['error'])
        logger.critical(test_messages['critical'])

        # Принудительно сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        log_files = os.listdir('logs')
        assert len(log_files) > 0

        with open(f'logs/{log_files[0]}', 'r') as f:
            log_content = f.read()

        # В вашем коде уровень логгера INFO, поэтому debug не пишется
        assert test_messages['debug'] not in log_content
        assert test_messages['info'] in log_content
        assert test_messages['warning'] in log_content
        assert test_messages['error'] in log_content
        assert test_messages['critical'] in log_content

    @pytest.mark.integration
    @pytest.mark.filesystem
    @pytest.mark.regression
    def test_multiple_logger_calls(self):
        """Тест множественных вызовов get_logger"""
        logger_instance = Logger()
        logger1 = logger_instance.get_logger(log_file="test1.log")
        logger2 = logger_instance.get_logger(log_file="test2.log")

        # Должен вернуться один и тот же экземпляр логгера
        assert logger1 is logger2

        # Принудительно сбрасываем handlers
        for handler in logger1.handlers:
            handler.flush()

        time.sleep(0.1)

        # Файлы должны создаваться
        log_files = os.listdir('logs')
        assert len(log_files) == 2
        assert "test1.log" in log_files
        assert "test2.log" in log_files

    @pytest.mark.unit
    def test_get_current_logger(self):
        """Тест получения текущего логгера"""
        logger_instance = Logger()

        # Сначала current_logger должен быть None
        assert Logger.get_current_logger() is None

        # Создаем логгер
        created_logger = logger_instance.get_logger()

        # Проверяем, что current_logger установлен
        current_logger = Logger.get_current_logger()
        assert current_logger is created_logger
        assert isinstance(current_logger, logging.Logger)

    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_log_directory_creation(self):
        """Тест создания директории для логов"""
        logger_instance = Logger()
        nested_log = "nested/test.log"
        logger = logger_instance.get_logger(log_file=nested_log)

        # Принудительно сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        assert os.path.exists('logs/nested')
        assert os.path.exists(f'logs/{nested_log}')

    @pytest.mark.unit
    def test_initialization_once(self):
        """Тест, что __init__ вызывается только один раз"""
        logger1 = Logger()
        first_filename = logger1.filename

        logger2 = Logger()
        second_filename = logger2.filename

        assert first_filename == second_filename
        assert hasattr(logger1, 'initialized')
        assert hasattr(logger2, 'initialized')

    @pytest.mark.integration
    @pytest.mark.filesystem
    @pytest.mark.parametrize("log_file,should_exist", [
        (None, True),        # файл по умолчанию - должен создаться
        ("", False),         # пустое имя - файл не создается
        ("test.log", True),  # конкретный файл - создается
        ("nested/test.log", True),  # с вложенной папкой - создается
    ])
    def test_log_file_creation_parametrized(self, log_file, should_exist):
        """Параметризованный тест для различных значений log_file"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file=log_file)

        # Принудительно сбрасываем handlers
        if logger.handlers:
            for handler in logger.handlers:
                handler.flush()

        time.sleep(0.1)

        if should_exist:
            assert os.path.exists('logs')
            if log_file is None:
                # При None должен создаться 1 файл
                assert len(os.listdir('logs')) == 1
            else:
                # При указанном имени должен создаться конкретный файл
                assert os.path.exists(f'logs/{log_file}')
        else:
            # При log_file="" папка logs не создается
            assert not os.path.exists('logs')

    @pytest.mark.unit
    def test_critical_logs_in_console(self, capsys):
        """Тест, что CRITICAL логи всегда идут в консоль"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file="test.log")

        test_message = "Critical test message"
        logger.critical(test_message)

        # Захватываем вывод в консоль
        captured = capsys.readouterr()

        # Проверяем, что сообщение было в stderr или stdout
        assert test_message in captured.err or test_message in captured.out

    @pytest.mark.integration
    @pytest.mark.filesystem
    @pytest.mark.regression
    def test_file_logging_without_console_duplication(self):
        """Тест, что в файле нет дублирования CRITICAL сообщений"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file="test.log")

        test_message = "Test message"
        logger.critical(test_message)
        logger.info(test_message)

        # Принудительно сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        # Читаем файл
        with open('logs/test.log', 'r') as f:
            lines = f.readlines()

        # Проверяем, что каждое сообщение только один раз
        critical_count = sum(1 for line in lines if 'CRITICAL' in line and test_message in line)
        info_count = sum(1 for line in lines if 'INFO' in line and test_message in line)

        assert critical_count == 1
        assert info_count == 1

    @pytest.mark.integration
    @pytest.mark.filesystem
    @pytest.mark.regression
    def test_logger_reuses_same_instance(self):
        """Тест, что логгер переиспользует тот же экземпляр"""
        logger_instance = Logger()
        logger1 = logger_instance.get_logger(log_file="test1.log")
        logger2 = logger_instance.get_logger(log_file="test2.log")

        assert logger1 is logger2

        # Проверяем, что обработчики обновились
        file_handlers = [h for h in logger1.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1  # Должен быть только последний файловый обработчик
        assert file_handlers[0].baseFilename.endswith('test2.log')

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_many_log_entries(self):
        """Тест с множеством записей (1000 сообщений)"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file="many_entries.log")

        start_time = time.time()

        # Пишем 1000 сообщений
        for i in range(1000):
            logger.info(f"Test message number {i}")

        # Сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверяем, что файл создался и имеет разумный размер
        assert os.path.exists('logs/many_entries.log')
        file_size = os.path.getsize('logs/many_entries.log')
        assert file_size > 0

        # Просто для информации (не обязательное утверждение)
        print(f"\nВремя записи 1000 сообщений: {execution_time:.2f} сек")
        print(f"Размер файла: {file_size} байт")

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.filesystem
    def test_nested_directories_deep(self):
        """Тест создания глубокой вложенности директорий"""
        logger_instance = Logger()

        # Создаем путь с 5 уровнями вложенности
        deep_path = "level1/level2/level3/level4/level5/test.log"
        logger = logger_instance.get_logger(log_file=deep_path)

        logger.info("Test message in deep directory")

        # Сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        # Проверяем, что все директории создались
        assert os.path.exists('logs/level1/level2/level3/level4/level5')
        assert os.path.exists(f'logs/{deep_path}')

    @pytest.mark.slow
    @pytest.mark.regression
    def test_logger_reused_many_times(self):
        """Многократное переиспользование логгера (100 раз)"""
        logger_instance = Logger()

        for i in range(100):
            logger = logger_instance.get_logger(log_file=f"test_{i}.log")
            logger.info(f"Test message {i}")

            # Проверяем, что это тот же экземпляр
            current = Logger.get_current_logger()
            assert current is logger

        # Сбрасываем и проверяем последний файл
        for handler in logger.handlers:
            handler.flush()

        time.sleep(0.1)

        # Проверяем, что создалось много файлов
        files = os.listdir('logs')
        assert len(files) == 100

        # Проверяем последний файл
        with open('logs/test_99.log', 'r') as f:
            content = f.read()
            assert "Test message 99" in content

    @pytest.mark.slow
    @pytest.mark.integration
    def test_large_log_messages(self):
        """Тест с большими сообщениями (10KB каждое)"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file="large_messages.log")

        # Создаем большое сообщение (10KB)
        large_message = "X" * 10 * 1024

        start_time = time.time()

        # Пишем 100 больших сообщений
        for i in range(100):
            # Пишем ПОЛНОЕ сообщение, не обрезая
            logger.info(f"Large message {i}: {large_message}")

        # Сбрасываем handlers
        for handler in logger.handlers:
            handler.flush()

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверяем размер файла (должен быть около 1MB)
        # 100 сообщений × ~10KB = ~1000KB = ~1MB
        file_size = os.path.getsize('logs/large_messages.log')
        expected_min_size = 900 * 1024  # 900KB минимум (с учетом служебной информации)
        expected_max_size = 1100 * 1024  # 1100KB максимум

        assert expected_min_size < file_size < expected_max_size, \
            f"Размер файла {file_size/1024:.1f}KB, ожидалось около 1000KB"

        print(f"\nВремя записи 100 больших сообщений (10KB каждое): {execution_time:.2f} сек")
        print(f"Размер файла: {file_size/1024:.1f} KB")
        print(f"Скорость записи: {100/execution_time:.1f} сообщений/сек")

    @pytest.mark.slow
    @pytest.mark.stress
    def test_stress_concurrent_logging(self):
        """Стресс-тест с быстрой последовательной записью"""
        logger_instance = Logger()
        logger = logger_instance.get_logger(log_file="stress.log")

        start_time = time.time()

        # Очень быстрая запись без задержек
        for i in range(5000):
            logger.info(f"Fast message {i}")
            if i % 1000 == 0:
                # Периодически сбрасываем
                for handler in logger.handlers:
                    handler.flush()

        # Финальный сброс
        for handler in logger.handlers:
            handler.flush()

        end_time = time.time()
        execution_time = end_time - start_time

        # Проверяем, что запись была достаточно быстрой
        messages_per_second = 5000 / execution_time
        print(f"\nЗапись 5000 сообщений за {execution_time:.2f} сек")
        print(f"Скорость: {messages_per_second:.0f} сообщений/сек")

        assert messages_per_second > 100  # минимум 100 сообщений в секунду
