"""
Budget Optimizer agent: allocates budget across transport, stay, food, activities.
"""

from state import (
    BudgetAllocation,
    DecisionLogEntry,
    GraphState,
)


def optimize_budget(state: GraphState) -> GraphState:
    """
    Propose budget allocation; will trigger interrupt for human approval.
    """
    intent = state.get("parsed_intent")
    currency = (intent.currency if intent else None) or "INR"

    allocation = BudgetAllocation(
        transport=3000.0,
        stay=4000.0,
        food=3500.0,
        activities=3500.0,
        buffer=1000.0,
        currency=currency,
        reasoning="Balanced for solo backpacking: transport (flights + local), "
        "budget stay (hostel), food, and adventure activities.",
    )

    new_entry = DecisionLogEntry(
        agent="budget_optimizer",
        step="allocate",
        message=f"Proposed allocation: transport {allocation.transport}, stay {allocation.stay}, "
        f"food {allocation.food}, activities {allocation.activities} ({currency})",
        data=allocation.model_dump(),
    )

    return {
        "budget_allocation": allocation,
        "decision_log": [new_entry],
    }
