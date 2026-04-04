import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.core import EmailTriageEnv

class RuleBasedAgent:
    """Free baseline agent using simple rules - NO API KEYS NEEDED"""
    
    def get_action(self, observation):
        email = observation.current_email
        urgency = observation.metrics.get('urgency_score', 0)
        importance = observation.metrics.get('importance_score', 0)
        
        # Rule 1: High urgency + high importance
        if urgency > 0.6 and importance > 0.5:
            return {"type": "prioritize_high", "reasoning": "High urgency and importance"}
        
        # Rule 2: Urgent keywords
        urgent_keywords = ['urgent', 'asap', 'deadline', 'critical']
        for keyword in urgent_keywords:
            if keyword in email.subject.lower() or keyword in email.body.lower():
                return {"type": "categorize_urgent", "reasoning": f"Found keyword: {keyword}"}
        
        # Rule 3: Executive senders
        exec_senders = ['ceo', 'president', 'vp', 'director']
        if any(exec in email.from_address.lower() for exec in exec_senders):
            return {"type": "prioritize_high", "reasoning": "Message from executive"}
        
        # Rule 4: Newsletters = low priority
        low_priority = ['newsletter', 'digest', 'noreply']
        if any(ind in email.from_address.lower() or ind in email.subject.lower() for ind in low_priority):
            return {"type": "prioritize_low", "reasoning": "Newsletter or automated"}
        
        # Rule 5: Delegate for team emails
        if 'team' in email.body.lower() or 'department' in email.body.lower():
            return {"type": "delegate", "reasoning": "Team coordination needed"}
        
        # Default action
        return {"type": "prioritize_normal", "reasoning": "Standard priority"}

def run_baseline(task_id="easy_triage", episodes=2):
    env = EmailTriageEnv(task_id=task_id)
    agent = RuleBasedAgent()
    scores = []
    
    print(f"\n{'='*50}")
    print(f"Testing {task_id}")
    print(f"{'='*50}")
    
    for episode in range(episodes):
        obs = env.reset()
        done = False
        total_reward = 0
        step = 0
        
        while not done:
            action = agent.get_action(obs)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            step += 1
            print(f"  Step {step}: {action['type']} (reward: {reward:.2f})")
        
        print(f"Episode {episode+1} Total: {total_reward:.2f}")
        scores.append(total_reward)
    
    avg = sum(scores) / len(scores)
    print(f"Average: {avg:.2f}")
    return avg

if __name__ == "__main__":
    print("\n🚀 EMAIL TRIAGE BASELINE (FREE - No API Keys)\n")
    
    results = {}
    for task in ["easy_triage", "medium_triage", "hard_triage"]:
        score = run_baseline(task)
        results[task] = score
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    for task, score in results.items():
        print(f"{task:20s}: {score:.2f}")
