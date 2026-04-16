from dataclasses import dataclass
from typing import List, Optional, Any
from enum import Enum

class NodeType(Enum):
    PROGRAM = "PROGRAM"
    POLICY = "POLICY"
    SYSTEM_BLOCK = "SYSTEM_BLOCK"
    DENY_STATEMENT = "DENY_STATEMENT"
    ALLOW_STATEMENT = "ALLOW_STATEMENT"
    EXCLAMATION_STATEMENT = "EXCLAMATION_STATEMENT"
    IF_STATEMENT = "IF_STATEMENT"
    CONDITION = "CONDITION"
    BLOCK = "BLOCK"

@dataclass
class ASTNode:
    type: NodeType
    value: Any = None
    children: List['ASTNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class Program(ASTNode):
    def __init__(self):
        super().__init__(NodeType.PROGRAM)
        self.policies = []
        self.system_blocks = []
        self.rules = []

@dataclass
class Policy(ASTNode):
    def __init__(self, name: str):
        super().__init__(NodeType.POLICY)
        self.name = name
        self.deny_all = False
        self.allow_list = []
        self.exclusions = []

@dataclass
class SystemBlock(ASTNode):
    def __init__(self):
        super().__init__(NodeType.SYSTEM_BLOCK)
        self.exclusions = []
        self.settings = {}

@dataclass
class Rule(ASTNode):
    def __init__(self, condition: str, action: str, target: str):
        super().__init__(NodeType.IF_STATEMENT)
        self.condition = condition
        self.action = action
        self.target = target