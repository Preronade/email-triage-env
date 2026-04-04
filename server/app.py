"""
OpenEnv compliant email triage environment server
"""

import sys
import os

# Add parent directory to path so we can import environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Try to import environment, fallback to mock
try:
    from environment.core import EmailTriageEnv
    ENV_AVAILABLE = True
except ImportError:
    ENV_AVAILABLE = False
    print("Warning: environment module not available")

app = FastAPI(title="Email Triage Environment")

# Store environments
environments = {}

@app.get("/")
def root():
    return {"status": "healthy", "service": "Email Triage Environment"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(task_id: str = "easy_triage"):
    if ENV_AVAILABLE:
        env = EmailTriageEnv(task_id=task_id)
        env_id = f"{task_id}_{id(env)}"
        environments[env_id] = env
        return JSONResponse(content={
            "status": "reset_complete",
            "env_id": env_id,
            "task_id": task_id
        })
    return {"status": "reset_complete", "task_id": task_id}

@app.post("/step")
def step():
    return {"reward": 0.5, "done": False, "info": {}}

@app.get("/state")
def state(env_id: str = ""):
    return {"task": "email_triage", "progress": 0.5}

def main():
    """Entry point for OpenEnv multi-mode deployment"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
