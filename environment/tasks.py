from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

def clamp_score(score: float) -> float:
    """Score must be strictly between 0 and 1, never 0.0 or 1.0"""
    epsilon = 1e-6
    return max(epsilon, min(1.0 - epsilon, float(score)))

@dataclass
class Task:
    name: str
    difficulty: str
    emails: List[Dict]
    optimal_actions: List[str]
    weights: Dict[str, float]
    
    def grade_action(self, action: str, context: Dict) -> float:
        raise NotImplementedError
    
    def compute_final_score(self, actions_taken: List[Dict]) -> float:
        raise NotImplementedError

class EasyTriageTask(Task):
    def __init__(self):
        emails = [
            {
                "id": "e1",
                "from": "ceo@company.com",
                "subject": "URGENT: Board meeting in 1 hour",
                "body": "Need your analysis for the board presentation. Critical.",
                "priority_hints": ["urgent", "ceo", "board"],
                "correct_priority": "high",
                "correct_category": "urgent"
            },
            {
                "id": "e2",
                "from": "team@company.com",
                "subject": "Weekly sync notes",
                "body": "Here are the notes from our weekly team meeting.",
                "priority_hints": ["regular"],
                "correct_priority": "normal",
                "correct_category": "regular"
            },
            {
                "id": "e3",
                "from": "newsletter@tech.com",
                "subject": "Tech digest",
                "body": "Weekly technology news summary.",
                "priority_hints": ["low", "newsletter"],
                "correct_priority": "low",
                "correct_category": "informational"
            }
        ]
        
        super().__init__(
            name="Basic Priority Classification",
            difficulty="easy",
            emails=emails,
            optimal_actions=["prioritize_high", "categorize_urgent",
                           "prioritize_normal", "categorize_regular",
                           "prioritize_low", "categorize_informational"],
            weights={"accuracy": 0.6, "efficiency": 0.2, "consistency": 0.2}
        )
    
    def grade_action(self, action: str, context: Dict) -> float:
        email = context.get("current_email", {})
        correct_priority = email.get("correct_priority")
        correct_category = email.get("correct_category")
        
        score = 0.0
        
        if action == f"prioritize_{correct_priority}":
            score += 0.5
        elif "prioritize" in action:
            score += 0.1
            
        if action == f"categorize_{correct_category}":
            score += 0.5
        elif "categorize" in action:
            score += 0.1
            
        return score
    
    def compute_final_score(self, actions_taken: List[Dict]) -> float:
        if not actions_taken:
            return clamp_score(0.0)  # FIX: was 0.0
            
        accuracy_score = sum(1 for a in actions_taken 
                           if self.grade_action(a['type'], a) > 0.5) / len(actions_taken)
        
        efficiency_score = min(1.0 - 1e-6, len(actions_taken) / (len(self.emails) * 2))  # FIX: can't hit 1.0
        consistency_score = 0.9
        
        final = (self.weights["accuracy"] * accuracy_score +
                self.weights["efficiency"] * efficiency_score +
                self.weights["consistency"] * consistency_score)
        
        return clamp_score(final)  # FIX: clamp final


