"""
graph/nutrition_graph.py — LangGraph Multi-Agent Orchestrator.

Assembles all 9 agents into a directed StateGraph.
Each node is an independent agent that reads and updates NutritionState.

Flow:
  user_input -> bmi -> calorie -> diet -> disease ->
  workout -> weekly_planner -> grocery -> explanation -> END

Conditional edge after user_input: aborts early on validation errors.
"""

from __future__ import annotations
from langgraph.graph import StateGraph, END
from graph.state import NutritionState

from agents.user_input_agent      import user_input_agent
from agents.bmi_agent             import bmi_agent
from agents.calorie_agent         import calorie_agent
from agents.diet_agent            import diet_agent
from agents.disease_agent         import disease_agent
from agents.workout_agent         import workout_agent
from agents.weekly_planner_agent  import weekly_planner_agent
from agents.grocery_agent         import grocery_agent
from agents.explanation_agent     import explanation_agent


def _route_after_input(state: NutritionState) -> str:
    """Abort the pipeline early if user input validation failed."""
    return "abort" if state.get("errors") else "continue"


def build_nutrition_graph():
    """Build and compile the LangGraph multi-agent workflow."""
    g = StateGraph(NutritionState)

    # Register all agent nodes
    g.add_node("user_input",     user_input_agent)
    g.add_node("bmi",            bmi_agent)
    g.add_node("calorie",        calorie_agent)
    g.add_node("diet",           diet_agent)
    g.add_node("disease",        disease_agent)
    g.add_node("workout",        workout_agent)
    g.add_node("weekly_planner", weekly_planner_agent)
    g.add_node("grocery",        grocery_agent)
    g.add_node("explanation",    explanation_agent)

    # Entry point
    g.set_entry_point("user_input")

    # Conditional edge: abort if validation errors
    g.add_conditional_edges(
        "user_input",
        _route_after_input,
        {"continue": "bmi", "abort": END},
    )

    # Linear pipeline
    g.add_edge("bmi",            "calorie")
    g.add_edge("calorie",        "diet")
    g.add_edge("diet",           "disease")
    g.add_edge("disease",        "workout")
    g.add_edge("workout",        "weekly_planner")
    g.add_edge("weekly_planner", "grocery")
    g.add_edge("grocery",        "explanation")
    g.add_edge("explanation",    END)

    return g.compile()


# Singleton compiled graph — import this everywhere
nutrition_graph = build_nutrition_graph()
