"""
ui/app.py — Premium Streamlit Dashboard for AI Nutrition Planner.

BUGS FIXED:
1. Removed threading entirely — Streamlit + threads = broken session state
2. Direct nutrition_graph.invoke() inside st.spinner() works correctly
3. Results stored in st.session_state so they persist across reruns
4. Proper error display if API key or pipeline fails

Run:
    cd nutrition_ai
    streamlit run ui/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from graph.nutrition_graph import nutrition_graph
from config.settings import DISEASE_OPTIONS, GOAL_OPTIONS, ACTIVITY_MULTIPLIERS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Nutrition Planner",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
:root {
  --saffron:#E8751A; --turmeric:#F5A623; --cream:#FDF6EC;
  --forest:#2D5016; --mint:#6BAF6B; --charcoal:#1C1C1C;
  --warm-grey:#6B6560; --card-bg:#FFFFFF; --border:#E8DFD0;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:var(--cream);color:var(--charcoal);}
h1,h2,h3{font-family:'Playfair Display',serif;}
section[data-testid="stSidebar"]{background:var(--forest);}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] p{color:#d4e6c3 !important;}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{color:var(--turmeric) !important;}
.main-header{background:linear-gradient(135deg,var(--forest) 0%,#4a7c2f 100%);
  padding:2.5rem 2rem;border-radius:16px;margin-bottom:2rem;color:white;
  position:relative;overflow:hidden;}
.main-header::before{content:'🌿';font-size:8rem;position:absolute;right:-1rem;top:-1rem;opacity:0.12;}
.main-header h1{font-family:'Playfair Display',serif;font-size:2.8rem;margin:0;color:white;}
.main-header p{color:#b8d4a0;margin-top:0.5rem;font-size:1.1rem;}
.metric-card{background:var(--card-bg);border:1px solid var(--border);border-radius:12px;
  padding:1.25rem 1.5rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);}
.metric-card .val{font-family:'Playfair Display',serif;font-size:2.2rem;font-weight:700;color:var(--forest);}
.metric-card .lbl{font-size:.82rem;color:var(--warm-grey);text-transform:uppercase;letter-spacing:.08em;margin-top:.25rem;}
.metric-card .sub{font-size:.9rem;color:var(--saffron);font-weight:500;margin-top:.2rem;}
.section-hdr{display:flex;align-items:center;gap:.6rem;margin:1.5rem 0 1rem;
  border-bottom:2px solid var(--turmeric);padding-bottom:.5rem;}
.section-hdr h2{font-family:'Playfair Display',serif;font-size:1.6rem;color:var(--forest);margin:0;}
.meal-card{background:var(--card-bg);border-left:4px solid var(--saffron);
  border-radius:0 10px 10px 0;padding:1rem 1.25rem;margin-bottom:.75rem;
  box-shadow:0 1px 4px rgba(0,0,0,.06);}
.meal-card h4{color:var(--saffron);font-size:.85rem;text-transform:uppercase;
  letter-spacing:.1em;margin:0 0 .5rem;}
.meal-card ul{margin:0;padding-left:1.2rem;}
.meal-card li{color:var(--charcoal);font-size:.95rem;line-height:1.6;}
.meal-card .cbadge{font-size:.78rem;background:var(--cream);border:1px solid var(--border);
  border-radius:20px;padding:2px 8px;color:var(--warm-grey);float:right;}
.grocery-cat{background:var(--card-bg);border:1px solid var(--border);
  border-radius:10px;padding:1rem 1.25rem;margin-bottom:.75rem;}
.grocery-cat h4{color:var(--forest);font-size:.9rem;text-transform:uppercase;
  letter-spacing:.08em;margin:0 0 .6rem;}
.adj-tag{background:#FFF3E0;border:1px solid var(--turmeric);border-radius:6px;
  padding:6px 12px;font-size:.9rem;color:#5D4037;margin-bottom:.5rem;}
.exp-box{background:linear-gradient(135deg,#f0f7eb 0%,#e8f4f8 100%);
  border:1px solid var(--mint);border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.exp-box h4{color:var(--forest);margin-bottom:.5rem;}
.exp-box p{color:var(--charcoal);line-height:1.7;margin:0;}
.workout-block{background:var(--card-bg);border-radius:12px;padding:1.25rem;
  border:1px solid var(--border);margin-bottom:.75rem;}
.workout-block h4{color:var(--forest);font-family:'Playfair Display',serif;margin-bottom:.6rem;}
.bmi-bar{height:14px;border-radius:7px;
  background:linear-gradient(to right,#64B5F6,#81C784,#FFB74D,#E57373);
  position:relative;margin:1rem 0 .5rem;}
.bmi-marker{position:absolute;top:-6px;width:26px;height:26px;background:var(--charcoal);
  border:3px solid white;border-radius:50%;transform:translateX(-50%);
  box-shadow:0 2px 6px rgba(0,0,0,.3);}
div.stButton>button{background:var(--forest);color:white;border:none;border-radius:8px;
  font-family:'DM Sans',sans-serif;font-size:1rem;font-weight:500;
  padding:.6rem 2rem;width:100%;}
div.stButton>button:hover{background:#3d6b1e;}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MEAL_ICONS = {
    "breakfast":     "🌅 Breakfast",
    "mid_morning":   "🍎 Mid-Morning",
    "lunch":         "🍛 Lunch",
    "evening_snack": "☕ Evening Snack",
    "dinner":        "🌙 Dinner",
}
CAT_ICONS  = {"Vegetables":"🥦","Fruits":"🍎","Dairy":"🥛","Grains":"🌾","Protein":"🍗","Pantry":"🫙"}
EXP_ICONS  = {"why_these_calories":"🔥","why_this_diet":"🥗","why_this_workout":"💪","why_seasonal_foods":"🌿"}
EXP_TITLES = {
    "why_these_calories": "Why These Calories?",
    "why_this_diet":      "Why This Diet?",
    "why_this_workout":   "Why This Workout?",
    "why_seasonal_foods": "Why Seasonal Foods?",
}


# ── Helper functions ──────────────────────────────────────────────────────────
def bmi_pct(bmi):
    return min(100, max(0, (float(bmi) - 10) / 30 * 100))


def sec_hdr(icon, title):
    st.markdown(
        f"<div class='section-hdr'>"
        f"<span style='font-size:1.5rem'>{icon}</span>"
        f"<h2>{title}</h2></div>",
        unsafe_allow_html=True,
    )


def meal_card(slot, data):
    items     = "".join(f"<li>{i}</li>" for i in data.get("items", []))
    cal       = data.get("calories", "—")
    note      = data.get("notes", "")
    note_html = (
        f"<p style='font-size:.82rem;color:#888;margin:.4rem 0 0'>{note}</p>"
        if note else ""
    )
    st.markdown(
        f"<div class='meal-card'>"
        f"<h4>{MEAL_ICONS.get(slot, slot)} "
        f"<span class='cbadge'>~{cal} kcal</span></h4>"
        f"<ul>{items}</ul>{note_html}</div>",
        unsafe_allow_html=True,
    )


# ── Sidebar inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Your Profile")
    st.markdown("---")

    st.markdown("### 👤 Personal Details")
    age    = st.slider("Age", 15, 80, 28)
    gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1: height = st.number_input("Height (cm)", 140, 220, 162)
    with c2: weight = st.number_input("Weight (kg)",  30, 200,  68)

    st.markdown("### 🎯 Goal & Diet")
    goal      = st.selectbox("Goal", GOAL_OPTIONS)
    diet_type = st.radio("Diet Type", ["Veg", "Non-Veg"], horizontal=True)

    st.markdown("### 🏃 Activity")
    activity    = st.selectbox("Activity Level", list(ACTIVITY_MULTIPLIERS.keys()), index=1)
    workout_min = st.slider("Workout Time (min/day)", 0, 120, 45, step=5)

    st.markdown("### 🩺 Health Conditions")
    diseases = st.multiselect("Conditions (select all that apply)", DISEASE_OPTIONS[1:])

    st.markdown("---")
    go_btn = st.button("✨ Generate My Plan")

    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")
    for agent_name in [
        "User Input", "BMI Analysis", "Calorie Estimation", "Diet Planning",
        "Disease Adjustment", "Workout Planning", "Weekly Planner",
        "Grocery List", "Explanation",
    ]:
        st.markdown(
            f"<div style='padding:3px 0;font-size:.82rem;color:#b8d4a0'>▸ {agent_name}</div>",
            unsafe_allow_html=True,
        )


# ── Main header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
  <h1>AI Nutrition & Diet Planner</h1>
  <p>Personalised Indian home-food plans · Powered by LangGraph Multi-Agent AI</p>
</div>
""", unsafe_allow_html=True)


# ── Landing page (no result yet) ──────────────────────────────────────────────
if not go_btn and "result" not in st.session_state:
    c1, c2, c3 = st.columns(3)
    for col, e, t, d in [
        (c1, "🤖", "Multi-Agent AI",  "9 specialised AI agents collaborate dynamically using LangGraph"),
        (c2, "🌿", "Pure Indian Food", "Roti, dal, sabzi, seasonal produce — no fancy imports"),
        (c3, "🩺", "Health-Aware",     "Tailored for Diabetes, BP, PCOS, Thyroid & more"),
    ]:
        with col:
            st.markdown(
                f"<div class='metric-card' style='text-align:left'>"
                f"<div style='font-size:2rem;margin-bottom:.5rem'>{e}</div>"
                f"<div style='font-weight:600;color:var(--forest);font-size:1rem'>{t}</div>"
                f"<div style='color:var(--warm-grey);font-size:.88rem;margin-top:.3rem'>{d}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    st.info("👈 Fill in your profile in the sidebar and click **Generate My Plan** to begin!")
    st.stop()


# ── RUN PIPELINE (no threads — direct invocation) ─────────────────────────────
if go_btn:
    user_inputs = {
        "age":             int(age),
        "gender":          gender,
        "height_cm":       float(height),
        "weight_kg":       float(weight),
        "goal":            goal,
        "diet_type":       diet_type,
        "workout_minutes": int(workout_min),
        "activity_level":  activity,
        "diseases":        list(diseases),
        "errors":          [],
    }

    # ✅ FIX: Direct call inside spinner — no threading, no race conditions
    with st.spinner("🤖 AI agents are working on your personalised plan… (this takes ~60 seconds)"):
        try:
            result = nutrition_graph.invoke(user_inputs)
            st.session_state["result"] = result
        except Exception as e:
            st.error(f"❌ Pipeline failed: {e}")
            st.markdown("""
**Troubleshooting:**
1. Open your `.env` file and check:
   - `LLM_PROVIDER=google` *(no quotes, no spaces)*
   - `GOOGLE_API_KEY=AIza...` *(your actual key)*
2. Make sure the `.env` file is in the `nutrition_ai/` folder
3. Run `pip install -r requirements.txt` again
            """)
            st.stop()


# ── Load result ───────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.stop()

result = st.session_state["result"]

if result.get("errors"):
    st.error("⚠️ Input validation errors:")
    for err in result["errors"]:
        st.markdown(f"- {err}")
    st.stop()


# ════════════════════════════════════════════════════════════════════════
# SECTION 1 — Health Overview
# ════════════════════════════════════════════════════════════════════════
sec_hdr("📊", "Health Overview")

bmi_val    = result.get("bmi", 0)
bmi_cat    = result.get("bmi_category", "—")
target_cal = result.get("target_calories", 0)
protein_g  = result.get("protein_g", 0)
carbs_g    = result.get("carbs_g", 0)
fats_g     = result.get("fats_g", 0)

bmi_color = {
    "Underweight": "#64B5F6",
    "Normal":      "#81C784",
    "Overweight":  "#FFB74D",
    "Obese":       "#E57373",
}.get(bmi_cat, "#888888")

mcols = st.columns(5)
for col, (val, label, sub, color) in zip(mcols, [
    (bmi_val,             "BMI",             bmi_cat, bmi_color),
    (f"{target_cal:.0f}", "Target kcal/day", goal,    "var(--saffron)"),
    (f"{protein_g:.0f}g", "Protein",         "daily", "var(--saffron)"),
    (f"{carbs_g:.0f}g",   "Carbs",           "daily", "var(--saffron)"),
    (f"{fats_g:.0f}g",    "Fats",            "daily", "var(--saffron)"),
]):
    with col:
        val_style = f"color:{bmi_color}" if label == "BMI" else ""
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='val' style='{val_style}'>{val}</div>"
            f"<div class='lbl'>{label}</div>"
            f"<div class='sub' style='color:{color}'>{sub}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

# BMI gradient bar with marker
pct = bmi_pct(bmi_val)
st.markdown(
    f"<div class='bmi-bar'>"
    f"<div class='bmi-marker' style='left:{pct}%'></div>"
    f"</div>"
    f"<div style='display:flex;justify-content:space-between;"
    f"font-size:.75rem;color:var(--warm-grey);margin-bottom:1rem'>"
    f"<span>Underweight &lt;18.5</span>"
    f"<span>Normal 18.5–24.9</span>"
    f"<span>Overweight 25–29.9</span>"
    f"<span>Obese ≥30</span></div>",
    unsafe_allow_html=True,
)

with st.expander("💬 Personalised Health Interpretation", expanded=True):
    interp = result.get("bmi_interpretation", "")
    st.markdown(f"<p style='line-height:1.8'>{interp}</p>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# SECTION 2 — Today's Meal Plan
# ════════════════════════════════════════════════════════════════════════
sec_hdr("🥗", "Today's Meal Plan")

daily = result.get("daily_diet_plan", {})
if daily:
    for slot in ["breakfast", "mid_morning", "lunch", "evening_snack", "dinner"]:
        if slot in daily:
            meal_card(slot, daily[slot])
else:
    st.warning("Diet plan not available. Check the terminal for errors.")

adj = result.get("disease_adjustments", [])
if adj and adj != ["No medical conditions flagged. Follow the standard plan."]:
    with st.expander("🩺 Medical Dietary Adjustments", expanded=True):
        for a in adj:
            st.markdown(f"<div class='adj-tag'>⚡ {a}</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# SECTION 3 — 7-Day Meal Plan
# ════════════════════════════════════════════════════════════════════════
sec_hdr("📅", "7-Day Meal Plan")

weekly = result.get("weekly_plan", [])
if weekly:
    tabs = st.tabs([d.get("day", f"Day {i+1}") for i, d in enumerate(weekly)])
    for tab, day_data in zip(tabs, weekly):
        with tab:
            st.caption(f"Total: ~{day_data.get('total_calories', '—')} kcal")
            for slot in ["breakfast", "mid_morning", "lunch", "evening_snack", "dinner"]:
                if slot in day_data:
                    meal_card(slot, day_data[slot])
else:
    st.warning("Weekly plan not available.")


# ════════════════════════════════════════════════════════════════════════
# SECTION 4 — Workout Plan
# ════════════════════════════════════════════════════════════════════════
sec_hdr("💪", "Workout Plan")

workout = result.get("workout_plan", {})
if workout:
    wc1, wc2, wc3 = st.columns(3)
    for col, key, icon, bg in [
        (wc1, "warm_up",      "🔥", "#FFF3E0"),
        (wc2, "main_workout", "⚡", "#E8F5E9"),
        (wc3, "cool_down",    "❄️", "#E3F2FD"),
    ]:
        with col:
            blk  = workout.get(key, {})
            dur  = blk.get("duration_min", "—")
            exs  = "".join(f"<li>{e}</li>" for e in blk.get("exercises", []))
            lbl  = key.replace("_", " ").title()
            st.markdown(
                f"<div class='workout-block' style='background:{bg}'>"
                f"<h4>{icon} {lbl} "
                f"<span style='font-size:.8rem;color:var(--warm-grey);font-weight:normal'>"
                f"({dur} min)</span></h4>"
                f"<ul style='padding-left:1.2rem;margin:0'>{exs}</ul></div>",
                unsafe_allow_html=True,
            )

    sched = workout.get("weekly_schedule", {})
    if sched:
        st.markdown("**Weekly Schedule**")
        sc = st.columns(7)
        for col, (day, focus) in zip(sc, sched.items()):
            with col:
                st.markdown(
                    f"<div style='background:var(--card-bg);border:1px solid var(--border);"
                    f"border-radius:8px;padding:8px;text-align:center;font-size:.82rem'>"
                    f"<div style='color:var(--forest);font-weight:600'>{day[:3]}</div>"
                    f"<div style='color:var(--warm-grey);margin-top:4px;font-size:.78rem'>{focus}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    tips = workout.get("tips", [])
    if tips:
        with st.expander("💡 Workout Tips"):
            for tip in tips:
                st.markdown(f"• {tip}")
else:
    st.warning("Workout plan not available.")


# ════════════════════════════════════════════════════════════════════════
# SECTION 5 — Grocery List
# ════════════════════════════════════════════════════════════════════════
sec_hdr("🛒", "Weekly Grocery List")

grocery = result.get("grocery_list", {})
if grocery:
    gc1, gc2 = st.columns(2)
    for i, (cat, items) in enumerate(grocery.items()):
        with (gc1 if i % 2 == 0 else gc2):
            icon = CAT_ICONS.get(cat, "📦")
            rows = "".join(
                f"<div style='padding:3px 0;font-size:.9rem;"
                f"border-bottom:1px solid #f0ebe3'>• {it}</div>"
                for it in items
            )
            st.markdown(
                f"<div class='grocery-cat'><h4>{icon} {cat}</h4>{rows}</div>",
                unsafe_allow_html=True,
            )
else:
    st.warning("Grocery list not available.")


# ════════════════════════════════════════════════════════════════════════
# SECTION 6 — Why This Plan?
# ════════════════════════════════════════════════════════════════════════
sec_hdr("📖", "Why This Plan?")

explanation = result.get("explanation", {})
if explanation:
    ec1, ec2 = st.columns(2)
    for i, (key, para) in enumerate(explanation.items()):
        with (ec1 if i % 2 == 0 else ec2):
            icon  = EXP_ICONS.get(key, "💡")
            title = EXP_TITLES.get(key, key.replace("_", " ").title())
            st.markdown(
                f"<div class='exp-box'>"
                f"<h4>{icon} {title}</h4>"
                f"<p>{para}</p></div>",
                unsafe_allow_html=True,
            )
else:
    st.warning("Explanations not available.")


# ════════════════════════════════════════════════════════════════════════
# SECTION 7 — Architecture
# ════════════════════════════════════════════════════════════════════════
with st.expander("🤖 Multi-Agent Architecture — How It Works", expanded=False):
    st.markdown("""
### Why This is Multi-Agent AI (Not RAG)

| Aspect | RAG System | This System |
|--------|-----------|-------------|
| Architecture | Retrieve → Generate | 9 agents, each with own responsibility |
| Intelligence | One LLM call | Specialised LLM call per agent |
| State | Stateless | Shared `NutritionState` evolves across agents |
| Routing | Fixed | Conditional edges (abort on validation failure) |
| Scalability | Add prompts | Add a new agent node |

### LangGraph Flow
```
user_input → bmi → calorie → diet → disease →
workout → weekly_planner → grocery → explanation → END
```
    """)

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:var(--warm-grey);font-size:.82rem'>"
    "AI Nutrition Planner · Built with LangGraph · "
    "Always consult a qualified dietitian before major dietary changes.</p>",
    unsafe_allow_html=True,
)
