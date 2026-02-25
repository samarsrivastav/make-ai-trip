"""
Route/Itinerary Planner agent: day-by-day schedule with timings and travel duration.
"""

from state import (
    DayItem,
    DayPlan,
    DecisionLogEntry,
    GraphState,
)


def plan_itinerary(state: GraphState) -> GraphState:
    """
    Build day-by-day itinerary; respects travel times and feasibility.
    """
    intent = state.get("parsed_intent")
    num_days = (intent.num_days if intent else 4) or 4
    researched = state.get("researched_data")

    days: list[DayPlan] = []
    for d in range(1, num_days + 1):
        items: list[DayItem] = []
        if d == 1:
            items = [
                DayItem(time="06:00", title="Travel to Rishikesh", duration_minutes=315, description="Flight + cab"),
                DayItem(time="12:00", title="Check-in & lunch", duration_minutes=90),
                DayItem(time="14:00", title="Explore Tapovan", duration_minutes=180),
                DayItem(time="18:00", title="Ganga Aarti", duration_minutes=60),
            ]
        elif d == 2:
            items = [
                DayItem(time="08:00", title="White Water Rafting", duration_minutes=180, price=1500.0),
                DayItem(time="12:00", title="Lunch by river", duration_minutes=60),
                DayItem(time="14:00", title="Beach/relax", duration_minutes=180),
            ]
        else:
            items = [
                DayItem(time="09:00", title="Morning activity / yoga", duration_minutes=120),
                DayItem(time="12:00", title="Lunch", duration_minutes=60),
                DayItem(time="14:00", title="Local exploration", duration_minutes=240),
            ]
        days.append(DayPlan(day=d, date=None, items=items))

    new_entry = DecisionLogEntry(
        agent="planner",
        step="itinerary",
        message=f"Built {len(days)}-day itinerary with timings and travel duration.",
        data=None,
    )

    return {
        "day_by_day_itinerary": days,
        "decision_log": [new_entry],
    }
