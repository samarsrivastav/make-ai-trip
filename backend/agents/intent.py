"""
Intent Parser agent: extracts structured intent from natural language.
Uses simple regex and keyword matching; can be replaced with LLM later.
"""

import re
from typing import Optional

from state import (
    DecisionLogEntry,
    GraphState,
    ParsedIntent,
)


def _extract_destination(text: str) -> Optional[str]:
    """Extract destination from phrases like 'trip to X', 'in X', 'visit X', 'Goa'."""
    if not text or not text.strip():
        return None
    t = text.strip()
    # "trip to Goa", "to Rishikesh", "visit Manali", "in Kerala", "around Coorg", "go to Goa"
    for pattern in [
        r"\b(?:trip\s+to|visit|go\s+to|to)\s+([A-Za-z][A-Za-z\s]{1,30}?)(?:\s+trip|\s+under|\s+from|\s+next|,|$)",
        r"\b(?:in|around)\s+([A-Za-z][A-Za-z\s]{1,30}?)(?:\s+under|\s+from|,|$)",
        r"\b([A-Za-z][a-z]+)\s+trip\b",
    ]:
        m = re.search(pattern, t, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    # Known place names as single word (e.g. "Goa", "Manali", "Kerala")
    known = {"goa", "manali", "rishikesh", "kerala", "mumbai", "delhi", "jaipur", "udaipur", "coorg", "leh", "shimla", "darjeeling", "varanasi", "alleppey", "munnar"}
    words = re.split(r"[\s,]+", t)
    for w in words:
        wc = w.strip()
        if len(wc) > 2 and wc.lower() in known:
            return wc.title()
    # First capitalized word that looks like a place name
    for w in words:
        wc = w.strip()
        if len(wc) > 2 and wc[0].isupper() and wc.isalpha():
            return wc
    return None


def _extract_origin(text: str) -> Optional[str]:
    """Extract origin from 'from X'."""
    m = re.search(r"\bfrom\s+([A-Za-z][A-Za-z\s]{1,20}?)(?:\s+next|,|$)", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def _extract_budget(text: str) -> Optional[float]:
    """Extract budget number (INR). Handles ₹15,000, under 20000, 15k, etc."""
    # ₹15,000 or ₹15000 or Rs 20000
    m = re.search(r"₹?\s*Rs\.?\s*([0-9,]+)\s*(?:k|K|INR)?", text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r"(?:under|budget|within)\s*[₹\s]*([0-9,]+)\s*(?:k|K|INR|Rs)?", text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r"([0-9,]+)\s*(?:k|K)\b", text, re.IGNORECASE)
    if m:
        val = float(m.group(1).replace(",", ""))
        return val * 1000 if val < 1000 else val
    return None


def _extract_num_days(text: str) -> Optional[int]:
    """Extract number of days."""
    m = re.search(r"(\d+)\s*[-]?\s*day", text, re.IGNORECASE)
    if m:
        return min(max(1, int(m.group(1))), 30)
    m = re.search(r"(?:for\s+)?(\d+)\s+days?", text, re.IGNORECASE)
    if m:
        return min(max(1, int(m.group(1))), 30)
    if re.search(r"\bweekend\b", text, re.IGNORECASE):
        return 2
    if re.search(r"\bweek\b", text, re.IGNORECASE):
        return 7
    return None


def _extract_travel_style(text: str) -> Optional[str]:
    """Extract travel style."""
    t = text.lower()
    if "solo" in t or "backpacking" in t:
        return "solo_backpacking"
    if "family" in t:
        return "family"
    if "luxury" in t:
        return "luxury"
    if "weekend" in t:
        return "weekend"
    if "honeymoon" in t:
        return "honeymoon"
    return None


def _extract_interests(text: str) -> list[str]:
    """Extract interest keywords."""
    t = text.lower()
    interests = []
    if "adventure" in t or "rafting" in t or "trek" in t or "sports" in t:
        interests.append("adventure")
    if "spiritual" in t or "yoga" in t or "meditation" in t or "temple" in t or "aarti" in t:
        interests.append("spiritual")
    if "food" in t or "cuisine" in t or "eat" in t:
        interests.append("food")
    if "culture" in t or "heritage" in t or "historical" in t:
        interests.append("culture")
    if "beach" in t or "sea" in t:
        interests.append("beach")
    if "nature" in t or "wildlife" in t:
        interests.append("nature")
    return interests if interests else []


def parse_intent(state: GraphState) -> GraphState:
    """
    Parse user input into structured intent (budget, dates, origin, style, interests).
    Uses simple extraction; replace with LLM for better accuracy.
    """
    user_input = (state.get("user_input") or "").strip()
    if not user_input:
        user_input = ""

    destination = _extract_destination(user_input)
    origin = _extract_origin(user_input)
    budget_total = _extract_budget(user_input)
    num_days = _extract_num_days(user_input)
    travel_style = _extract_travel_style(user_input)
    interests = _extract_interests(user_input)

    parsed = ParsedIntent(
        budget_total=budget_total or 15000.0,
        currency="INR",
        origin=origin or "Delhi",
        destination=destination or "Rishikesh",
        num_days=num_days or 4,
        travel_style=travel_style or "solo_backpacking",
        interests=interests or ["adventure", "spiritual"],
        constraints=[],
    )

    new_entry = DecisionLogEntry(
        agent="intent_parser",
        step="parse",
        message=f"Parsed from input: budget={parsed.budget_total} {parsed.currency}, "
        f"origin={parsed.origin}, destination={parsed.destination}, days={parsed.num_days}",
        data=parsed.model_dump(),
    )

    return {
        "parsed_intent": parsed,
        "destination_shortlist": [parsed.destination] if parsed.destination else [],
        "decision_log": [new_entry],
    }
