from fastapi import FastAPI
from backend.routes import router


app = FastAPI(title="AI Incident Response Agent")

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "AI Incident Response Agent is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }