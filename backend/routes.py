"""
FastAPI routes for plan creation, approval (resume), and state retrieval.
"""

from typing import Any, Optional

from fastapi import APIRouter, Request
from langgraph.types import Command
from pydantic import BaseModel, Field

plan_router = APIRouter()


class CreatePlanRequest(BaseModel):
    """Request body for creating a new travel plan."""

    user_input: str = Field(..., min_length=1, description="Natural language trip request")
    thread_id: Optional[str] = Field(None, description="Resume existing plan; omit for new plan")


class ApproveRequest(BaseModel):
    """Request body for resuming after an approval checkpoint."""

    resume: Any = Field(..., description="Approval payload (e.g. true or modified budget dict)")


def _state_to_dict(state: dict) -> dict:
    """Convert graph state to JSON-serializable dict (Pydantic models to dict)."""
    out = {}
    for k, v in state.items():
        if k.startswith("__"):
            continue
        if hasattr(v, "model_dump"):
            out[k] = v.model_dump()
        elif isinstance(v, list):
            out[k] = [
                x.model_dump() if hasattr(x, "model_dump") else x
                for x in v
            ]
        else:
            out[k] = v
    return out


@plan_router.post("", status_code=200)
async def create_plan(request: Request, body: CreatePlanRequest):
    """
    Start a new plan or continue from a checkpoint.
    If thread_id is provided and graph is at interrupt, use ApproveRequest to resume instead.
    """
    graph = request.app.state.graph
    thread_id = body.thread_id or f"plan-{id(body)}"
    config = {"configurable": {"thread_id": thread_id}}

    if body.thread_id:
        # Resuming: need to call with Command(resume=...) - use approve endpoint
        return {
            "message": "Use POST /api/plan/{thread_id}/approve with resume payload to continue",
            "thread_id": thread_id,
        }

    inputs = {"user_input": body.user_input}
    result = graph.invoke(inputs, config=config)

    interrupted = result.pop("__interrupt__", None)
    if interrupted:
        return {
            "thread_id": thread_id,
            "status": "awaiting_approval",
            "interrupt": [getattr(i, "value", i) for i in interrupted],
            "state": _state_to_dict(result),
        }

    return {
        "thread_id": thread_id,
        "status": "complete",
        "state": _state_to_dict(result),
    }


@plan_router.post("/{thread_id}/approve", status_code=200)
async def approve(request: Request, thread_id: str, body: ApproveRequest):
    """Resume graph after human approval at a checkpoint."""
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke(Command(resume=body.resume), config=config)

    interrupted = result.pop("__interrupt__", None)
    if interrupted:
        return {
            "thread_id": thread_id,
            "status": "awaiting_approval",
            "interrupt": [getattr(i, "value", i) for i in interrupted],
            "state": _state_to_dict(result),
        }

    return {
        "thread_id": thread_id,
        "status": "complete",
        "state": _state_to_dict(result),
    }


@plan_router.get("/{thread_id}", status_code=200)
async def get_plan_state(request: Request, thread_id: str):
    """Get current state for a plan (e.g. after loading from URL)."""
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": thread_id}}

    state = graph.get_state(config)
    if not state or not state.values:
        return {"thread_id": thread_id, "state": None, "status": "not_found"}

    values = state.values
    interrupted = getattr(state, "next", ()) or []
    return {
        "thread_id": thread_id,
        "state": _state_to_dict(dict(values)),
        "status": "awaiting_approval" if interrupted else "complete",
    }
