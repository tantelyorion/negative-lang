from typing import Dict, List, Any, Set
from dataclasses import dataclass, field

@dataclass
class RuleSet:
    default_action: str = "deny"
    allowed: Set[str] = field(default_factory=set)
    denied: Set[str] = field(default_factory=set)
    exceptions: Dict[str, str] = field(default_factory=dict)
    
class RulesEngine:
    def __init__(self):
        self.rules = RuleSet()
        
    def add_rule(self, action: str, target: str, priority: int = 0):
        if action == "allow":
            if target not in self.rules.denied:
                self.rules.allowed.add(target)
        elif action == "deny":
            self.rules.denied.add(target)
            if target in self.rules.allowed:
                self.rules.allowed.remove(target)
                
    def add_exclusion(self, target: str):
        self.rules.denied.add(target)
        if target in self.rules.allowed:
            self.rules.allowed.remove(target)
            
    def check_permission(self, resource: str) -> bool:
        if resource in self.rules.denied:
            return False
        if resource in self.rules.allowed:
            return True
        return self.rules.default_action == "allow"
    
    def get_allowed_resources(self) -> Set[str]:
        return self.rules.allowed.copy()
    
    def get_denied_resources(self) -> Set[str]:
        return self.rules.denied.copy()
    
    def export_json(self) -> Dict:
        return {
            "default": self.rules.default_action,
            "allowed": list(self.rules.allowed),
            "denied": list(self.rules.denied),
            "exceptions": self.rules.exceptions
        }