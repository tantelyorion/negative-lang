#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LEXER FOR NEGATIVE LANGUAGE
Convertit le code source en une liste de tokens
Version: 1.1.0
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class TokenType(Enum):
    """Tous les types de tokens possibles dans Negative"""
    
    # Mots-clés
    POLICY = "POLICY"
    SYSTEM = "SYSTEM"
    DENY = "DENY"
    ALLOW = "ALLOW"
    IF = "IF"
    ELSE = "ELSE"
    LET = "LET"
    IMPORT = "IMPORT"
    AS = "AS"
    FN = "FN"
    RETURN = "RETURN"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IN = "IN"
    
    # Opérateurs
    EXCLAMATION = "EXCLAMATION"      # !
    EQUALS = "EQUALS"                # =
    EQUALS_EQUALS = "EQUALS_EQUALS"  # ==
    NOT_EQUALS = "NOT_EQUALS"        # !=
    LESS_THAN = "LESS_THAN"          # <
    GREATER_THAN = "GREATER_THAN"    # >
    LESS_EQUAL = "LESS_EQUAL"        # <=
    GREATER_EQUAL = "GREATER_EQUAL"  # >=
    PLUS = "PLUS"                    # +
    MINUS = "MINUS"                  # -
    STAR = "STAR"                    # *
    SLASH = "SLASH"                  # /
    ARROW = "ARROW"                  # ->
    COLON = "COLON"                  # :
    SEMICOLON = "SEMICOLON"          # ;
    COMMA = "COMMA"                  # ,
    DOT = "DOT"                      # .
    
    # Délimiteurs
    LBRACE = "LBRACE"    # {
    RBRACE = "RBRACE"    # }
    LPAREN = "LPAREN"    # (
    RPAREN = "RPAREN"    # )
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    
    # Types
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    
    # Spéciaux
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    
    # Directives
    AT = "AT"            # @


@dataclass
class Token:
    """Représente un token avec sa position dans le code source"""
    type: TokenType
    value: Any
    line: int
    column: int
    file: str = "<stdin>"
    
    def __repr__(self) -> str:
        return f"Token({self.type.value}, {self.value!r}, line={self.line}, col={self.column})"
    
    def __str__(self) -> str:
        if self.value is not None:
            return f"{self.type.value}:{self.value}"
        return self.type.value


