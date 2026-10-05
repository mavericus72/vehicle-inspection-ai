from fastapi import FastAPI

from src.api.routes import router
from src.config import ensure_project_directories

ensure_project_directories()

app = FastAPI(
    title="Vehicle Inspection AI",
    description=(
        "AI-powered vehicle inspection service."
    ),
    version="1.0.0",
)


app.include_router(
    router
)


@app.get("/")
def root():
    return {
        "service": "vehicle-inspection-ai",
        "status": "running",
        "version": "1.0.0",
    }
