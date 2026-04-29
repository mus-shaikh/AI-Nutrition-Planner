"""
agents/explanation_agent.py — Agent 9: Plan Explanation Generator.

Final agent in the pipeline. Synthesises all previous outputs
and generates human-readable explanations for WHY each
recommendation was made — building trust and understanding.
"""

from __future__ import annotations
import json, re
from graph.state import NutritionState
from utils.llm import get_llm


def explanation_agent(state: NutritionState) -> NutritionState:
    prompt = f"""You are a friendly Indian nutrition coach writing to a patient.

Patient summary:
- Age: {state['age']} | Gender: {state['gender']}
- BMI: {state.get('bmi','N/A')} ({state.get('bmi_category','N/A')})
- Goal: {state['goal']} | Diet: {state['diet_type']}
- Target: {state.get('target_calories','N/A'):.0f} kcal | Protein: {state.get('protein_g','N/A'):.0f}g | Carbs: {state.get('carbs_g','N/A'):.0f}g | Fats: {state.get('fats_g','N/A'):.0f}g
- Conditions: {', '.join(state.get('diseases',[])) or 'None'}
- Season: {state.get('season','winter')}
- Disease adjustments applied: {len(state.get('disease_adjustments',[]))} adjustments

Write 4 short explanation paragraphs (3-5 sentences each) in simple, warm language.
Explain the reasoning behind recommendations in a way a non-expert can understand.

Return ONLY valid JSON (no markdown):
{{
  "why_these_calories": "<explain the calorie target calculation and why it suits their goal>",
  "why_this_diet": "<explain the Indian home food philosophy and specific food choices>",
  "why_this_workout": "<explain the workout plan rationale given their goal and fitness level>",
  "why_seasonal_foods": "<explain importance of eating seasonal Indian foods for health>"
}}"""

    raw = get_llm().invoke(prompt).content.strip()
    clean = re.sub(r"```json|```", "", raw).strip()
    try:
        explanation = json.loads(clean)
    except Exception:
        explanation = {
            "why_these_calories": f"Your daily target of {state.get('target_calories',0):.0f} kcal is calculated from your basal metabolic rate and activity level, then adjusted for {state['goal'].lower()}. This ensures you have enough energy while making steady progress toward your goal.",
            "why_this_diet":      "We use simple Indian home food because it is nutritious, affordable, easily available, and your body is already adapted to it. Seasonal vegetables and traditional dals provide excellent micronutrients without any expense.",
            "why_this_workout":   "Your workout is designed to fit your schedule and current fitness level. Consistency with even 30-45 minutes daily yields better results than intense but irregular sessions.",
            "why_seasonal_foods": "Seasonal Indian fruits and vegetables are fresher, more nutritious, cheaper, and naturally suited to your body's needs in that climate. Eating in sync with seasons is a time-tested Ayurvedic principle.",
        }

    return {**state, "explanation": explanation, "current_agent": "explanation_agent"}
