# 🌿 AI Nutrition & Diet Planner
### Production-Grade Multi-Agent System using LangGraph

---

## 🚀 Quick Start

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Configure your FREE API key

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
```

**FREE options (no credit card needed):**

| Provider | Free Limit | Sign-up URL |
|----------|-----------|-------------|
| **Google Gemini** ⭐ | 1,500 req/day | https://ai.google.dev |
| **Groq** | 6K tokens/min | https://console.groq.com |

**Paid options:**
| Provider | Trial | Sign-up URL |
|----------|-------|-------------|
| Anthropic | ~$5 free credits | https://console.anthropic.com |
| OpenAI | ~$5 free credits | https://platform.openai.com |

### Step 3 — Run the Streamlit UI
```bash
streamlit run ui/app.py
```

### Step 4 — Or test via CLI
```bash
python main.py
```

---

## 📂 Project Structure

```
nutrition_ai/
├── agents/
│   ├── __init__.py
│   ├── user_input_agent.py       # Agent 1: Validate inputs, detect season
│   ├── bmi_agent.py              # Agent 2: BMI calculation + LLM interpretation
│   ├── calorie_agent.py          # Agent 3: BMR/TDEE + macro split
│   ├── diet_agent.py             # Agent 4: Daily Indian meal plan
│   ├── disease_agent.py          # Agent 5: Medical dietary adjustments
│   ├── workout_agent.py          # Agent 6: Workout plan
│   ├── weekly_planner_agent.py   # Agent 7: Full 7-day meal plan
│   ├── grocery_agent.py          # Agent 8: Grouped grocery list
│   └── explanation_agent.py      # Agent 9: WHY explanations
├── graph/
│   ├── __init__.py
│   ├── state.py                  # Shared NutritionState TypedDict
│   └── nutrition_graph.py        # LangGraph StateGraph assembly
├── utils/
│   ├── __init__.py
│   ├── llm.py                    # Multi-provider LLM factory
│   └── season.py                 # Indian season auto-detection
├── config/
│   ├── __init__.py
│   └── settings.py               # All configuration constants
├── ui/
│   ├── __init__.py
│   └── app.py                    # Premium Streamlit dashboard
├── data/
│   └── __init__.py               # Reserved for future data files
├── main.py                       # CLI entry point
├── requirements.txt
├── .env.example                  # Environment variable template
└── README.md
```

---

## 🧠 Agent Pipeline

```
User Input Agent
  ↓ (abort if validation errors)
BMI & Health Analysis Agent
  ↓
Calorie Estimation Agent         (Mifflin-St Jeor BMR + PAL)
  ↓
Diet Planning Agent              (Indian home food, seasonal produce)
  ↓
Disease Adjustment Agent         (Diabetes, BP, PCOS, Thyroid etc.)
  ↓
Workout Planning Agent           (beginner-friendly, home-based)
  ↓
Weekly Meal Planner Agent        (7-day plan, no repetition)
  ↓
Grocery List Agent               (grouped, deduplicated)
  ↓
Explanation Agent                (WHY each recommendation)
  ↓
END
```

---

## 🌿 Food Philosophy

- **Only basic Indian home food** — roti, dal, sabzi, curd, paneer
- **Auto-detected seasonal produce** based on current month
- Summer: Lauki, Bhindi, Mango, Watermelon
- Monsoon: Karela, Beans, Banana, Papaya  
- Winter: Palak, Gajar, Orange, Guava
- **No imported foods** — no avocado, quinoa, broccoli
- **Fish** (Non-Veg): max 3x/week, grilled/steamed/curry only

---

## ⚠️ Disclaimer
Educational purposes only. Always consult a qualified dietitian
and physician before making dietary or exercise changes.
