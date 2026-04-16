import unittest
import json
from negative.lexer import Lexer
from negative.parser import Parser
from negative.interpreter import Interpreter

class TestNegative(unittest.TestCase):
    def test_lexer_basic(self):
        source = "policy test { deny all }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertGreater(len(tokens), 0)
        
    def test_parser_policy(self):
        source = "policy security { deny all allow admin }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(len(ast.policies), 1)
        self.assertEqual(ast.policies[0].name, "security")
        self.assertTrue(ast.policies[0].deny_all)
        
    def test_interpreter_basic(self):
        source = """
        policy test {
            deny all
            allow admin
            !guest
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        result = interpreter.interpret(ast)
        
        self.assertEqual(result["default"], "deny")
        self.assertIn("admin", result["allowed"])
        self.assertIn("guest", result["excluded"])
        
    def test_system_block(self):
        source = """
        system {
            !debug
            max_connections = 100
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        result = interpreter.interpret(ast)
        
        self.assertIn("debug", result["excluded"])
        self.assertEqual(result["system_settings"]["max_connections"], 100)
        
    def test_if_statement(self):
        source = """
        if connected
            deny access
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.context["connected"] = True
        result = interpreter.interpret(ast)
        
        self.assertIn("access", result["excluded"])

if __name__ == '__main__':
    unittest.main()