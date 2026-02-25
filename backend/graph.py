"""
LangGraph workflow: intent -> research -> approvals -> budget -> planner -> coordinator.
Uses interrupt() at three checkpoints for human-in-the-loop.
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agents.budget import optimize_budget
from agents.coordinator import coordinate_bookings
from agents.intent import parse_intent
from agents.planner import plan_itinerary
from agents.research import research
from state import GraphState


def _serialize_for_interrupt(obj):
    """Convert state to JSON-serializable dict for interrupt payload."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, list):
        return [_serialize_for_interrupt(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize_for_interrupt(v) for k, v in obj.items()}
    return obj


def approve_destinations(state: GraphState) -> GraphState:
    """Pause for human approval of destination shortlist. Resume with any value to continue."""
    shortlist = state.get("destination_shortlist") or []
    researched = state.get("researched_data")
    payload = {
        "checkpoint": "destination_shortlist",
        "message": "Approve destination shortlist?",
        "destination_shortlist": shortlist,
        "researched_summary": {
            "flights_count": len(researched.flights) if researched else 0,
            "hotels_count": len(researched.hotels) if researched else 0,
            "activities_count": len(researched.activities) if researched else 0,
        } if researched else None,
    }
    interrupt(payload)
    return {"current_checkpoint": "destinations_approved"}


def approve_budget(state: GraphState) -> GraphState:
    """Pause for human approval of budget allocation. Resume with approved_budget dict or True."""
    allocation = state.get("budget_allocation")
    payload = {
        "checkpoint": "budget_allocation",
        "message": "Approve budget allocation?",
        "budget_allocation": _serialize_for_interrupt(allocation),
    }
    result = interrupt(payload)
    from state import BudgetAllocation
    if isinstance(result, dict) and result.get("transport") is not None:
        return {"approved_budget": BudgetAllocation(**result), "current_checkpoint": "budget_approved"}
    return {"approved_budget": allocation, "current_checkpoint": "budget_approved"}


def approve_itinerary(state: GraphState) -> GraphState:
    """Pause for human approval of final itinerary. Resume with any value to continue."""
    itinerary = state.get("day_by_day_itinerary") or []
    payload = {
        "checkpoint": "final_itinerary",
        "message": "Approve final itinerary?",
        "day_count": len(itinerary),
        "day_by_day_itinerary": _serialize_for_interrupt(itinerary),
    }
    interrupt(payload)
    return {"current_checkpoint": "itinerary_approved"}


def get_graph_with_checkpointer():
    """Build and compile the travel planning graph with in-memory checkpointer."""
    builder = StateGraph(GraphState)

    builder.add_node("intent", parse_intent)
    builder.add_node("research", research)
    builder.add_node("approve_destinations", approve_destinations)
    builder.add_node("budget", optimize_budget)
    builder.add_node("approve_budget", approve_budget)
    builder.add_node("planner", plan_itinerary)
    builder.add_node("approve_itinerary", approve_itinerary)
    builder.add_node("coordinator", coordinate_bookings)

    builder.add_edge(START, "intent")
    builder.add_edge("intent", "research")
    builder.add_edge("research", "approve_destinations")
    builder.add_edge("approve_destinations", "budget")
    builder.add_edge("budget", "approve_budget")
    builder.add_edge("approve_budget", "planner")
    builder.add_edge("planner", "approve_itinerary")
    builder.add_edge("approve_itinerary", "coordinator")
    builder.add_edge("coordinator", END)

    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    return graph, checkpointer
