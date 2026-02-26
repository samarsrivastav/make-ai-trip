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
    total = (intent.budget_total if intent else None) or 15000.0
    # Scale allocation to user's budget (keep same ratios)
    scale = total / 15000.0
    allocation = BudgetAllocation(
        transport=round(3000.0 * scale, 0),
        stay=round(4000.0 * scale, 0),
        food=round(3500.0 * scale, 0),
        activities=round(3500.0 * scale, 0),
        buffer=round(1000.0 * scale, 0),
        currency=currency,
        reasoning=f"Balanced allocation for {total:,.0f} {currency}: transport, stay, food, activities.",
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
