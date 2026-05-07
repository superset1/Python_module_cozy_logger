import logging
import datetime
import inspect
import os
from zoneinfo import ZoneInfo

class Logger(object):
    '''Custom Logger - Singleton'''

    _instance = None
    _current_logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.frame = inspect.currentframe().f_back
            self.filename = self.frame.f_code.co_filename
            self.initialized = True
            self.LOG_FILE_INFO = None

    def _get_log_filename(self, timezone=None):
        if timezone:
            tz = ZoneInfo(timezone)
            now = datetime.datetime.now(tz)
        else:
            now = datetime.datetime.now().astimezone()

        return f"{os.path.basename(self.filename).split('.')[0]}_{now.strftime('%Y_%m_%dT%H_%M_%S')}.log"

    def get_logger(self, *, log_file: str=None, log_level: str="INFO", timezone: str=None, verbose: bool=False):
        LOG_NAME = __name__

        if verbose:
            LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s Debug: %(name)s %(funcName)s %(lineno)d %(module)s %(process)d %(processName)s %(relativeCreated)d %(thread)d %(threadName)s %(taskName)s'
        else:
            LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

        # Convert string to logging constant
        log_level_int = getattr(logging, log_level.upper(), logging.INFO)

        # Custom formatter with timezone support
        class TimezoneFormatter(logging.Formatter):
            def __init__(self, fmt, timezone=None):
                super().__init__(fmt)
                self.tz = ZoneInfo(timezone) if timezone else None

            def formatTime(self, record, datefmt=None):
                dt = datetime.datetime.now(self.tz) if self.tz else datetime.datetime.now().astimezone()
                if datefmt:
                    return dt.strftime(datefmt)
                return dt.isoformat()

        # Custom logger
        logger = logging.getLogger(LOG_NAME)
        log_formatter = TimezoneFormatter(LOG_FORMAT, timezone)
        logger.setLevel(log_level_int)

        logger.handlers.clear()

        # Default file name only if log_file is None (not '')
        if log_file is None:
            log_file = self._get_log_filename(timezone)

        if log_file:
            # File output
            self.LOG_FILE_INFO = f"logs/{log_file}"
            log_dir = os.path.dirname(self.LOG_FILE_INFO)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(self.LOG_FILE_INFO, encoding='utf-8', mode='a')
            file_handler.setFormatter(log_formatter)
            file_handler.setLevel(log_level_int)
            logger.addHandler(file_handler)

            # Duplicate critical logs in console
            console_level = logging.CRITICAL
        else:
            # Console output only if log_file == ''
            console_level = log_level_int
            self.LOG_FILE_INFO = ""

        # Console config
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(console_level)
        logger.addHandler(stream_handler)

        # Change log level
        def log_level(log_level: str):
            log_level_int = getattr(logging, log_level.upper(), logging.INFO)
            logger.setLevel(log_level_int)
            if log_file:
                # File output
                file_handler.setLevel(log_level_int)
            else:
                # Console output if log_file == ''
                stream_handler.setLevel(log_level_int)

        logger.log_level = log_level

        self.__class__._current_logger = logger

        return logger

    @classmethod
    def get_current_logger(cls):
        '''Get current logger'''
        return cls._current_logger
