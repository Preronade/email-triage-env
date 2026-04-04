#!/usr/bin/env python3
from environment.core import EmailTriageEnv

print("🧪 Testing Email Triage Environment")
print("="*50)

# Test 1: Create environment
print("\n✅ Test 1: Creating environment")
env = EmailTriageEnv("easy_triage")
print("   Environment created successfully")

# Test 2: Reset
print("\n✅ Test 2: Reset function")
obs = env.reset()
print(f"   First email: {obs.current_email.subject}")
print(f"   Inbox queue: {obs.inbox_queue}")

# Test 3: Step function
print("\n✅ Test 3: Step function")
action = {"type": "prioritize_high", "reasoning": "Test"}
obs, reward, done, info = env.step(action)
print(f"   Reward: {reward:.2f}")
print(f"   Done: {done}")

# Test 4: State function
print("\n✅ Test 4: State function")
state = env.state()
print(f"   Task: {state['task']}")
print(f"   Difficulty: {state['difficulty']}")

# Test 5: All tasks
print("\n✅ Test 5: Loading all tasks")
for task in ["easy_triage", "medium_triage", "hard_triage"]:
    env = EmailTriageEnv(task)
    obs = env.reset()
    print(f"   {task}: {len(env.task.emails)} emails loaded")

print("\n" + "="*50)
print("🎉 ALL TESTS PASSED! Environment is ready!")
print("="*50)