class Lexer:
    """
    Analyseur lexical pour Negative Language
    Transforme une chaîne de caractères en une liste de tokens
    """
    
    def __init__(self, source: str, filename: str = "<stdin>"):
        """
        Initialise le lexer avec le code source
        
        Args:
            source: Code source à analyser
            filename: Nom du fichier (pour les erreurs)
        """
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
        
        # Mots-clés réservés
        self.keywords: Dict[str, TokenType] = {
            'policy': TokenType.POLICY,
            'system': TokenType.SYSTEM,
            'deny': TokenType.DENY,
            'allow': TokenType.ALLOW,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'let': TokenType.LET,
            'import': TokenType.IMPORT,
            'as': TokenType.AS,
            'fn': TokenType.FN,
            'return': TokenType.RETURN,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'in': TokenType.IN,
        }
        
        # Caractères d'échappement
        self.escape_chars = {
            'n': '\n',
            't': '\t',
            'r': '\r',
            '\\': '\\',
            '"': '"',
            "'": "'",
        }
    
    def tokenize(self) -> List[Token]:
        """
        Convertit le code source en une liste de tokens
        
        Returns:
            Liste des tokens générés
            
        Raises:
            SyntaxError: En cas de caractère inconnu
        """
        while self.pos < len(self.source):
            char = self.current_char()
            
            # Sauts de ligne
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.col, self.filename))
                self.line += 1
                self.col = 1
                self.pos += 1
                continue
            
            # Espaces et tabulations (ignorés)
            if char in ' \t':
                if char == '\t':
                    self.col += 4
                else:
                    self.col += 1
                self.pos += 1
                continue
            
            # Commentaires
            if char == '#':
                self.skip_comment()
                continue
            
            # Chaînes de caractères
            if char in ['"', "'"]:
                self.tokens.append(self.read_string(char))
                continue
            
            # Nombres
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiants et mots-clés
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Opérateurs et délimiteurs
            self.tokens.append(self.read_operator())
            
        # Token de fin de fichier
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col, self.filename))
        return self.tokens
    
    def current_char(self) -> str:
        """Retourne le caractère courant ou \\0 si fin de fichier"""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return '\0'
    
    def peek(self, offset: int = 1) -> str:
        """Regarde le caractère à offset positions sans avancer"""
        if self.pos + offset < len(self.source):
            return self.source[self.pos + offset]
        return '\0'
    
    def advance(self) -> str:
        """Avance d'un caractère et retourne le caractère précédent"""
        char = self.current_char()
        self.pos += 1
        self.col += 1
        return char
    
    def skip_comment(self) -> None:
        """Ignore un commentaire jusqu'à la fin de la ligne"""
        while self.pos < len(self.source) and self.current_char() != '\n':
            self.pos += 1
            self.col += 1
    
    def read_string(self, quote_char: str) -> Token:
        """
        Lit une chaîne de caractères
        
        Args:
            quote_char: Caractère de guillemet (' ou ")
            
        Returns:
            Token de type STRING
        """
        start_line = self.line
        start_col = self.col
        self.pos += 1  # Ignorer le guillemet ouvrant
        self.col += 1
        
        string_value = ""
        
        while self.pos < len(self.source) and self.current_char() != quote_char:
            char = self.current_char()
            
            if char == '\\':
                self.pos += 1
                self.col += 1
                if self.pos < len(self.source):
                    escape_char = self.current_char()
                    if escape_char in self.escape_chars:
                        string_value += self.escape_chars[escape_char]
                    else:
                        string_value += escape_char
            else:
                string_value += char
            
            self.pos += 1
            self.col += 1
            
        # Vérifier la fermeture des guillemets
        if self.pos >= len(self.source):
            raise SyntaxError(
                f"String non terminée à la ligne {start_line}, colonne {start_col} dans {self.filename}"
            )
        
        self.pos += 1  # Ignorer le guillemet fermant
        self.col += 1
        
        return Token(TokenType.STRING, string_value, start_line, start_col, self.filename)
    
    def read_number(self) -> Token:
        """
        Lit un nombre (entier ou flottant)
        
        Returns:
            Token de type NUMBER
        """
        start_line = self.line
        start_col = self.col
        num_str = ""
        is_float = False
        
        while self.pos < len(self.source):
            char = self.current_char()
            
            if char.isdigit():
                num_str += char
                self.pos += 1
                self.col += 1
            elif char == '.' and not is_float and self.peek().isdigit():
                num_str += char
                is_float = True
                self.pos += 1
                self.col += 1
            else:
                break
        
        if is_float:
            return Token(TokenType.NUMBER, float(num_str), start_line, start_col, self.filename)
        return Token(TokenType.NUMBER, int(num_str), start_line, start_col, self.filename)
    
    def read_identifier(self) -> Token:
        """
        Lit un identifiant ou un mot-clé
        
        Returns:
            Token de type IDENTIFIER ou un mot-clé spécifique
        """
        start_line = self.line
        start_col = self.col
        ident = ""
        
        while self.pos < len(self.source):
            char = self.current_char()
            if char.isalnum() or char == '_':
                ident += char
                self.pos += 1
                self.col += 1
            else:
                break
        
        # Vérifier si c'est un mot-clé
        token_type = self.keywords.get(ident.lower(), TokenType.IDENTIFIER)
        
        # Valeur booléenne
        if token_type == TokenType.TRUE:
            return Token(TokenType.BOOLEAN, True, start_line, start_col, self.filename)
        if token_type == TokenType.FALSE:
            return Token(TokenType.BOOLEAN, False, start_line, start_col, self.filename)
        
        return Token(token_type, ident, start_line, start_col, self.filename)
    
    def read_operator(self) -> Token:
        """
        Lit un opérateur ou un délimiteur
        
        Returns:
            Token correspondant à l'opérateur
        """
        char = self.current_char()
        start_line = self.line
        start_col = self.col
        
        # Opérateurs à deux caractères
        two_char_ops = {
            '==': TokenType.EQUALS_EQUALS,
            '!=': TokenType.NOT_EQUALS,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '->': TokenType.ARROW,
        }
        
        if self.pos + 1 < len(self.source):
            two_char = char + self.source[self.pos + 1]
            if two_char in two_char_ops:
                self.pos += 2
                self.col += 2
                return Token(two_char_ops[two_char], two_char, start_line, start_col, self.filename)
        
        # Opérateurs à un caractère
        one_char_ops = {
            '!': TokenType.EXCLAMATION,
            '=': TokenType.EQUALS,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '@': TokenType.AT,
        }
        
        if char in one_char_ops:
            self.pos += 1
            self.col += 1
            return Token(one_char_ops[char], char, start_line, start_col, self.filename)
        
        # Caractère inconnu
        raise SyntaxError(
            f"Caractère inconnu '{char}' à la ligne {self.line}, colonne {self.col} dans {self.filename}"
        )
    
    def get_tokens_with_positions(self) -> List[Dict]:
        """
        Retourne les tokens avec leurs positions pour le debugging
        
        Returns:
            Liste de dictionnaires décrivant chaque token
        """
        return [
            {
                'type': t.type.value,
                'value': t.value,
                'line': t.line,
                'column': t.column,
                'file': t.file
            }
            for t in self.tokens
        ]


def tokenize_file(filename: str) -> List[Token]:
    """
    Tokenize un fichier source
    
    Args:
        filename: Chemin du fichier .neg
        
    Returns:
        Liste des tokens
    """
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    lexer = Lexer(source, filename)
    return lexer.tokenize()


def tokenize_source(source: str, filename: str = "<string>") -> List[Token]:
    """
    Tokenize une chaîne de caractères
    
    Args:
        source: Code source
        filename: Nom fictif du fichier
        
    Returns:
        Liste des tokens
    """
    lexer = Lexer(source, filename)
    return lexer.tokenize()