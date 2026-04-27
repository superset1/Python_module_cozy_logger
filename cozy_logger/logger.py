import logging
import datetime
import inspect
import os

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
            self.log_file_default = f"{os.path.basename(self.filename).split('.')[0]}_{datetime.datetime.now().strftime('%Y_%m_%dT%H_%M_%S')}.log"
            self.initialized = True
            self.LOG_FILE_INFO = None

    def get_logger(self, *, log_file: str=None, log_level: str="INFO", verbose: bool=False):
        LOG_NAME = __name__

        if verbose:
            LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s Debug: %(name)s %(funcName)s %(lineno)d %(module)s %(process)d %(processName)s %(relativeCreated)d %(thread)d %(threadName)s %(taskName)s'
        else:
            LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

        # Convert string to logging constant
        log_level_int = getattr(logging, log_level.upper(), logging.INFO)

        # Custom logger
        logger = logging.getLogger(LOG_NAME)
        log_formatter = logging.Formatter(LOG_FORMAT)
        logger.setLevel(log_level_int)

        logger.handlers.clear()

        # Default file name only if log_file is None (not '')
        if log_file is None:
            log_file = self.log_file_default

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
