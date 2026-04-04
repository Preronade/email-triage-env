from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def root():
    return {"status": "healthy"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(task_id: str = "easy_triage"):
    return {"status": "reset_complete"}

@app.post("/step")
def step():
    return {"reward": 0.5, "done": False}

@app.get("/state")
def state(env_id: str = ""):
    return {"task": "email_triage"}

# This main() function is required for OpenEnv
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
