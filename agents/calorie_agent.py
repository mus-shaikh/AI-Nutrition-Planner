

from __future__ import annotations
import json, re
from graph.state import NutritionState
from config.settings import ACTIVITY_MULTIPLIERS
from utils.llm import get_llm


def _bmr(w: float, h: float, age: int, gender: str) -> float:
    base = 10*w + 6.25*h - 5*age
    return round(base + 5 if gender.lower() == "male" else base - 161, 1)


def _tdee(bmr: float, activity: str) -> float:
    return round(bmr * ACTIVITY_MULTIPLIERS.get(activity, 1.375), 0)


def _target(tdee: float, goal: str) -> float:
    if goal == "Weight Loss": return max(1200.0, tdee - 500)
    if goal == "Weight Gain": return tdee + 400
    return tdee


def _fallback_macros(cal: float, goal: str) -> dict:
    p_pct = 0.35 if goal == "Weight Loss" else 0.25
    f_pct = 0.25
    p = round((cal * p_pct) / 4)
    f = round((cal * f_pct) / 9)
    c = round((cal - p*4 - f*9) / 4)
    return {"protein_g": p, "carbs_g": c, "fats_g": f}


def calorie_agent(state: NutritionState) -> NutritionState:
    w, h     = float(state["weight_kg"]), float(state["height_cm"])
    age      = int(state["age"])
    gender   = state["gender"]
    goal     = state["goal"]
    activity = state.get("activity_level", "Light (1-2 days/week)")
    diet     = state.get("diet_type", "Veg")
    diseases = state.get("diseases", [])

    bmr_val  = _bmr(w, h, age, gender)
    tdee_val = _tdee(bmr_val, activity)
    target   = _target(tdee_val, goal)

    prompt = f"""You are a certified sports nutritionist.

Patient: {gender}, Age {age} | Target: {target:.0f} kcal/day
Goal: {goal} | Diet: {diet} | Conditions: {', '.join(diseases) or 'None'}

Calculate optimal daily macros in grams.
Constraints:
- protein*4 + carbs*4 + fats*9 must equal {target:.0f} kcal (within 10 kcal)
- Weight Loss: protein >= 30% calories
- Weight Gain: carbs >= 45% calories
- Diabetes: lower carbs (30-35%), higher protein
- PCOS: balanced carbs (35%), high protein (30%)

Return ONLY valid JSON, no markdown:
{{"protein_g": <int>, "carbs_g": <int>, "fats_g": <int>}}"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        macros = json.loads(clean)
        assert all(k in macros for k in ("protein_g","carbs_g","fats_g"))
    except Exception:
        macros = _fallback_macros(target, goal)

    return {
        **state,
        "bmr":             bmr_val,
        "tdee":            tdee_val,
        "target_calories": target,
        "protein_g":       float(macros["protein_g"]),
        "carbs_g":         float(macros["carbs_g"]),
        "fats_g":          float(macros["fats_g"]),
        "current_agent":   "calorie_agent",
    }
