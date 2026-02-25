"""
Booking Coordinator agent: produces booking-ready options with links and contact info.
"""

from state import (
    BookingOption,
    DecisionLogEntry,
    GraphState,
)


def coordinate_bookings(state: GraphState) -> GraphState:
    """
    Turn itinerary and research into booking-ready options with links/maps.
    """
    researched = state.get("researched_data")

    options: list[BookingOption] = []
    if researched:
        for f in researched.flights:
            options.append(
                BookingOption(
                    type="flight",
                    label=f"{f.origin} → {f.destination}",
                    details={"departure": f.departure, "carrier": f.carrier},
                    booking_link=f.booking_link,
                    price=f.price,
                    currency=f.currency or "INR",
                )
            )
        for h in researched.hotels:
            options.append(
                BookingOption(
                    type="hotel",
                    label=h.name,
                    details={"address": h.address, "rating": h.rating},
                    booking_link=h.booking_link,
                    map_link=h.map_link,
                    contact=h.contact,
                    price=h.price_per_night,
                    currency=h.currency or "INR",
                )
            )
        for a in researched.activities:
            options.append(
                BookingOption(
                    type="activity",
                    label=a.name,
                    details={"duration_minutes": a.duration_minutes, "type": a.type},
                    booking_link=a.booking_link,
                    map_link=a.map_link,
                    price=a.price,
                    currency=a.currency or "INR",
                )
            )

    new_entry = DecisionLogEntry(
        agent="coordinator",
        step="bookings",
        message=f"Prepared {len(options)} booking-ready options with links.",
        data=None,
    )

    return {
        "booking_options": options,
        "decision_log": [new_entry],
    }
