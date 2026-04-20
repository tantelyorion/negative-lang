# Negative Language

**Programming by Negation** - A language where everything is denied by default.

## Installation

```bash
pip install -e .


negative-lang/
│
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── README.md
├── install.sh
├── install.bat
├── pyproject.toml
├── requirements.txt
├── setup.py
│
├── negative/
│   ├── __init__.py
│   ├── __main__.py
│   ├── version.py
│   ├── cli.py
│   ├── lexer.py
│   ├── parser.py
│   ├── ast.py
│   ├── interpreter.py
│   ├── rules_engine.py
    ├── typing.py
│   │
│   ├── runtime/
│   │   ├── __init__.py
│   │   ├── environment.py
│   │   └── builtins.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── error_handler.py
│       └── logger.py
│
├── examples/
│   ├── security.neg
│   ├── system_config.neg
│   ├── ai_constraints.neg
│   └── comprehensive.neg
│
├── tests/
│   ├── __init__.py
│   └── test_negative.py
│
└── docs/
    └── index.html