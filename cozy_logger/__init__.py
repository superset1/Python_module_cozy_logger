from importlib.metadata import version
from .logger import Logger

__version__ = version("cozy_logger")
__all__ = ['Logger']
