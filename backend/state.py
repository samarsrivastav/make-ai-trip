"""
Shared state schema for the LangGraph travel planning workflow.
All agents read and write this state; checkpoints persist it for human-in-the-loop.
"""

import operator
from typing import Annotated, Any, Optional, TypedDict

from pydantic import BaseModel, Field


class ParsedIntent(BaseModel):
    """Structured intent extracted from the user's natural language input."""

    budget_total: Optional[float] = None
    currency: str = "INR"
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    num_days: Optional[int] = None
    travel_style: Optional[str] = None  # solo_backpacking, family, luxury, weekend, etc.
    interests: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class FlightOption(BaseModel):
    """A single flight option with pricing and link."""

    origin: str
    destination: str
    departure: str
    arrival: str
    carrier: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    booking_link: Optional[str] = None
    is_demo: bool = False


class HotelOption(BaseModel):
    """A single hotel option with pricing and link."""

    name: str
    address: Optional[str] = None
    price_per_night: Optional[float] = None
    currency: str = "INR"
    rating: Optional[float] = None
    booking_link: Optional[str] = None
    map_link: Optional[str] = None
    contact: Optional[str] = None
    is_demo: bool = False


class ActivityOption(BaseModel):
    """An activity or place to visit."""

    name: str
    type: Optional[str] = None  # adventure, spiritual, food, etc.
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    currency: str = "INR"
    opening_hours: Optional[str] = None
    booking_link: Optional[str] = None
    map_link: Optional[str] = None
    is_demo: bool = False


class WeatherInfo(BaseModel):
    """Weather summary for the destination/dates."""

    location: str
    date: str
    summary: Optional[str] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    conditions: Optional[str] = None


class ResearchedData(BaseModel):
    """Aggregated data from the Research Agent."""

    flights: list[FlightOption] = Field(default_factory=list)
    hotels: list[HotelOption] = Field(default_factory=list)
    activities: list[ActivityOption] = Field(default_factory=list)
    weather: list[WeatherInfo] = Field(default_factory=list)
    local_tips: list[str] = Field(default_factory=list)
    raw_notes: Optional[str] = None


class BudgetAllocation(BaseModel):
    """Proposed budget split across categories."""

    transport: float = 0.0
    stay: float = 0.0
    food: float = 0.0
    activities: float = 0.0
    buffer: float = 0.0
    currency: str = "INR"
    reasoning: Optional[str] = None


class DayItem(BaseModel):
    """Single item in a day (activity or travel)."""

    time: Optional[str] = None
    title: str
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    map_link: Optional[str] = None
    booking_link: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"


class DayPlan(BaseModel):
    """One day of the itinerary."""

    day: int
    date: Optional[str] = None
    items: list[DayItem] = Field(default_factory=list)
    travel_notes: Optional[str] = None


class BookingOption(BaseModel):
    """Booking-ready option (flight/hotel/activity) with links."""

    type: str  # flight, hotel, activity
    label: str
    details: dict[str, Any] = Field(default_factory=dict)
    booking_link: Optional[str] = None
    map_link: Optional[str] = None
    contact: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"


class DecisionLogEntry(BaseModel):
    """Single entry in the transparency decision log."""

    agent: str
    step: str
    message: str
    data: Optional[dict[str, Any]] = None


class TravelPlanState(BaseModel):
    """Full workflow state (Pydantic); use for validation/serialization."""

    user_input: str = ""
    parsed_intent: Optional[ParsedIntent] = None
    destination_shortlist: list[str] = Field(default_factory=list)
    researched_data: Optional[ResearchedData] = None
    budget_allocation: Optional[BudgetAllocation] = None
    approved_budget: Optional[BudgetAllocation] = None
    day_by_day_itinerary: list[DayPlan] = Field(default_factory=list)
    booking_options: list[BookingOption] = Field(default_factory=list)
    decision_log: list[DecisionLogEntry] = Field(default_factory=list)
    current_checkpoint: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


class GraphState(TypedDict, total=False):
    """Graph state as TypedDict for LangGraph partial updates. Lists use add reducer."""

    user_input: str
    parsed_intent: Optional[ParsedIntent]
    destination_shortlist: list[str]
    researched_data: Optional[ResearchedData]
    budget_allocation: Optional[BudgetAllocation]
    approved_budget: Optional[BudgetAllocation]
    day_by_day_itinerary: list[DayPlan]
    booking_options: list[BookingOption]
    decision_log: Annotated[list[DecisionLogEntry], operator.add]
    current_checkpoint: Optional[str]
    error_message: Optional[str]
