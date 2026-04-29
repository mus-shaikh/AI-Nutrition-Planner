"""
config/settings.py — Central configuration for the AI Nutrition Planner.

LLM_PROVIDER options (set in .env):
  "google"    -> Google Gemini 2.5 Flash  (FREE - 1500 req/day, no card)
  "groq"      -> Groq Llama 3.3-70b       (FREE - fastest, no card)
  "anthropic" -> Anthropic Claude Sonnet  (Paid - ~$5 trial)
  "openai"    -> OpenAI GPT-4o-mini       (Paid)

WINDOWS NOTE: If your .env has CRLF line endings (common on Windows),
values may contain \r characters. All settings here use .strip() to fix this.
"""

import os
from dotenv import load_dotenv

# Load .env with override=True so Windows CRLF values are re-read correctly
load_dotenv(override=True)


def _env(key: str, default: str = "") -> str:
    """Get env var and strip all whitespace/CRLF (Windows-safe)."""
    return (os.getenv(key) or default).strip().strip("\r\n").strip()


# ── Provider & API Keys ───────────────────────────────────────────────────────
LLM_PROVIDER      = _env("LLM_PROVIDER", "google").lower()
GOOGLE_API_KEY    = _env("GOOGLE_API_KEY")
GROQ_API_KEY      = _env("GROQ_API_KEY")
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
OPENAI_API_KEY    = _env("OPENAI_API_KEY")

# ── Model names per provider ──────────────────────────────────────────────────
LLM_MODELS = {
    "google":    "gemini-2.0-flash",
    "groq":      "llama-3.3-70b-versatile",
    "anthropic": "claude-sonnet-4-20250514",
    "openai":    "gpt-4o-mini",
}

LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS  = 4096

# ── Indian seasonal mapping ───────────────────────────────────────────────────
SEASON_MAP = {
    1: "winter", 2: "winter",
    3: "summer", 4: "summer", 5: "summer", 6: "summer",
    7: "monsoon", 8: "monsoon", 9: "monsoon",
    10: "winter", 11: "winter", 12: "winter",
}

SEASONAL_VEGETABLES = {
    "summer":  ["Lauki", "Tori", "Bhindi", "Cucumber", "Pumpkin", "Tinda"],
    "monsoon": ["Tinda", "Karela", "French Beans", "Arbi", "Ridgegourd", "Parwal"],
    "winter":  ["Palak", "Methi", "Carrot", "Cauliflower", "Peas", "Gajar", "Matar", "Mooli"],
}

SEASONAL_FRUITS = {
    "summer":  ["Mango", "Watermelon", "Muskmelon", "Litchi", "Jamun"],
    "monsoon": ["Banana", "Papaya", "Pear", "Jamun", "Guava"],
    "winter":  ["Orange", "Guava", "Pomegranate", "Amla", "Banana", "Apple"],
}

# ── Options ───────────────────────────────────────────────────────────────────
DISEASE_OPTIONS = [
    "None", "Diabetes", "High BP", "PCOS", "Thyroid",
    "High Cholesterol", "Kidney Issues", "Fatty Liver",
]

GOAL_OPTIONS = ["Weight Loss", "Weight Gain", "Maintenance"]

ACTIVITY_MULTIPLIERS = {
    "Sedentary (desk job, no exercise)": 1.2,
    "Light (1-2 days/week)":            1.375,
    "Moderate (3-5 days/week)":         1.55,
    "Active (6-7 days/week)":           1.725,
    "Very Active (2x training/day)":    1.9,
}
