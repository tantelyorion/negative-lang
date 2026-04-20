#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PARSER FOR NEGATIVE LANGUAGE
Convertit une liste de tokens en AST (Abstract Syntax Tree)
Version: 1.1.0
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field

from .lexer import Token, TokenType
from .ast import (
    Program, Policy, SystemBlock, Rule,
    Expr, BinaryExpr, UnaryExpr, LiteralExpr, VariableExpr,
    LetStatement, ImportStatement, FunctionStatement,
    NodeType
)


class Parser:
    """
    Analyseur syntaxique pour Negative Language
    Transforme une liste de tokens en AST
    """
    
    def __init__(self, tokens: List[Token]):
        """
        Initialise le parser avec une liste de tokens
        
        Args:
            tokens: Liste des tokens générés par le lexer
        """
        self.tokens = tokens
        self.pos = 0
        self.current_policy: Optional[Policy] = None
        
    def parse(self) -> Program:
        """
        Parse l'ensemble du programme
        
        Returns:
            Noeud racine de l'AST (Program)
        """
        program = Program()
        
        while not self.is_at_end():
            token = self.peek()
            
            # Bloc policy
            if token.type == TokenType.POLICY:
                program.policies.append(self.parse_policy())
            
            # Bloc system
            elif token.type == TokenType.SYSTEM:
                program.system_blocks.append(self.parse_system_block())
            
            # Instruction let
            elif token.type == TokenType.LET:
                program.let_statements.append(self.parse_let_statement())
            
            # Instruction import
            elif token.type == TokenType.IMPORT:
                program.imports.append(self.parse_import_statement())
            
            # Instruction function
            elif token.type == TokenType.FN:
                program.functions.append(self.parse_function_statement())
            
            # Exclusion simple (!)
            elif token.type == TokenType.EXCLAMATION:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Attendu un identifiant après '!'")
                program.exclusions.append(target.value)
            
            # Instruction allow directe
            elif token.type == TokenType.ALLOW:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Attendu un identifiant après 'allow'")
                program.direct_allows.append(target.value)
            
            # Instruction deny directe
            elif token.type == TokenType.DENY:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Attendu un identifiant après 'deny'")
                program.direct_denies.append(target.value)
            
            # Règle conditionnelle
            elif token.type == TokenType.IF:
                program.rules.append(self.parse_if_statement())
            
            # Directive @
            elif token.type == TokenType.AT:
                program.directives.append(self.parse_directive())
            
            else:
                # Ignorer les NEWLINE et autres tokens inattendus
                if token.type == TokenType.NEWLINE:
                    self.advance()
                else:
                    raise SyntaxError(
                        f"Token inattendu: {token.type.value} à la ligne {token.line}, colonne {token.column}"
                    )
        
        return program
    
    def parse_policy(self) -> Policy:
        """
        Parse un bloc policy
        
        Returns:
            Noeud Policy
        """
        self.consume(TokenType.POLICY, "Attendu 'policy'")
        name_token = self.consume(TokenType.IDENTIFIER, "Attendu nom de politique")
        
        policy = Policy(name_token.value)
        
        self.consume(TokenType.LBRACE, "Attendu '{' après le nom de la politique")
        
        # Par défaut, deny_all = True (implicite)
        policy.deny_all = True
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            token = self.peek()
            
            if token.type == TokenType.DENY:
                self.advance()
                
                if self.check(TokenType.IDENTIFIER) and self.peek().value == 'all':
                    self.advance()
                    policy.deny_all = True
                else:
                    target = self.consume(TokenType.IDENTIFIER, "Attendu cible après 'deny'")
                    policy.exclusions.append(target.value)
            
            elif token.type == TokenType.ALLOW:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Attendu cible après 'allow'")
                policy.allow_list.append(target.value)
            
            elif token.type == TokenType.EXCLAMATION:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Attendu cible après '!'")
                policy.exclusions.append(target.value)
            
            elif token.type == TokenType.NEWLINE:
                self.advance()
            
            else:
                raise SyntaxError(
                    f"Token inattendu dans la politique: {token.type.value} à la ligne {token.line}"
                )
        
        self.consume(TokenType.RBRACE, "Attendu '}' après le bloc politique")
        
        return policy
    
    def parse_system_block(self) -> SystemBlock:
        """
        Parse un bloc system
        
        Returns:
            Noeud SystemBlock
        """
        self.consume(TokenType.SYSTEM, "Attendu 'system'")
        
        system = SystemBlock()
        
        self.consume(TokenType.LBRACE, "Attendu '{' après 'system'")
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            token = self.peek()
            
            if token.type == TokenType.EXCLAMATION:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Attendu cible après '!'")
                system.exclusions.append(target.value)
            
            elif token.type == TokenType.IDENTIFIER:
                key = token.value
                self.advance()
                
                self.consume(TokenType.EQUALS, "Attendu '=' après la clé")
                
                value = self.parse_value()
                system.settings[key] = value
            
            elif token.type == TokenType.NEWLINE:
                self.advance()
            
            else:
                raise SyntaxError(
                    f"Token inattendu dans system: {token.type.value} à la ligne {token.line}"
                )
        
        self.consume(TokenType.RBRACE, "Attendu '}' après le bloc system")
        
        return system
    
    def parse_let_statement(self) -> LetStatement:
        """
        Parse une instruction let (déclaration de variable)
        
        Returns:
            Noeud LetStatement
        """
        self.consume(TokenType.LET, "Attendu 'let'")
        
        name_token = self.consume(TokenType.IDENTIFIER, "Attendu nom de variable")
        var_name = name_token.value
        
        var_type = None
        if self.check(TokenType.COLON):
            self.advance()
            type_token = self.consume(TokenType.IDENTIFIER, "Attendu type après ':'")
            var_type = type_token.value
        
        self.consume(TokenType.EQUALS, "Attendu '=' après le nom de variable")
        
        value = self.parse_value()
        
        return LetStatement(var_name, var_type, value)
    
    def parse_import_statement(self) -> ImportStatement:
        """
        Parse une instruction import
        
        Returns:
            Noeud ImportStatement
        """
        self.consume(TokenType.IMPORT, "Attendu 'import'")
        
        path_token = self.consume(TokenType.STRING, "Attendu chemin du module")
        module_path = path_token.value
        
        alias = None
        if self.check(TokenType.AS):
            self.advance()
            alias_token = self.consume(TokenType.IDENTIFIER, "Attendu alias après 'as'")
            alias = alias_token.value
        
        return ImportStatement(module_path, alias)
    
    def parse_function_statement(self) -> FunctionStatement:
        """
        Parse une déclaration de fonction
        
        Returns:
            Noeud FunctionStatement
        """
        self.consume(TokenType.FN, "Attendu 'fn'")
        
        name_token = self.consume(TokenType.IDENTIFIER, "Attendu nom de fonction")
        func_name = name_token.value
        
        self.consume(TokenType.LPAREN, "Attendu '(' après le nom de la fonction")
        
        params = []
        while not self.check(TokenType.RPAREN) and not self.is_at_end():
            param_token = self.consume(TokenType.IDENTIFIER, "Attendu nom de paramètre")
            param_name = param_token.value
            
            param_type = None
            if self.check(TokenType.COLON):
                self.advance()
                type_token = self.consume(TokenType.IDENTIFIER, "Attendu type du paramètre")
                param_type = type_token.value
            
            params.append((param_name, param_type))
            
            if self.check(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RPAREN, "Attendu ')' après les paramètres")
        
        return_type = None
        if self.check(TokenType.ARROW):
            self.advance()
            type_token = self.consume(TokenType.IDENTIFIER, "Attendu type de retour")
            return_type = type_token.value
        
        # Corps de la fonction (à implémenter dans une version future)
        body = []
        
        return FunctionStatement(func_name, params, return_type, body)
    
    def parse_if_statement(self) -> Rule:
        """
        Parse une règle conditionnelle if
        
        Returns:
            Noeud Rule
        """
        self.consume(TokenType.IF, "Attendu 'if'")
        
        condition = self.parse_condition()
        
        # Nouvelle ligne obligatoire avant l'action
        if not self.check(TokenType.NEWLINE):
            raise SyntaxError(
                f"Attendu nouvelle ligne après la condition à la ligne {self.peek().line}"
            )
        self.advance()  # Consomme NEWLINE
        
        # Action (deny ou allow)
        action_token = self.peek()
        if action_token.type not in [TokenType.DENY, TokenType.ALLOW]:
            raise SyntaxError(
                f"Attendu 'deny' ou 'allow', obtenu {action_token.type.value} à la ligne {action_token.line}"
            )
        
        action = action_token.value
        self.advance()
        
        target = self.consume(TokenType.IDENTIFIER, "Attendu cible après l'action")
        
        return Rule(condition, action, target.value)
    
    def parse_condition(self) -> str:
        """
        Parse une condition simple
        
        Returns:
            Chaîne représentant la condition
        """
        condition_parts = []
        
        while not self.is_at_end():
            token = self.peek()
            
            # Fin de la condition : NEWLINE ou action
            if token.type == TokenType.NEWLINE:
                break
            if token.type in [TokenType.DENY, TokenType.ALLOW]:
                break
            
            # Opérateurs
            if token.type == TokenType.EXCLAMATION:
                condition_parts.append('!')
                self.advance()
            elif token.type == TokenType.EQUALS_EQUALS:
                condition_parts.append('==')
                self.advance()
            elif token.type == TokenType.NOT_EQUALS:
                condition_parts.append('!=')
                self.advance()
            elif token.type == TokenType.LESS_THAN:
                condition_parts.append('<')
                self.advance()
            elif token.type == TokenType.GREATER_THAN:
                condition_parts.append('>')
                self.advance()
            elif token.type == TokenType.LESS_EQUAL:
                condition_parts.append('<=')
                self.advance()
            elif token.type == TokenType.GREATER_EQUAL:
                condition_parts.append('>=')
                self.advance()
            elif token.type == TokenType.IN:
                condition_parts.append('in')
                self.advance()
            
            # Identifiants et valeurs
            elif token.type == TokenType.IDENTIFIER:
                condition_parts.append(token.value)
                self.advance()
            elif token.type == TokenType.STRING:
                condition_parts.append(f'"{token.value}"')
                self.advance()
            elif token.type == TokenType.NUMBER:
                condition_parts.append(str(token.value))
                self.advance()
            elif token.type == TokenType.BOOLEAN:
                condition_parts.append('true' if token.value else 'false')
                self.advance()
            
            # Espace implicite
            else:
                break
        
        return ' '.join(condition_parts).strip()
    
    def parse_value(self) -> Any:
        """
        Parse une valeur littérale
        
        Returns:
            Valeur parsée (str, int, float, bool, ou None)
        """
        token = self.peek()
        
        if token.type == TokenType.STRING:
            self.advance()
            return token.value
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return token.value
        
        if token.type == TokenType.BOOLEAN:
            self.advance()
            return token.value
        
        if token.type == TokenType.IDENTIFIER:
            # Vérifier si c'est true/false
            if token.value.lower() == 'true':
                self.advance()
                return True
            if token.value.lower() == 'false':
                self.advance()
                return False
            self.advance()
            return token.value
        
        raise SyntaxError(
            f"Valeur inattendue: {token.type.value} à la ligne {token.line}"
        )
    
    def parse_directive(self) -> Dict[str, Any]:
        """
        Parse une directive @
        
        Returns:
            Dictionnaire représentant la directive
        """
        self.consume(TokenType.AT, "Attendu '@'")
        
        name_token = self.consume(TokenType.IDENTIFIER, "Attendu nom de directive")
        name = name_token.value
        
        directive = {'name': name, 'args': {}}
        
        if self.check(TokenType.LPAREN):
            self.advance()
            
            while not self.check(TokenType.RPAREN) and not self.is_at_end():
                key_token = self.consume(TokenType.IDENTIFIER, "Attendu nom d'argument")
                key = key_token.value
                
                self.consume(TokenType.EQUALS, "Attendu '='")
                
                value = self.parse_value()
                directive['args'][key] = value
                
                if self.check(TokenType.COMMA):
                    self.advance()
            
            self.consume(TokenType.RPAREN, "Attendu ')'")
        
        return directive
    
    def consume(self, expected_type: TokenType, error_message: str) -> Token:
        """
        Consomme un token du type attendu
        
        Args:
            expected_type: Type de token attendu
            error_message: Message d'erreur si le token n'est pas trouvé
            
        Returns:
            Le token consommé
        """
        if self.check(expected_type):
            return self.advance()
        
        token = self.peek()
        raise SyntaxError(
            f"{error_message} à la ligne {token.line}, colonne {token.column}\n"
            f"  Trouvé: {token.type.value} ({token.value})"
        )
    
    def check(self, expected_type: TokenType) -> bool:
        """
        Vérifie si le token courant est du type attendu
        
        Args:
            expected_type: Type de token à vérifier
            
        Returns:
            True si le token correspond, False sinon
        """
        if self.is_at_end():
            return False
        return self.peek().type == expected_type
    
    def advance(self) -> Token:
        """
        Avance d'un token et retourne le token précédent
        
        Returns:
            Le token consommé
        """
        if not self.is_at_end():
            self.pos += 1
        return self.previous()
    
    def peek(self) -> Token:
        """
        Regarde le token courant sans avancer
        
        Returns:
            Le token courant
        """
        return self.tokens[self.pos]
    
    def previous(self) -> Token:
        """
        Retourne le token précédent
        
        Returns:
            Le token précédent
        """
        return self.tokens[self.pos - 1]
    
    def is_at_end(self) -> bool:
        """
        Vérifie si on est à la fin du flux de tokens
        
        Returns:
            True si le token courant est EOF, False sinon
        """
        return self.peek().type == TokenType.EOF
    
    def synchronize(self) -> None:
        """
        Synchronise le parser après une erreur
        Saute les tokens jusqu'au prochain statement valide
        """
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.NEWLINE:
                return
            
            token = self.peek()
            if token.type in [
                TokenType.POLICY,
                TokenType.SYSTEM,
                TokenType.LET,
                TokenType.IMPORT,
                TokenType.FN,
                TokenType.IF,
            ]:
                return
            
            self.advance()


def parse_file(filename: str) -> Program:
    """
    Parse un fichier source
    
    Args:
        filename: Chemin du fichier .neg
        
    Returns:
        Noeud racine de l'AST
    """
    from .lexer import tokenize_file
    tokens = tokenize_file(filename)
    parser = Parser(tokens)
    return parser.parse()


def parse_source(source: str, filename: str = "<string>") -> Program:
    """
    Parse une chaîne de caractères
    
    Args:
        source: Code source
        filename: Nom fictif du fichier
        
    Returns:
        Noeud racine de l'AST
    """
    from .lexer import tokenize_source
    tokens = tokenize_source(source, filename)
    parser = Parser(tokens)
    return parser.parse()