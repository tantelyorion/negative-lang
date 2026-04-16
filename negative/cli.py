#!/usr/bin/env python3

import sys
import json
import argparse
from pathlib import Path
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter

class NegativeCLI:
    def __init__(self):
        self.interpreter = Interpreter()
        
    def run(self, filename: str) -> dict:
        """Execute a Negative file"""
        try:
            source = self.read_file(filename)
            result = self.execute(source)
            
            # Output result
            print(json.dumps(result, indent=2))
            return result
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    def check(self, filename: str) -> bool:
        """Check syntax of a Negative file without executing"""
        try:
            source = self.read_file(filename)
            tokens = self.tokenize(source)
            ast = self.parse(tokens)
            print(f"✓ Syntax check passed for {filename}")
            print(f"  Tokens: {len(tokens)}")
            print(f"  AST nodes: {self.count_nodes(ast)}")
            return True
        except Exception as e:
            print(f"✗ Syntax error in {filename}: {e}", file=sys.stderr)
            return False
            
    def explain(self, filename: str):
        """Explain the rules generated from a Negative file"""
        try:
            source = self.read_file(filename)
            result = self.execute(source)
            
            print(f"\n📋 Negative Policy Analysis for {filename}")
            print("=" * 50)
            print(f"Default policy: {result['default'].upper()}")
            print(f"\n✅ Allowed resources: {len(result['allowed'])}")
            for resource in result['allowed']:
                print(f"  • {resource}")
            print(f"\n❌ Excluded resources: {len(result['excluded'])}")
            for resource in result['excluded']:
                print(f"  • {resource}")
            if result['system_settings']:
                print(f"\n⚙️ System settings:")
                for key, value in result['system_settings'].items():
                    print(f"  • {key} = {value}")
            if result['rules']:
                print(f"\n📜 Active rules:")
                for rule in result['rules']:
                    print(f"  • if {rule['condition']} then {rule['action']} {rule['target']}")
                    
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    def compile(self, filename: str, output: str = None):
        """Compile Negative to JSON rules"""
        try:
            source = self.read_file(filename)
            result = self.execute(source)
            
            if output is None:
                output = filename.replace('.neg', '.njson')
                
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
                
            print(f"✓ Compiled {filename} → {output}")
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
            
    def execute(self, source: str) -> dict:
        """Execute Negative source code"""
        tokens = self.tokenize(source)
        ast = self.parse(tokens)
        result = self.interpreter.interpret(ast)
        return result
        
    def read_file(self, filename: str) -> str:
        path = Path(filename)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def tokenize(self, source: str):
        lexer = Lexer(source)
        return lexer.tokenize()
        
    def parse(self, tokens):
        parser = Parser(tokens)
        return parser.parse()
        
    def count_nodes(self, ast) -> int:
        count = 1
        for child in ast.children:
            count += self.count_nodes(child)
        return count

def main():
    parser = argparse.ArgumentParser(
        description="Negative Language - Programming by negation",
        prog="negative"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a Negative file')
    run_parser.add_argument('file', help='.neg file to execute')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check syntax of a Negative file')
    check_parser.add_argument('file', help='.neg file to check')
    
    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain rules from a Negative file')
    explain_parser.add_argument('file', help='.neg file to explain')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile Negative to JSON')
    compile_parser.add_argument('file', help='.neg file to compile')
    compile_parser.add_argument('-o', '--output', help='Output file (default: .njson)')
    
    args = parser.parse_args()
    
    cli = NegativeCLI()
    
    if args.command == 'run':
        cli.run(args.file)
    elif args.command == 'check':
        success = cli.check(args.file)
        sys.exit(0 if success else 1)
    elif args.command == 'explain':
        cli.explain(args.file)
    elif args.command == 'compile':
        cli.compile(args.file, args.output)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()