class MediumTriageTask(Task):
    def __init__(self):
        emails = [
            {
                "id": "m1",
                "from": "client@bigcorp.com",
                "subject": "Contract signing deadline today",
                "body": "Need final approval by 5pm for $1M deal",
                "priority_hints": ["client", "deadline", "financial"],
                "time_sensitivity": 0.9,
                "stakeholder_importance": 0.95,
            },
            {
                "id": "m2",
                "from": "internal@company.com",
                "subject": "IT maintenance this weekend",
                "body": "Systems will be down Saturday 2-4am",
                "priority_hints": ["maintenance", "scheduled"],
                "time_sensitivity": 0.3,
                "stakeholder_importance": 0.4,
            },
            {
                "id": "m3",
                "from": "angry_customer@email.com",
                "subject": "URGENT COMPLAINT - Service down",
                "body": "Been down for 3 hours, losing business!",
                "priority_hints": ["complaint", "urgent", "escalation"],
                "time_sensitivity": 0.95,
                "stakeholder_importance": 0.85,
            }
        ]
        
        super().__init__(
            name="Multi-constraint Optimization",
            difficulty="medium",
            emails=emails,
            optimal_actions=["prioritize_high", "delegate", "categorize_urgent",
                           "request_info", "prioritize_normal"],
            weights={"accuracy": 0.4, "time_management": 0.3, "delegation": 0.2, "communication": 0.1}
        )
    
    def grade_action(self, action: str, context: Dict) -> float:
        email = context.get("current_email", {})
        time_sensitivity = email.get("time_sensitivity", 0.5)
        
        score = 0.0
        
        if "prioritize_high" in action and time_sensitivity > 0.7:
            score += 0.4
        elif "prioritize_normal" in action and 0.3 <= time_sensitivity <= 0.7:
            score += 0.3
            
        if "delegate" in action and email.get("stakeholder_importance", 0) > 0.7:
            score += 0.3
            
        if "categorize_urgent" in action and time_sensitivity > 0.8:
            score += 0.3
            
        return clamp_score(score)  # FIX: was min(1.0, score) which can hit 1.0
    
    def compute_final_score(self, actions_taken: List[Dict]) -> float:
        if len(actions_taken) < len(self.emails):
            return clamp_score(0.3)  # FIX: was 0.3 (safe but clamp for consistency)
        
        accuracy = sum(self.grade_action(a['type'], a) for a in actions_taken) / len(actions_taken)
        time_spent = len(actions_taken) * 0.1
        time_score = max(1e-6, 1.0 - time_spent)  # FIX: can't hit 0.0
        delegation_actions = [a for a in actions_taken if a['type'] == 'delegate']
        delegation_score = min(1.0 - 1e-6, len(delegation_actions) / 2)  # FIX: can't hit 1.0
        
        final = (self.weights["accuracy"] * accuracy +
                self.weights["time_management"] * time_score +
                self.weights["delegation"] * delegation_score)
        
        return clamp_score(final)  # FIX: clamp final


class HardTriageTask(Task):
    def __init__(self):
        emails = [
            {
                "id": "h1",
                "from": "vp_engineering@company.com",
                "subject": "RE: Critical infrastructure update",
                "body": "We need to decide about the migration. Multiple stakeholders involved.",
                "priority_hints": ["vp", "infrastructure", "ambiguous"],
                "stakeholders": ["engineering", "product", "security", "compliance"],
                "ambiguity_level": 0.8,
            },
            {
                "id": "h2",
                "from": "legal@company.com",
                "subject": "Compliance review needed",
                "body": "New regulation requires changes to data handling",
                "priority_hints": ["legal", "compliance", "regulatory"],
                "deadline_days": 5,
                "ambiguity_level": 0.6,
            },
            {
                "id": "h3",
                "from": "strategic_partner@partner.com",
                "subject": "Partnership renewal discussion",
                "body": "Need to discuss terms for next year",
                "priority_hints": ["partner", "revenue", "strategic"],
                "ambiguity_level": 0.7,
            }
        ]
        
        super().__init__(
            name="Complex Stakeholder Management",
            difficulty="hard",
            emails=emails,
            optimal_actions=["request_info", "delegate", "prioritize_high", 
                           "categorize_urgent", "prioritize_normal"],
            weights={"stakeholder_satisfaction": 0.35, "accuracy": 0.25, 
                    "communication": 0.2, "efficiency": 0.2}
        )
    
    def grade_action(self, action: str, context: Dict) -> float:
        email = context.get("current_email", {})
        ambiguity = email.get("ambiguity_level", 0.5)
        
        score = 0.0
        
        if ambiguity > 0.7 and action == "request_info":
            score += 0.5
            
        if len(email.get("stakeholders", [])) > 2 and "delegate" in action:
            score += 0.3
            
        if "prioritize_high" in action and email.get("deadline_days", 10) < 2:
            score += 0.2
            
        return clamp_score(score)  # FIX: clamp
    
    def compute_final_score(self, actions_taken: List[Dict]) -> float:
        if len(actions_taken) < len(self.emails):
            return clamp_score(0.2)  # FIX: was 0.2 (safe but clamp for consistency)
        
        stakeholder_score = 0.7
        accuracy_score = sum(self.grade_action(a['type'], a) for a in actions_taken) / len(actions_taken)
        communication_score = min(1.0 - 1e-6,  # FIX: can't hit 1.0
                                  len([a for a in actions_taken if a.get('reasoning')]) / len(actions_taken))
        
        final = (self.weights["stakeholder_satisfaction"] * stakeholder_score +
                self.weights["accuracy"] * accuracy_score +
                self.weights["communication"] * communication_score)
        
        return clamp_score(final)  # FIX: clamp final