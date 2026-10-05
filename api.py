from fastapi import FastAPI

from src.api.routes import router
from src.config import ensure_project_directories


# ============================================================
# Project initialization
# ============================================================

ensure_project_directories()


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="Vehicle Inspection AI",
    description="AI-powered vehicle inspection service.",
    version="1.0.0",
)


# ============================================================
# API routes
# ============================================================

app.include_router(router)


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def root():
    """
    Root endpoint used for service health verification.
    """

    return {
        "service": "vehicle-inspection-ai",
        "status": "running",
        "version": "1.0.0",
    }
