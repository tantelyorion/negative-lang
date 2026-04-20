# Nouveau fichier: negative/typing.py
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class TypeKind(Enum):
    INT = "int"
    STRING = "string"
    BOOL = "bool"
    LIST = "list"
    ANY = "any"

@dataclass
class NegativeType:
    kind: TypeKind
    element_type: Optional['NegativeType'] = None
    
    def check(self, value: Any) -> bool:
        if self.kind == TypeKind.INT:
            return isinstance(value, int)
        elif self.kind == TypeKind.STRING:
            return isinstance(value, str)
        elif self.kind == TypeKind.BOOL:
            return isinstance(value, bool)
        return True