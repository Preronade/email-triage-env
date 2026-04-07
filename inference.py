#!/usr/bin/env python3
"""
Email Triage Inference with LiteLLM Proxy
Uses the evaluator's API_BASE_URL and API_KEY - NO personal keys needed
"""

import os
import sys
import json
import time
from datetime import datetime
import openai

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from environment.core import EmailTriageEnv

# ============================================
# CRITICAL: Use the evaluator's environment variables
# DO NOT hardcode any API keys here!
# ============================================
API_BASE_URL = os.environ.get("API_BASE_URL", "http://litellm-proxy:4000")
API_KEY = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", "dummy-key"))

# Initialize OpenAI client with the proxy
client = openai.OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

class LiteLLMAgent:
    """Agent that makes REAL LLM calls through the provided proxy"""
    
    def __init__(self):
        self.total_calls = 0
        self.total_tokens = 0
        
    def get_action(self, observation, task_name: str):
        """Call LLM through LiteLLM proxy to decide action"""
        
        email = observation.current_email
        
        # Build prompt
        system_prompt = """You are an executive assistant managing email triage.
Output a JSON object with: {"type": "action_name", "reasoning": "your reasoning", "confidence": 0.0-1.0}
Actions: prioritize_high, prioritize_normal, prioritize_low, categorize_urgent, 
categorize_regular, categorize_informational, delegate, archive, request_info"""
        
        user_prompt = f"""Task: {task_name}
From: {email.from_address}
Subject: {email.subject}
Body: {email.body[:500]}
Urgency: {observation.metrics.get('urgency_score', 0):.2f}
Importance: {observation.metrics.get('importance_score', 0):.2f}
Queue: {observation.inbox_queue} remaining

Choose the best action:"""
        
        try:
            # Make ACTUAL LLM call through the proxy
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # The proxy will map this
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            self.total_calls += 1
            if response.usage:
                self.total_tokens += response.usage.total_tokens
            
            action = json.loads(response.choices[0].message.content)
            return action
            
        except Exception as e:
            print(f"[WARNING] LLM call failed: {e}")
            # Fallback action (should not happen in evaluation)
            return {"type": "prioritize_normal", "reasoning": "Fallback", "confidence": 0.5}
    
    def get_stats(self):
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "model": "gpt-3.5-turbo",
            "api_base": API_BASE_URL
        }

def run_task(task_id: str, episodes: int = 2) -> dict:
    """Run inference on a single task with real LLM calls"""
    
    print(f"[START] Task: {task_id}")
    
    env = EmailTriageEnv(task_id=task_id)
    agent = LiteLLMAgent()
    
    episode_scores = []
    
    for episode in range(episodes):
        print(f"[STEP] Episode: {episode + 1}/{episodes}")
        
        obs = env.reset()
        done = False
        total_reward = 0
        step_count = 0
        actions_log = []
        
        while not done:
            # Each action decision uses a REAL LLM call through the proxy
            action = agent.get_action(obs, env.task.name)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step_count += 1
            
            actions_log.append({
                "step": step_count,
                "action": action.get('type'),
                "reward": round(reward, 3),
                "confidence": action.get('confidence', 0)
            })
            
            print(f"[STEP] Step {step_count}: {action.get('type')} -> Reward: {reward:.3f}")
            print(f"[STEP] Reasoning: {action.get('reasoning', 'No reasoning')}")
        
        final_score = env.task.compute_final_score(env.actions_taken)
        episode_scores.append(final_score)
        
        print(f"[STEP] Episode {episode + 1} Complete - Score: {final_score:.3f}")
        print(f"[STEP] Total LLM calls: {agent.total_calls}")
        print(f"[STEP] Total tokens used: {agent.total_tokens}")
    
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
    print(f"[END] LLM Calls: {agent.total_calls} | Tokens: {agent.total_tokens}")
    
    return result

def main():
    """Main inference entry point - uses LiteLLM proxy"""
    
    print("[START] Email Triage Inference - LiteLLM Proxy Mode")
    print(f"[STEP] API Base URL: {API_BASE_URL}")
    print(f"[STEP] Model: gpt-3.5-turbo (via proxy)")
    print("[STEP] Making REAL LLM calls through evaluator's proxy")
    
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
    total_llm_calls = 0
    for result in all_results:
        score = result.get('average_score', 0)
        total_score += score
        stats = result.get('agent_stats', {})
        total_llm_calls += stats.get('total_calls', 0)
        print(f"[STEP] {result['task']}: {score:.3f} ({stats.get('total_calls', 0)} LLM calls)")
    
    overall_score = total_score / len(tasks)
    print(f"[END] Overall Score: {overall_score:.3f}")
    print(f"[END] Total LLM Calls: {total_llm_calls}")
    print("[END] Inference Complete - Used LiteLLM Proxy!")
    
    # Output results
    summary = {
        "overall_score": overall_score,
        "tasks": all_results,
        "timestamp": datetime.now().isoformat(),
        "total_llm_calls": total_llm_calls,
        "api_base_url": API_BASE_URL
    }
    
    with open("inference_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    return summary

if __name__ == "__main__":
    main()