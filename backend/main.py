"""
FastAPI application for the AI Travel Planning & Booking Agent.
Exposes LangGraph workflow and approval/replan endpoints.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graph import get_graph_with_checkpointer
from routes import plan_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load graph and checkpointer on startup."""
    app.state.graph, app.state.checkpointer = get_graph_with_checkpointer()
    yield
    # cleanup if needed


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Travel Planning & Booking Agent",
        description="Multi-agent system for trip planning with human-in-the-loop",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(plan_router, prefix="/api/plan", tags=["plan"])
    return app


app = create_app()


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check for deployment."""
    return {"status": "ok", "service": "travel-agent"}
