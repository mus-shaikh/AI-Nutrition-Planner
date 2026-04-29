"""
main.py — CLI entry point for testing without Streamlit.

Usage:
    cd nutrition_ai
    python main.py

Make sure your .env file has a valid API key before running.
"""

import json
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(__file__))

from graph.nutrition_graph import nutrition_graph


# ── Sample test input ─────────────────────────────────────────────────────────
SAMPLE_INPUT = {
    "age":             28,
    "gender":          "Female",
    "height_cm":       162.0,
    "weight_kg":       68.0,
    "goal":            "Weight Loss",
    "diet_type":       "Veg",
    "workout_minutes": 45,
    "activity_level":  "Moderate (3-5 days/week)",
    "diseases":        ["Diabetes"],
    "errors":          [],
}


def print_section(title: str, content: str):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")
    print(content)


def main():
    print("\n🌿 AI Nutrition & Diet Planner — LangGraph Multi-Agent System")
    print("Running pipeline with sample input...\n")

    try:
        result = nutrition_graph.invoke(SAMPLE_INPUT)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure your .env file is configured with a valid API key.")
        print("See .env.example for setup instructions.")
        sys.exit(1)

    if result.get("errors"):
        print("⚠️  Validation errors:")
        for err in result["errors"]:
            print(f"   • {err}")
        sys.exit(1)

    # ── Print all outputs ─────────────────────────────────────────────────────
    print_section("1. BMI & HEALTH ANALYSIS",
        f"BMI: {result['bmi']} ({result['bmi_category']})\n\n{result['bmi_interpretation']}")

    print_section("2. CALORIES & MACROS",
        f"BMR:             {result['bmr']} kcal\n"
        f"TDEE:            {result['tdee']} kcal\n"
        f"Target Calories: {result['target_calories']:.0f} kcal\n"
        f"Protein:         {result['protein_g']:.0f}g\n"
        f"Carbs:           {result['carbs_g']:.0f}g\n"
        f"Fats:            {result['fats_g']:.0f}g")

    print_section("3. TODAY'S DIET PLAN",
        json.dumps(result['daily_diet_plan'], indent=2))

    print_section("4. DISEASE ADJUSTMENTS",
        "\n".join(f"  • {a}" for a in result['disease_adjustments']))

    print_section("5. WORKOUT PLAN",
        json.dumps(result['workout_plan'], indent=2))

    print_section("6. WEEKLY MEAL PLAN (7 Days)",
        json.dumps(result['weekly_plan'], indent=2))

    print_section("7. GROCERY LIST",
        json.dumps(result['grocery_list'], indent=2))

    print_section("8. EXPLANATIONS",
        json.dumps(result['explanation'], indent=2))

    print("\n✅ Pipeline complete! Run 'streamlit run ui/app.py' for the full UI.\n")


if __name__ == "__main__":
    main()
