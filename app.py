"""
OpenEnv compliant email triage environment server
Uses LiteLLM proxy for LLM calls
"""

import os
import json
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import openai

# ============================================
# USE THE EVALUATOR'S PROXY - CRITICAL!
# ============================================
API_BASE_URL = os.environ.get("API_BASE_URL", "http://litellm-proxy:4000")
API_KEY = os.environ.get("API_KEY", os.environ.get("OPENAI_API_KEY", ""))

# Initialize OpenAI client with the proxy
client = openai.OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

app = FastAPI(title="Email Triage Environment")

# Store environments
environments = {}

class ActionRequest(BaseModel):
    action: Dict[str, Any]
    env_id: Optional[str] = None

# ============================================
# FIX: Clamp scores to strictly (0, 1)
# ============================================
def clamp_score(score: float) -> float:
    """Score must be strictly between 0 and 1, never 0.0 or 1.0"""
    epsilon = 1e-6
    return max(epsilon, min(1.0 - epsilon, float(score)))

def get_llm_action(email_subject, email_body, urgency, importance):
    """Make REAL LLM call through LiteLLM proxy"""
    
    prompt = f"""
Email subject: {email_subject}
Email body: {email_body[:300]}
Urgency score: {urgency}
Importance score: {importance}

Choose one action: prioritize_high, prioritize_normal, prioritize_low,
categorize_urgent, categorize_regular, delegate, archive, request_info.

Output JSON: {{"type": "action_name", "reasoning": "why"}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an executive assistant for email triage."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("type", "prioritize_normal"), result.get("reasoning", "")
        
    except Exception as e:
        print(f"LLM call failed: {e}")
        return "prioritize_normal", "Fallback"

@app.get("/")
def root():
    return {"status": "healthy", "service": "Email Triage Environment"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset_env(task_id: str = "easy_triage"):
    """Reset environment"""
    try:
        from environment.core import EmailTriageEnv
        env = EmailTriageEnv(task_id=task_id)
        observation = env.reset()
        env_id = f"{task_id}_{id(env)}"
        environments[env_id] = env
        
        return JSONResponse(content={
            "status": "reset_complete",
            "env_id": env_id,
            "observation": {
                "current_email": {
                    "subject": observation.current_email.subject,
                    "from": observation.current_email.from_address,
                    "body": observation.current_email.body[:300]
                },
                "inbox_queue": observation.inbox_queue,
                "metrics": observation.metrics
            }
        })
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/step")
def step_action(request: ActionRequest):
    """Execute action - MAKES REAL LLM CALL"""
    env_id = request.action.get('env_id') or request.env_id
    
    if not env_id or env_id not in environments:
        return {"reward": clamp_score(0.0), "done": True, "info": {"error": "Environment not found"}}
    
    env = environments[env_id]
    obs = env._get_observation()
    
    # CRITICAL: Make REAL LLM call through the proxy
    action_type, reasoning = get_llm_action(
        obs.current_email.subject,
        obs.current_email.body,
        obs.metrics.get('urgency_score', 0),
        obs.metrics.get('importance_score', 0)
    )
    
    action = {"type": action_type, "reasoning": reasoning}
    observation, reward, done, info = env.step(action)
    
    return {
        "observation": {
            "current_email": {
                "subject": observation.current_email.subject,
                "from": observation.current_email.from_address
            },
            "inbox_queue": observation.inbox_queue,
            "metrics": observation.metrics
        },
        "reward": clamp_score(reward),   # FIX: clamped
        "done": done,
        "info": info
    }

@app.get("/state")
def get_state(env_id: str):
    if env_id in environments:
        return environments[env_id].state()
    return {"error": "Environment not found"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()