from fastapi import FastAPI

from backend.routes import router
from backend.database import engine
from backend.models import Base


# Create database tables when the service starts.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Incident Response Agent"
)

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