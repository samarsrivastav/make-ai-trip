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

    entries = [
        DecisionLogEntry(
            agent="research",
            step="fetch",
            message=f"Researching destination: {destination}",
            data=None,
        ),
    ]

    # Demo data when APIs are not configured
    researched = ResearchedData(
        flights=[
            FlightOption(
                origin="Delhi",
                destination="Dehradun",
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
                name="Zostel Rishikesh",
                address="Tapovan, Rishikesh",
                price_per_night=600.0,
                currency="INR",
                rating=4.5,
                booking_link="https://www.zostel.com/",
                map_link="https://maps.google.com/?q=Zostel+Rishikesh",
                is_demo=True,
            )
        ],
        activities=[
            ActivityOption(
                name="White Water Rafting",
                type="adventure",
                duration_minutes=180,
                price=1500.0,
                currency="INR",
                booking_link="https://example.com/rafting",
                map_link="https://maps.google.com/?q=Rishikesh+rafting",
                is_demo=True,
            ),
            ActivityOption(
                name="Evening Ganga Aarti",
                type="spiritual",
                duration_minutes=60,
                price=0.0,
                currency="INR",
                opening_hours="18:00",
                map_link="https://maps.google.com/?q=Triveni+Ghat",
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
        local_tips=["Book rafting in advance in peak season."],
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
