"""
Built-in functions for Negative Language
"""

from typing import Dict, Any, Callable

class BuiltinFunctions:
    """Collection of built-in functions available in Negative"""
    
    @staticmethod
    def print(*args) -> None:
        """Print values to stdout"""
        print(*args)
        
    @staticmethod
    def type(obj: Any) -> str:
        """Return type of object"""
        return type(obj).__name__
        
    @staticmethod
    def len(obj: Any) -> int:
        """Return length of object"""
        return len(obj)
        
    @staticmethod
    def isinstance(obj: Any, class_type: type) -> bool:
        """Check if object is instance of class"""
        return isinstance(obj, class_type)
        
    @staticmethod
    def allowed(resource: str, rules: Dict) -> bool:
        """Check if resource is allowed by rules"""
        if resource in rules.get("excluded", []):
            return False
        if resource in rules.get("allowed", []):
            return True
        return rules.get("default", "deny") == "allow"
        
    @staticmethod
    def denied(resource: str, rules: Dict) -> bool:
        """Check if resource is denied by rules"""
        return not BuiltinFunctions.allowed(resource, rules)
        
    @classmethod
    def get_all(cls) -> Dict[str, Callable]:
        """Get all built-in functions"""
        return {
            "print": cls.print,
            "type": cls.type,
            "len": cls.len,
            "isinstance": cls.isinstance,
            "allowed": cls.allowed,
            "denied": cls.denied,
        }