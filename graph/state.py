"""
graph/state.py — Shared LangGraph state TypedDict.

Flows through every agent node. Each agent reads the full state
and returns an updated copy. LangGraph merges updates automatically.
"""

from __future__ import annotations
from typing import Any, Dict, List
from typing_extensions import TypedDict


class NutritionState(TypedDict, total=False):
    # ── User inputs ──────────────────────────────────────────────────────────
    age:             int
    gender:          str        # "Male" | "Female"
    height_cm:       float
    weight_kg:       float
    goal:            str        # "Weight Loss" | "Weight Gain" | "Maintenance"
    diet_type:       str        # "Veg" | "Non-Veg"
    workout_minutes: int        # 0-120
    activity_level:  str
    diseases:        List[str]  # ["Diabetes", "High BP", ...]
    season:          str        # "summer" | "monsoon" | "winter"

    # ── BMI Agent ────────────────────────────────────────────────────────────
    bmi:                float
    bmi_category:       str     # Underweight | Normal | Overweight | Obese
    bmi_interpretation: str

    # ── Calorie Agent ────────────────────────────────────────────────────────
    bmr:             float
    tdee:            float
    target_calories: float
    protein_g:       float
    carbs_g:         float
    fats_g:          float

    # ── Diet Agent ───────────────────────────────────────────────────────────
    daily_diet_plan: Dict[str, Any]
    # { "breakfast": {"items": [...], "calories": int, "notes": str}, ... }

    # ── Disease Agent ────────────────────────────────────────────────────────
    disease_adjustments: List[str]

    # ── Workout Agent ────────────────────────────────────────────────────────
    workout_plan: Dict[str, Any]
    # { "warm_up": {...}, "main_workout": {...}, "cool_down": {...},
    #   "weekly_schedule": {...}, "tips": [...] }

    # ── Weekly Planner ───────────────────────────────────────────────────────
    weekly_plan: List[Dict[str, Any]]   # 7 day-dicts

    # ── Grocery Agent ────────────────────────────────────────────────────────
    grocery_list: Dict[str, List[str]]
    # { "Vegetables": [...], "Fruits": [...], "Dairy": [...],
    #   "Grains": [...], "Protein": [...], "Pantry": [...] }

    # ── Explanation Agent ────────────────────────────────────────────────────
    explanation: Dict[str, str]
    # { "why_these_calories": str, "why_this_diet": str,
    #   "why_this_workout": str, "why_seasonal_foods": str }

    # ── Control ──────────────────────────────────────────────────────────────
    errors:        List[str]
    current_agent: str
