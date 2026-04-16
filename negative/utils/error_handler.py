"""
Error handling utilities for Negative Language
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ErrorLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

@dataclass
class NegativeError(Exception):
    """Base exception for Negative Language"""
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    level: ErrorLevel = ErrorLevel.ERROR
    
    def __str__(self):
        if self.line and self.column:
            return f"{self.level.value}: {self.message} at line {self.line}, column {self.column}"
        return f"{self.level.value}: {self.message}"

class ErrorHandler:
    """Centralized error handling"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def add_error(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        error = NegativeError(message, line, column, ErrorLevel.ERROR)
        self.errors.append(error)
        return error
        
    def add_warning(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        warning = NegativeError(message, line, column, ErrorLevel.WARNING)
        self.warnings.append(warning)
        return warning
        
    def has_errors(self) -> bool:
        return len(self.errors) > 0
        
    def print_errors(self):
        for error in self.errors:
            print(error)
        for warning in self.warnings:
            print(warning)
            
    def clear(self):
        self.errors.clear()
        self.warnings.clear()