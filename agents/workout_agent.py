"""
agents/workout_agent.py — Agent 6: Workout Plan Generation.

Generates a beginner-friendly, home-based workout plan
adapted to goal, available time, BMI, age, gender, and
medical conditions. No gym equipment required.
"""

from __future__ import annotations
import json, re
from graph.state import NutritionState
from utils.llm import get_llm


def workout_agent(state: NutritionState) -> NutritionState:
    goal     = state["goal"]
    mins     = state.get("workout_minutes", 30)
    bmi_cat  = state.get("bmi_category", "Normal")
    age      = int(state["age"])
    gender   = state["gender"]
    diseases = state.get("diseases", [])

    prompt = f"""You are a certified Indian fitness coach specialising in home workouts for beginners.

Patient: Age {age}, {gender}, BMI category: {bmi_cat}
Goal: {goal} | Available time: {mins} minutes/day
Medical conditions: {', '.join(diseases) or 'None'}

Design a structured daily workout plan fitting exactly {mins} minutes.
Rules:
1. Beginner-friendly, no gym equipment required
2. Warm-up: 5-10 min | Main: {max(10, mins-15)} min | Cool-down: 5 min
3. Respect conditions: gentle yoga/walking for PCOS/thyroid, no high-impact for knee issues
4. Weight Loss: cardio + bodyweight strength mix
5. Weight Gain: bodyweight strength focus + rest days
6. Maintenance: balanced cardio + flexibility

Return ONLY valid JSON (no markdown):
{{
  "warm_up":     {{"duration_min": 5,  "exercises": ["exercise - duration/reps"]}},
  "main_workout":{{"duration_min": {max(10,mins-15)}, "exercises": ["exercise - duration/reps"]}},
  "cool_down":   {{"duration_min": 5,  "exercises": ["exercise - duration/reps"]}},
  "weekly_schedule": {{
    "Monday": "focus", "Tuesday": "focus", "Wednesday": "focus",
    "Thursday": "focus", "Friday": "focus", "Saturday": "focus", "Sunday": "focus"
  }},
  "tips": ["practical tip 1", "practical tip 2", "practical tip 3"]
}}"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        plan = json.loads(clean)
    except Exception:
        plan = {
            "warm_up":      {"duration_min": 5,  "exercises": ["Jumping jacks - 2 min", "Arm circles - 1 min", "Neck rolls - 1 min", "Light jog in place - 1 min"]},
            "main_workout": {"duration_min": max(10, mins-15), "exercises": ["Brisk walk - 15 min", "Squats - 3x15", "Push-ups - 3x10", "Plank - 3x30 sec"]},
            "cool_down":    {"duration_min": 5,  "exercises": ["Full body stretch - 3 min", "Deep breathing - 2 min"]},
            "weekly_schedule": {d: "Active" for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]},
            "tips": ["Stay hydrated - drink 8-10 glasses of water daily", "Be consistent - results come with regularity", "Listen to your body and rest when needed"],
        }

    return {**state, "workout_plan": plan, "current_agent": "workout_agent"}
