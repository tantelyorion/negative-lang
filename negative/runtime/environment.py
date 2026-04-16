"""
Execution environment for Negative Language
"""

from typing import Dict, Any, Optional

class Environment:
    """Runtime environment for variable storage and context"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.constants: Dict[str, Any] = {}
        
    def define(self, name: str, value: Any, constant: bool = False):
        """Define a variable in current scope"""
        if constant:
            self.constants[name] = value
        else:
            self.variables[name] = value
            
    def get(self, name: str) -> Any:
        """Get variable value, searching parent scopes"""
        if name in self.variables:
            return self.variables[name]
        if name in self.constants:
            return self.constants[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable: {name}")
        
    def set(self, name: str, value: Any):
        """Set variable value in appropriate scope"""
        if name in self.constants:
            raise TypeError(f"Cannot reassign constant: {name}")
        if name in self.variables:
            self.variables[name] = value
        elif self.parent and (name in self.parent.variables or name in self.parent.constants):
            self.parent.set(name, value)
        else:
            self.define(name, value)
            
    def has(self, name: str) -> bool:
        """Check if variable exists in any scope"""
        return (name in self.variables or 
                name in self.constants or 
                (self.parent and self.parent.has(name)))