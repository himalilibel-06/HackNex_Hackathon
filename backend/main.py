"""
SAFE SIGHT - FastAPI Application Entrypoint (backend/main.py)

Mounts API routes, CORS middleware for React frontend, static file directories,
and health endpoints.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.schemas import HealthResponse
from backend.routes.videos import router as videos_router
from backend.routes.events import router as events_router
from backend.routes.incidents import router as incidents_router
from backend.routes.reports import router as reports_router

app = FastAPI(
    title="SafeSight AI API",
    description="Context-Aware Behaviour Understanding and Explainable Risk Scoring for Warehouse Safety",
    version="1.0.0"
)

# Configure CORS Middleware for React Frontend
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure required directories exist before mounting static files
os.makedirs("output/annotated", exist_ok=True)
os.makedirs("output/evidence", exist_ok=True)
os.makedirs("output/reports", exist_ok=True)
os.makedirs("videos/raw", exist_ok=True)

# Mount static file directories for video streaming and evidence preview
app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# Include Router Modules
app.include_router(videos_router)
app.include_router(events_router)
app.include_router(incidents_router)
app.include_router(reports_router)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint for frontend connection verification."""
    return HealthResponse(status="healthy")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
