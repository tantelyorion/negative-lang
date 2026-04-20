"""
Negative Language - Programming by Negation
A language where everything is denied by default.
"""

from .cli import NegativeCLI, main
from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .ast import Program, Policy, SystemBlock, Rule
from .interpreter import Interpreter
from .rules_engine import RulesEngine, RuleSet

__version__ = "1.1.0"
__all__ = [
    "NegativeCLI",
    "main",
    "Lexer",
    "Token",
    "TokenType",
    "Parser",
    "Program",
    "Policy",
    "SystemBlock",
    "Rule",
    "Interpreter",
    "RulesEngine",
    "RuleSet",
]