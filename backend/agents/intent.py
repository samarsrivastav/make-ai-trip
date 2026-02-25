"""
Intent Parser agent: extracts structured intent from natural language.
"""

from state import (
    DecisionLogEntry,
    GraphState,
    ParsedIntent,
)


def parse_intent(state: GraphState) -> GraphState:
    """
    Parse user input into structured intent (budget, dates, origin, style, interests).
    Placeholder: returns mock parsed intent; replace with LLM call later.
    """
    # Placeholder parsing: will be replaced with LLM-based extraction
    parsed = ParsedIntent(
        budget_total=15000.0,
        currency="INR",
        origin="Delhi",
        destination="Rishikesh",
        num_days=4,
        travel_style="solo_backpacking",
        interests=["adventure sports", "spiritual experiences"],
        constraints=[],
    )

    new_entry = DecisionLogEntry(
        agent="intent_parser",
        step="parse",
        message=f"Parsed intent: budget={parsed.budget_total} {parsed.currency}, "
        f"origin={parsed.origin}, destination={parsed.destination}, days={parsed.num_days}",
        data=parsed.model_dump(),
    )

    return {
        "parsed_intent": parsed,
        "destination_shortlist": [parsed.destination] if parsed.destination else [],
        "decision_log": [new_entry],
    }
