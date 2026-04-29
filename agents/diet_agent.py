"""
agents/diet_agent.py — Agent 4: Daily Diet Planning.

Generates a single-day Indian home meal plan using LLM.
Strict rules: only basic Indian food, seasonal produce,
veg/non-veg handling, goal & disease awareness.
"""

from __future__ import annotations
import json, re
from graph.state import NutritionState
from utils.llm import get_llm
from utils.season import get_seasonal_vegetables, get_seasonal_fruits


def diet_agent(state: NutritionState) -> NutritionState:
    target  = state["target_calories"]
    protein = state["protein_g"]
    carbs   = state["carbs_g"]
    fats    = state["fats_g"]
    goal    = state["goal"]
    diet    = state["diet_type"]
    season  = state.get("season", "winter")
    diseases= state.get("diseases", [])

    vegs   = get_seasonal_vegetables(season)
    fruits = get_seasonal_fruits(season)
    protein_src = (
        "Paneer, Dal (moong/chana/masoor/toor), Soy chunks, Curd, Rajma, Chhole"
        if diet == "Veg"
        else "Eggs, Chicken (home-style curry or grilled), Fish (grilled/steamed/curry - NOT fried), Dal, Curd"
    )

    prompt = f"""You are an expert Indian dietitian planning meals for a home kitchen.

Patient:
- Daily target: {target:.0f} kcal | Protein: {protein:.0f}g | Carbs: {carbs:.0f}g | Fats: {fats:.0f}g
- Goal: {goal} | Diet: {diet} | Conditions: {', '.join(diseases) or 'None'}
- Season: {season} | Vegetables: {', '.join(vegs)} | Fruits: {', '.join(fruits)}
- Protein sources: {protein_src}

STRICT RULES:
1. ONLY basic Indian home food (roti, rice, dal, sabzi, curd etc.)
2. NO imported/fancy foods (no avocado, quinoa, broccoli, oats)
3. Fruits ONLY from seasonal list: {', '.join(fruits)}
4. Vegetables ONLY from seasonal list: {', '.join(vegs)}
5. Non-Veg: fish max 2-3 times/week, NEVER fried
6. Diabetes: low GI, no sugar, small rice portions
7. High BP: low salt, no pickles, no papads
8. PCOS: high protein, balanced carbs
9. Weight Loss: low oil, high protein, controlled carbs
10. Weight Gain: more rice+roti, banana, milk, paneer

Return ONLY valid JSON (no markdown, no extra text):
{{
  "breakfast":     {{"items": ["food - quantity"], "calories": 0, "notes": ""}},
  "mid_morning":   {{"items": ["fruit or light snack"], "calories": 0, "notes": ""}},
  "lunch":         {{"items": ["food - quantity"], "calories": 0, "notes": ""}},
  "evening_snack": {{"items": ["food - quantity"], "calories": 0, "notes": ""}},
  "dinner":        {{"items": ["food - quantity"], "calories": 0, "notes": ""}}
}}"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        plan = json.loads(clean)
    except Exception:
        plan = {
            "breakfast":     {"items": ["2 Roti", "1 bowl Moong Dal", "1 cup Curd"], "calories": 420, "notes": ""},
            "mid_morning":   {"items": [f"1 medium {fruits[0]}"], "calories": 80, "notes": ""},
            "lunch":         {"items": ["1 cup Rice", "1 bowl Dal", f"1 bowl {vegs[0]} sabzi", "Salad"], "calories": 520, "notes": ""},
            "evening_snack": {"items": ["30g Roasted Chana", "1 cup Green Tea (no sugar)"], "calories": 140, "notes": ""},
            "dinner":        {"items": ["2 Roti", f"1 bowl {vegs[1] if len(vegs)>1 else vegs[0]} sabzi", "1 cup Curd"], "calories": 400, "notes": ""},
        }

    return {**state, "daily_diet_plan": plan, "current_agent": "diet_agent"}
