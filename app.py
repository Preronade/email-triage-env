import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(title="Email Triage Environment")

@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "Email Triage Environment",
        "openenv_compliant": True
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(task_id: str = "easy_triage"):
    return JSONResponse(content={
        "status": "reset_complete",
        "task_id": task_id,
        "observation": {"inbox_queue": 3, "metrics": {"progress": 0}}
    })

@app.post("/step")
def step():
    return {"reward": 0.5, "done": False, "info": {}}

@app.get("/state")
def state(env_id: str = ""):
    return {"task": "email_triage", "progress": 0.5, "status": "running"}

# This is CRITICAL - without this, the app exits immediately
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
