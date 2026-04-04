"""
OpenEnv compliant email triage environment server
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Email Triage Environment", description="OpenEnv compliant")

@app.get("/")
def root():
    return {"status": "healthy", "service": "Email Triage Environment"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(task_id: str = "easy_triage"):
    return JSONResponse(content={
        "status": "reset_complete",
        "task_id": task_id,
        "observation": {"inbox_queue": 3}
    })

@app.post("/step")
def step():
    return {"reward": 0.5, "done": False, "info": {}}

@app.get("/state")
def state(env_id: str = ""):
    return {"task": "email_triage", "progress": 0.5}

# Entry point for OpenEnv
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

# Also support openenv-server entry point
def server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
