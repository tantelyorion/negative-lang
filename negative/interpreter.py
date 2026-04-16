from typing import Dict, List, Any
from .ast import *
from .rules_engine import RulesEngine

class Interpreter:
    def __init__(self):
        self.rules_engine = RulesEngine()
        self.context = {}
        
    def interpret(self, program: Program) -> Dict[str, Any]:
        result = {
            "default": "deny",
            "allowed": [],
            "excluded": [],
            "system_settings": {},
            "rules": []
        }
        
        # Process policy blocks
        for policy in program.policies:
            if policy.deny_all:
                result["default"] = "deny"
            result["allowed"].extend(policy.allow_list)
            for excl_type, target in policy.exclusions:
                if excl_type == 'exclude':
                    result["excluded"].append(target)
                elif excl_type == 'deny':
                    result["excluded"].append(target)
                    
        # Process system blocks
        for system in program.system_blocks:
            result["excluded"].extend(system.exclusions)
            result["system_settings"].update(system.settings)
            
        # Process rules
        for rule in program.rules:
            if isinstance(rule, Rule):
                # Evaluate condition
                condition_result = self.evaluate_condition(rule.condition)
                if condition_result:
                    result["rules"].append({
                        "condition": rule.condition,
                        "action": rule.action,
                        "target": rule.target
                    })
                    if rule.action == "deny":
                        result["excluded"].append(rule.target)
                    else:  # allow
                        result["allowed"].append(rule.target)
                        
        # Apply priority rules: exclusions > allow > deny > default
        final_result = self.apply_priority(result)
        
        return final_result
    
    def evaluate_condition(self, condition: str) -> bool:
        # Simple condition evaluator
        # Can be extended for complex conditions
        if not condition or condition == "true":
            return True
        if condition == "false":
            return False
            
        # Check for variable in context
        if condition in self.context:
            return bool(self.context[condition])
            
        # Parse simple comparisons
        if "==" in condition:
            left, right = condition.split("==")
            return left.strip() == right.strip()
        elif "!=" in condition:
            left, right = condition.split("!=")
            return left.strip() != right.strip()
            
        return True
    
    def apply_priority(self, result: Dict) -> Dict:
        # Priority: excluded > allowed > default
        # Remove allowed items that are excluded
        result["allowed"] = [a for a in result["allowed"] if a not in result["excluded"]]
        
        # Apply rules
        for rule in result["rules"]:
            if rule["action"] == "deny" and rule["target"] in result["allowed"]:
                result["allowed"].remove(rule["target"])
            elif rule["action"] == "allow" and rule["target"] in result["excluded"]:
                result["excluded"].remove(rule["target"])
                
        return result