import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    POLICY = "POLICY"
    SYSTEM = "SYSTEM"
    DENY = "DENY"
    ALLOW = "ALLOW"
    IF = "IF"
    ELSE = "ELSE"
    
    # Operators
    EXCLAMATION = "EXCLAMATION"  # !
    EQUALS = "EQUALS"  # =
    NOT_EQUALS = "NOT_EQUALS"  # !=
    
    # Delimiters
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    SEMICOLON = "SEMICOLON"  # ;
    COLON = "COLON"  # :
    
    # Values
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    
    # Special
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            char = self.current_char()
            
            # Skip whitespace but track for indentation
            if char.isspace():
                if char == '\n':
                    self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.col))
                    self.line += 1
                    self.col = 1
                    self.pos += 1
                    continue
                elif char == ' ':
                    self.pos += 1
                    self.col += 1
                    continue
                elif char == '\t':
                    self.pos += 1
                    self.col += 4
                    continue
                    
            # Comments
            elif char == '#':
                self.skip_comment()
                continue
                
            # Operators
            elif char == '!':
                if self.peek() == '=':
                    self.tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.line, self.col))
                    self.pos += 2
                    self.col += 2
                else:
                    self.tokens.append(Token(TokenType.EXCLAMATION, '!', self.line, self.col))
                    self.pos += 1
                    self.col += 1
                continue
                
            # Delimiters
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, ';', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
            elif char == '=':
                self.tokens.append(Token(TokenType.EQUALS, '=', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.col))
                self.pos += 1
                self.col += 1
                continue
                
            # Strings
            elif char in ['"', "'"]:
                self.tokens.append(self.read_string(char))
                continue
                
            # Numbers
            elif char.isdigit():
                self.tokens.append(self.read_number())
                continue
                
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
                
            else:
                raise SyntaxError(f"Unknown character '{char}' at line {self.line}, column {self.col}")
                
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return self.tokens
    
    def current_char(self) -> str:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return '\0'
    
    def peek(self) -> str:
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return '\0'
    
    def skip_comment(self):
        while self.pos < len(self.source) and self.current_char() != '\n':
            self.pos += 1
            self.col += 1
    
    def read_string(self, quote_char: str) -> Token:
        start_line = self.line
        start_col = self.col
        self.pos += 1  # Skip opening quote
        self.col += 1
        string_value = ""
        
        while self.pos < len(self.source) and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.pos += 1
                self.col += 1
                if self.pos < len(self.source):
                    escape_char = self.current_char()
                    if escape_char == 'n':
                        string_value += '\n'
                    elif escape_char == 't':
                        string_value += '\t'
                    elif escape_char == '\\':
                        string_value += '\\'
                    elif escape_char == quote_char:
                        string_value += quote_char
                    else:
                        string_value += escape_char
            else:
                string_value += self.current_char()
            self.pos += 1
            self.col += 1
            
        if self.pos >= len(self.source):
            raise SyntaxError(f"Unterminated string at line {start_line}, column {start_col}")
            
        self.pos += 1  # Skip closing quote
        self.col += 1
        return Token(TokenType.STRING, string_value, start_line, start_col)
    
    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.col
        num_str = ""
        is_float = False
        
        while self.pos < len(self.source) and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if is_float:
                    break
                is_float = True
            num_str += self.current_char()
            self.pos += 1
            self.col += 1
            
        if is_float:
            return Token(TokenType.NUMBER, float(num_str), start_line, start_col)
        return Token(TokenType.NUMBER, int(num_str), start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.col
        ident = ""
        
        while self.pos < len(self.source) and (self.current_char().isalnum() or self.current_char() == '_'):
            ident += self.current_char()
            self.pos += 1
            self.col += 1
            
        # Check for keywords
        keywords = {
            'policy': TokenType.POLICY,
            'system': TokenType.SYSTEM,
            'deny': TokenType.DENY,
            'allow': TokenType.ALLOW,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN
        }
        
        token_type = keywords.get(ident, TokenType.IDENTIFIER)
        value = ident if token_type != TokenType.BOOLEAN else (ident == 'true')
        
        return Token(token_type, value, start_line, start_col)