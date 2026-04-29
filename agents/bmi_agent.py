"""
agents/bmi_agent.py — Agent 2: BMI Calculation & Health Analysis.

- Calculates BMI: weight(kg) / height(m)^2
- Classifies: Underweight / Normal / Overweight / Obese
- LLM generates personalised health interpretation
"""

from __future__ import annotations
from graph.state import NutritionState
from utils.llm import get_llm


def _bmi(weight_kg: float, height_cm: float) -> float:
    return round(weight_kg / (height_cm / 100) ** 2, 1)


def _classify(bmi: float) -> str:
    if bmi < 18.5:   return "Underweight"
    elif bmi < 25.0: return "Normal"
    elif bmi < 30.0: return "Overweight"
    else:            return "Obese"


def bmi_agent(state: NutritionState) -> NutritionState:
    weight   = float(state["weight_kg"])
    height   = float(state["height_cm"])
    age      = int(state["age"])
    gender   = state["gender"]
    goal     = state["goal"]
    diseases = state.get("diseases", [])

    bmi_val  = _bmi(weight, height)
    category = _classify(bmi_val)

    prompt = f"""You are a compassionate Indian health advisor.

Patient: Age {age}, {gender}, Weight {weight}kg, Height {height}cm
BMI: {bmi_val} ({category}) | Goal: {goal}
Medical conditions: {', '.join(diseases) if diseases else 'None'}

Write a warm, personalised BMI health interpretation in 3-4 sentences.
- Explain what this BMI means for them personally
- Flag any health risks considering their conditions
- Motivate them toward their goal
- Write as flowing prose (no bullet points, no headers)
"""

    response = get_llm().invoke(prompt)

    return {
        **state,
        "bmi":                bmi_val,
        "bmi_category":       category,
        "bmi_interpretation": response.content.strip(),
        "current_agent":      "bmi_agent",
    }
