from typing import List, Optional
from .lexer import Token, TokenType
from .ast import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def parse(self) -> Program:
        program = Program()
        
        while not self.is_at_end():
            token = self.peek()
            
            if token.type == TokenType.POLICY:
                program.policies.append(self.parse_policy())
            elif token.type == TokenType.SYSTEM:
                program.system_blocks.append(self.parse_system_block())
            elif token.type == TokenType.IDENTIFIER:
                # Check for exclamation statements
                if self.peek().value == '!':
                    program.rules.append(self.parse_exclamation())
                else:
                    program.rules.append(self.parse_if_statement())
            else:
                self.advance()
                
        return program
    
    def parse_policy(self) -> Policy:
        self.consume(TokenType.POLICY, "Expected 'policy' keyword")
        name_token = self.consume(TokenType.IDENTIFIER, "Expected policy name")
        policy = Policy(name_token.value)
        
        self.consume(TokenType.LBRACE, "Expected '{' after policy name")
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            token = self.peek()
            
            if token.type == TokenType.DENY:
                self.advance()
                if self.check(TokenType.IDENTIFIER) and self.peek().value == 'all':
                    self.advance()
                    policy.deny_all = True
                else:
                    # Deny specific item
                    target = self.consume(TokenType.IDENTIFIER, "Expected target after deny")
                    policy.exclusions.append(('deny', target.value))
            elif token.type == TokenType.ALLOW:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Expected target after allow")
                policy.allow_list.append(target.value)
            elif token.type == TokenType.EXCLAMATION:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Expected target after !")
                policy.exclusions.append(('exclude', target.value))
            else:
                self.advance()
                
        self.consume(TokenType.RBRACE, "Expected '}' after policy block")
        return policy
    
    def parse_system_block(self) -> SystemBlock:
        self.consume(TokenType.SYSTEM, "Expected 'system' keyword")
        system = SystemBlock()
        
        self.consume(TokenType.LBRACE, "Expected '{' after system")
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            token = self.peek()
            
            if token.type == TokenType.EXCLAMATION:
                self.advance()
                target = self.consume(TokenType.IDENTIFIER, "Expected target after !")
                system.exclusions.append(target.value)
            elif token.type == TokenType.IDENTIFIER:
                # Key-value pair
                key = token.value
                self.advance()
                self.consume(TokenType.EQUALS, "Expected '=' after key")
                value = self.parse_value()
                system.settings[key] = value
            else:
                self.advance()
                
        self.consume(TokenType.RBRACE, "Expected '}' after system block")
        return system
    
    def parse_exclamation(self) -> Rule:
        # Simple !exclusion statement
        self.consume(TokenType.EXCLAMATION, "Expected '!'")
        target = self.consume(TokenType.IDENTIFIER, "Expected target after !")
        return Rule("true", "deny", target.value)
    
    def parse_if_statement(self) -> Rule:
        self.consume(TokenType.IF, "Expected 'if' keyword")
        condition = self.parse_condition()
        
        # Action (deny or allow)
        action_token = self.peek()
        if action_token.type not in [TokenType.DENY, TokenType.ALLOW]:
            raise SyntaxError(f"Expected 'deny' or 'allow', got {action_token.type}")
        
        action = action_token.value
        self.advance()
        
        target = self.consume(TokenType.IDENTIFIER, "Expected target after action")
        
        return Rule(condition, action, target.value)
    
    def parse_condition(self) -> str:
        # Simple condition parsing for now
        condition_parts = []
        
        while not self.check(TokenType.DENY) and not self.check(TokenType.ALLOW) and not self.is_at_end():
            token = self.peek()
            if token.type == TokenType.IDENTIFIER:
                condition_parts.append(token.value)
                self.advance()
            elif token.type == TokenType.NOT_EQUALS:
                condition_parts.append("!=")
                self.advance()
            elif token.type == TokenType.EQUALS:
                condition_parts.append("==")
                self.advance()
            else:
                break
                
        return " ".join(condition_parts)
    
    def parse_value(self):
        token = self.peek()
        if token.type == TokenType.STRING:
            self.advance()
            return token.value
        elif token.type == TokenType.NUMBER:
            self.advance()
            return token.value
        elif token.type == TokenType.BOOLEAN:
            self.advance()
            return token.value
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return token.value
        else:
            raise SyntaxError(f"Unexpected token for value: {token.type}")
    
    def consume(self, expected_type: TokenType, error_message: str) -> Token:
        if self.check(expected_type):
            return self.advance()
        raise SyntaxError(f"{error_message} at line {self.peek().line}")
    
    def check(self, expected_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == expected_type
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.pos += 1
        return self.previous()
    
    def peek(self) -> Token:
        return self.tokens[self.pos]
    
    def previous(self) -> Token:
        return self.tokens[self.pos - 1]
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF