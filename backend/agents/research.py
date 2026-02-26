"""
Research Agent: fetches flights, hotels, weather, activities; fills shared state.
"""

from state import (
    ActivityOption,
    DecisionLogEntry,
    FlightOption,
    GraphState,
    HotelOption,
    ResearchedData,
    WeatherInfo,
)


def research(state: GraphState) -> GraphState:
    """
    Fetch real-world data (flights, hotels, weather, activities).
    Placeholder: returns demo data; will integrate Amadeus, Open-Meteo, etc.
    """
    intent = state.get("parsed_intent")
    destination = (intent.destination if intent else None) or "Rishikesh"
    origin = (intent.origin if intent else None) or "Delhi"

    entries = [
        DecisionLogEntry(
            agent="research",
            step="fetch",
            message=f"Researching destination: {destination} from {origin}",
            data=None,
        ),
    ]

    # Demo data when APIs are not configured; labels use parsed intent
    researched = ResearchedData(
        flights=[
            FlightOption(
                origin=origin,
                destination=destination,
                departure="2025-03-01 06:00",
                arrival="2025-03-01 07:15",
                carrier="IndiGo",
                price=2500.0,
                currency="INR",
                booking_link="https://www.goindigo.in/",
                is_demo=True,
            )
        ],
        hotels=[
            HotelOption(
                name=f"Stay at {destination}",
                address=destination,
                price_per_night=600.0,
                currency="INR",
                rating=4.5,
                booking_link="https://www.booking.com/",
                map_link=f"https://maps.google.com/?q={destination.replace(' ', '+')}",
                is_demo=True,
            )
        ],
        activities=[
            ActivityOption(
                name=f"Top activity in {destination}",
                type="adventure",
                duration_minutes=180,
                price=1500.0,
                currency="INR",
                booking_link="https://example.com/activities",
                map_link=f"https://maps.google.com/?q={destination.replace(' ', '+')}",
                is_demo=True,
            ),
            ActivityOption(
                name=f"Local experience in {destination}",
                type="spiritual",
                duration_minutes=60,
                price=0.0,
                currency="INR",
                opening_hours="18:00",
                map_link=f"https://maps.google.com/?q={destination.replace(' ', '+')}",
                is_demo=True,
            ),
        ],
        weather=[
            WeatherInfo(
                location=destination,
                date="2025-03-01",
                summary="Pleasant",
                temp_min=15.0,
                temp_max=28.0,
                conditions="Partly cloudy",
            )
        ],
        local_tips=[f"Book activities in {destination} in advance during peak season."],
    )

    entries.append(
        DecisionLogEntry(
            agent="research",
            step="complete",
            message=f"Found {len(researched.flights)} flight(s), {len(researched.hotels)} hotel(s), "
            f"{len(researched.activities)} activity(ies). Demo data used.",
            data=None,
        )
    )

    return {
        "researched_data": researched,
        "decision_log": entries,
    }
