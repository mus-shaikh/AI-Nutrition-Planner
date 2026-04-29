"""
agents/weekly_planner_agent.py — Agent 7: 7-Day Meal Planner.

Generates a full week of meals with:
- Rotation of sabzi, dal, and fruits across days
- No consecutive repetition
- Consistent calorie targets
- Seasonal and Veg/Non-Veg awareness
"""

from __future__ import annotations
import json, re
from graph.state import NutritionState
from utils.llm import get_llm
from utils.season import get_seasonal_vegetables, get_seasonal_fruits

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def weekly_planner_agent(state: NutritionState) -> NutritionState:
    target  = state["target_calories"]
    goal    = state["goal"]
    diet    = state["diet_type"]
    season  = state.get("season", "winter")
    diseases= state.get("diseases", [])
    sample  = state.get("daily_diet_plan", {})

    vegs   = get_seasonal_vegetables(season)
    fruits = get_seasonal_fruits(season)
    protein_note = (
        "Rotate protein: Mon/Thu use Eggs; Tue/Fri use Chicken; Wed/Sat use Fish (max 3x/week); Sun use Dal/Paneer"
        if diet == "Non-Veg"
        else "Rotate: Mon=Rajma, Tue=Moong Dal, Wed=Paneer, Thu=Chhole, Fri=Masoor Dal, Sat=Soy chunks, Sun=Toor Dal"
    )

    prompt = f"""You are an expert Indian dietitian creating a diverse 7-day meal plan.

Reference day (style guide only, do NOT copy):
{json.dumps(sample, indent=2)}

Patient: Target {target:.0f} kcal/day | Goal: {goal} | Diet: {diet}
Conditions: {', '.join(diseases) or 'None'} | Season: {season}
Vegetables available: {', '.join(vegs)}
Fruits available: {', '.join(fruits)}
Protein rotation: {protein_note}

STRICT RULES:
1. NO same sabzi on consecutive days - rotate all 7 vegetables
2. Rotate fruits across all 7 days
3. Different dal type each day
4. Each day total ~{target:.0f} kcal
5. ONLY basic Indian home food
6. Respect all medical conditions
7. Non-Veg: fish max 3 times, never fried

Return ONLY a valid JSON array of exactly 7 objects:
[
  {{
    "day": "Monday",
    "breakfast":     {{"items": ["food - qty"], "calories": 0}},
    "mid_morning":   {{"items": ["fruit"], "calories": 0}},
    "lunch":         {{"items": ["food - qty"], "calories": 0}},
    "evening_snack": {{"items": ["food - qty"], "calories": 0}},
    "dinner":        {{"items": ["food - qty"], "calories": 0}},
    "total_calories": 0
  }}
]"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        weekly = json.loads(clean)
        if not isinstance(weekly, list) or len(weekly) != 7:
            raise ValueError
    except Exception:
        weekly = [
            {
                "day": day,
                "breakfast":     {"items": ["2 Roti", "1 bowl Dal"], "calories": 400},
                "mid_morning":   {"items": [fruits[i % len(fruits)] + " - 1 medium"], "calories": 80},
                "lunch":         {"items": ["1 cup Rice", "1 bowl Dal", vegs[i % len(vegs)] + " sabzi"], "calories": 500},
                "evening_snack": {"items": ["Roasted chana - 30g"], "calories": 140},
                "dinner":        {"items": ["2 Roti", "Paneer sabzi - 1 bowl"], "calories": 420},
                "total_calories": 1540,
            }
            for i, day in enumerate(DAYS)
        ]

    return {**state, "weekly_plan": weekly, "current_agent": "weekly_planner_agent"}
