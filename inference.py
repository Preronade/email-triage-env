#!/usr/bin/env python3
"""
Email Triage Inference - COMPLETELY FREE (No API calls)
Uses intelligent rules instead of paid LLM APIs
"""

import os
import sys
import json
import random
from datetime import datetime

# Load environment variables (optional, not required for free version)
API_BASE_URL = os.getenv("API_BASE_URL", "mock://free-local")
MODEL_NAME = os.getenv("MODEL_NAME", "rule-based-agent")
HF_TOKEN = os.getenv("HF_TOKEN", "free-token-not-needed")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from environment.core import EmailTriageEnv

class FreeRuleBasedAgent:
    """100% FREE agent - No API calls, No payments, No external services"""
    
    def __init__(self):
        self.total_calls = 0
        self.decision_log = []
    
    def get_action(self, observation, task_name: str):
        """Intelligent rule-based decision making - COMPLETELY FREE"""
        
        email = observation.current_email
        urgency = observation.metrics.get('urgency_score', 0)
        importance = observation.metrics.get('importance_score', 0)
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()
        from_lower = email.from_address.lower()
        
        self.total_calls += 1
        
        # Sophisticated rule engine (no API needed!)
        
        # Rule 1: CEO or executive emails = HIGH priority
        exec_keywords = ['ceo', 'president', 'vp', 'director', 'founder', 'owner']
        if any(word in from_lower for word in exec_keywords):
            action = "prioritize_high"
            reasoning = "Executive sender requires immediate attention"
            confidence = 0.95
        
        # Rule 2: Urgent keywords detection
        elif any(word in subject_lower or word in body_lower 
                for word in ['urgent', 'asap', 'deadline', 'critical', 'emergency']):
            action = "categorize_urgent"
            reasoning = "Time-sensitive content detected"
            confidence = 0.9
        
        # Rule 3: High urgency + high importance
        elif urgency > 0.6 and importance > 0.5:
            action = "prioritize_high"
            reasoning = "High urgency and importance metrics"
            confidence = 0.85
        
        # Rule 4: Team coordination = delegate
        elif any(word in body_lower for word in ['team', 'department', 'committee', 'group']):
            action = "delegate"
            reasoning = "Requires team coordination"
            confidence = 0.8
        
        # Rule 5: Ambiguous requests = ask for info
        elif any(word in body_lower for word in ['maybe', 'perhaps', 'consider', 'thoughts?', 'opinion']):
            action = "request_info"
            reasoning = "Ambiguous request needs clarification"
            confidence = 0.75
        
        # Rule 6: Newsletters/automated = low priority
        elif any(word in from_lower or word in subject_lower 
                for word in ['newsletter', 'digest', 'noreply', 'automated', 'weekly']):
            action = "prioritize_low"
            reasoning = "Automated or newsletter content"
            confidence = 0.9
        
        # Rule 7: Normal priority default
        else:
            action = "prioritize_normal"
            reasoning = "Standard priority based on routine content"
            confidence = 0.7
        
        # Record decision
        decision = {
            "type": action,
            "reasoning": reasoning,
            "confidence": confidence,
            "urgency_score": urgency,
            "importance_score": importance
        }
        self.decision_log.append(decision)
        
        return decision
    
    def get_stats(self):
        return {
            "total_calls": self.total_calls,
            "model": "rule-based-free",
            "api_calls": 0,  # ZERO API calls!
            "cost": "$0.00"  # COMPLETELY FREE!
        }

def run_task(task_id: str, episodes: int = 2) -> dict:
    """Run inference on a single task with FREE agent"""
    
    print(f"[START] Task: {task_id}")
    
    env = EmailTriageEnv(task_id=task_id)
    agent = FreeRuleBasedAgent()
    
    episode_scores = []
    
    for episode in range(episodes):
        print(f"[STEP] Episode: {episode + 1}/{episodes}")
        
        obs = env.reset()
        done = False
        total_reward = 0
        step_count = 0
        
        while not done:
            action = agent.get_action(obs, env.task.name)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step_count += 1
            
            print(f"[STEP] Step {step_count}: {action['type']} -> Reward: {reward:.3f}")
            print(f"[STEP] Reasoning: {action['reasoning']}")
        
        final_score = env.task.compute_final_score(env.actions_taken)
        episode_scores.append(final_score)
        
        print(f"[STEP] Episode {episode + 1} Complete - Final Score: {final_score:.3f}")
    
    avg_score = sum(episode_scores) / len(episode_scores)
    
    result = {
        "task": task_id,
        "task_name": env.task.name,
        "difficulty": env.task.difficulty,
        "episodes": episodes,
        "scores": episode_scores,
        "average_score": round(avg_score, 3),
        "agent_stats": agent.get_stats()
    }
    
    print(f"[END] Task: {task_id} | Average Score: {avg_score:.3f}")
    
    return result

def main():
    """Main inference entry point - COMPLETELY FREE"""
    
    print("[START] Email Triage Inference - FREE Version")
    print("[STEP] Agent: Rule-based (No API calls, No payments)")
    print("[STEP] Model: FREE-RULE-BASED-AGENT")
    print("[STEP] API Base: MOCK-FREE-LOCAL")
    print("[STEP] Cost per run: $0.00")
    
    tasks = ["easy_triage", "medium_triage", "hard_triage"]
    all_results = []
    
    for task in tasks:
        try:
            result = run_task(task, episodes=2)
            all_results.append(result)
        except Exception as e:
            print(f"[ERROR] Task {task} failed: {e}")
            all_results.append({
                "task": task,
                "error": str(e),
                "average_score": 0.0
            })
    
    # Final summary
    print("\n[START] Final Summary")
    total_score = 0
    for result in all_results:
        score = result.get('average_score', 0)
        total_score += score
        print(f"[STEP] {result['task']}: {score:.3f}")
    
    overall_score = total_score / len(tasks)
    print(f"[END] Overall Score: {overall_score:.3f}")
    print(f"[END] Total Cost: $0.00 (FREE!)")
    
    # Output results
    summary = {
        "overall_score": overall_score,
        "tasks": all_results,
        "timestamp": datetime.now().isoformat(),
        "cost_usd": 0.00,
        "api_calls": 0
    }
    
    with open("inference_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("[END] Inference Complete - 100% FREE!")
    return summary

if __name__ == "__main__":
    main()
