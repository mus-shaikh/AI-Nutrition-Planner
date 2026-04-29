"""
agents/user_input_agent.py — Agent 1: Validate & enrich user inputs.

Pure Python — no LLM needed. Fast, deterministic validation.
- Validates required fields
- Clamps numeric ranges
- Normalises disease list
- Auto-detects Indian season
"""

from __future__ import annotations
from graph.state import NutritionState
from utils.season import get_current_season


def user_input_agent(state: NutritionState) -> NutritionState:
    errors: list[str] = list(state.get("errors", []))

    # Validate required fields
    for field in ["age", "gender", "height_cm", "weight_kg", "goal", "diet_type"]:
        if not state.get(field):  # type: ignore[call-overload]
            errors.append(f"Missing required field: '{field}'")

    # Clamp workout minutes to 0-120
    workout_minutes = max(0, min(120, int(state.get("workout_minutes", 30))))

    # Normalise diseases — remove "None" / empty entries
    raw = state.get("diseases", [])
    if isinstance(raw, str):
        raw = [raw]
    diseases = [d.strip() for d in raw if d and d.strip() not in ("None", "")]

    activity = state.get("activity_level", "Light (1-2 days/week)")
    season   = get_current_season()

    return {
        **state,
        "workout_minutes": workout_minutes,
        "diseases":        diseases,
        "activity_level":  activity,
        "season":          season,
        "errors":          errors,
        "current_agent":   "user_input_agent",
    }
