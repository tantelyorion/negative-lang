"""
Logging utilities for Negative Language
"""

from enum import Enum
from datetime import datetime
from typing import Optional

class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

class Logger:
    """Simple logger for Negative Language"""
    
    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level
        self.quiet = False
        
    def set_quiet(self, quiet: bool):
        self.quiet = quiet
        
    def _log(self, level: LogLevel, message: str):
        if level.value >= self.level.value and not self.quiet:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {level.name}: {message}")
            
    def debug(self, message: str):
        self._log(LogLevel.DEBUG, message)
        
    def info(self, message: str):
        self._log(LogLevel.INFO, message)
        
    def warning(self, message: str):
        self._log(LogLevel.WARNING, message)
        
    def error(self, message: str):
        self._log(LogLevel.ERROR, message)
        
    def fatal(self, message: str):
        self._log(LogLevel.FATAL, message)