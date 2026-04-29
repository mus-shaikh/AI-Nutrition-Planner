"""
agents/grocery_agent.py — Agent 8: Weekly Grocery List Generator.

Scans the full 7-day meal plan, deduplicates items,
and compiles a practical grouped grocery list with quantities.
"""

from __future__ import annotations
import json, re
from graph.state import NutritionState
from utils.llm import get_llm


def grocery_agent(state: NutritionState) -> NutritionState:
    weekly = state.get("weekly_plan", [])
    diet   = state["diet_type"]
    season = state.get("season", "winter")

    prompt = f"""You are a smart kitchen assistant for an Indian household.

Here is a 7-day meal plan:
{json.dumps(weekly, indent=2)}

Diet type: {diet} | Season: {season}

Generate a WEEKLY GROCERY LIST that:
1. Combines and deduplicates all items across all 7 days
2. Groups into practical categories
3. Gives realistic quantities (e.g., "Spinach (Palak) - 500g", "Eggs - 12 pcs")
4. Includes only items that actually appear in the meal plan
5. Adds common pantry staples needed for Indian cooking

Return ONLY valid JSON (no markdown):
{{
  "Vegetables": ["item - quantity"],
  "Fruits":     ["item - quantity"],
  "Dairy":      ["item - quantity"],
  "Grains":     ["item - quantity"],
  "Protein":    ["item - quantity"],
  "Pantry":     ["item - quantity"]
}}"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        grocery = json.loads(clean)
    except Exception:
        grocery = {
            "Vegetables": ["Mixed seasonal vegetables - 2 kg"],
            "Fruits":     ["Mixed seasonal fruits - 1 kg"],
            "Dairy":      ["Milk - 2 L", "Curd (Dahi) - 500g", "Paneer - 300g"],
            "Grains":     ["Wheat flour (Atta) - 2 kg", "Rice - 1 kg", "Assorted Dal - 500g each"],
            "Protein":    ["Eggs - 12 pcs"] if diet == "Non-Veg" else ["Soy chunks - 300g", "Rajma - 500g"],
            "Pantry":     ["Mustard oil - 500ml", "Turmeric powder - 100g", "Cumin seeds - 100g",
                          "Coriander powder - 100g", "Red chilli powder - 100g", "Salt - 500g",
                          "Ginger-Garlic paste - 200g", "Tomatoes - 1 kg", "Onions - 1 kg"],
        }

    return {**state, "grocery_list": grocery, "current_agent": "grocery_agent"}
