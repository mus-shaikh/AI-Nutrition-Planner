"""
agents/disease_agent.py — Agent 5: Disease-Specific Dietary Adjustments.

Reviews the generated diet plan and produces actionable,
condition-specific dietary guidance using the LLM.
Acts as a medical safety layer in the pipeline.
"""

from __future__ import annotations
import json, re
from graph.state import NutritionState
from utils.llm import get_llm


def disease_agent(state: NutritionState) -> NutritionState:
    diseases = state.get("diseases", [])

    if not diseases:
        return {
            **state,
            "disease_adjustments": ["No medical conditions flagged. Follow the standard plan."],
            "current_agent": "disease_agent",
        }

    prompt = f"""You are a clinical dietitian reviewing a meal plan for an Indian patient.

Diagnosed conditions: {', '.join(diseases)}
Patient goal: {state['goal']} | Diet type: {state['diet_type']}
Current plan summary: {json.dumps(state.get('daily_diet_plan', {}), indent=2)}

Provide 6-8 SPECIFIC, ACTIONABLE dietary adjustments for each condition.
Each instruction must be practical for an Indian home kitchen.

Examples of good adjustments:
- "Replace white rice with small portions of red/brown rice or millets (bajra/jowar)"
- "Use rock salt instead of regular salt to manage blood pressure"
- "Avoid maida-based items like white bread, puri, bhatura"

Return ONLY a JSON array of strings. No markdown, no explanation:
["adjustment 1", "adjustment 2", ...]"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        adjustments = json.loads(clean)
        if not isinstance(adjustments, list):
            raise ValueError
    except Exception:
        adjustments = [f"Consult a doctor for specific {d} dietary advice." for d in diseases]

    return {**state, "disease_adjustments": adjustments, "current_agent": "disease_agent"}
