import os
import json
import re
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.0-flash"


def _call_gemini(system: str, user: str) -> dict:
    """Call Gemini and parse the JSON response. Raises ValueError on bad output."""
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system,
    )
    response = model.generate_content(user)
    raw = response.text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\n\nRaw response:\n{raw}")


DIET_SYSTEM = """
You are an expert sports nutritionist and dietitian.
Given a user profile and their body analysis, produce a personalised dietary plan.
Respond ONLY with a valid JSON object — no explanation, no markdown, no preamble.
Use exactly these keys:
{
  "tdee": <float, total daily energy expenditure in kcal>,
  "daily_calories": <int, adjusted target calories>,
  "caloric_strategy": <"bulk" | "cut" | "recomp">,
  "caloric_adjustment": <int, e.g. 300 or -400>,
  "protein_g": <int>,
  "carbs_g": <int>,
  "fats_g": <int>,
  "meals_per_day": <int>,
  "meal_complexity": <"simple" | "moderate" | "detailed">,
  "water_intake_liters": <float>,
  "cheat_meals_per_week": <int>,
  "dietary_preference": <string or null>,
  "foods_to_avoid": <string, comma-separated or null>,
  "diet_reasoning": <string, 2-3 sentence explanation>
}
"""


def run_diet_agent(user: dict, body_analysis: dict) -> dict:
    """
    user: dict of User model fields
    body_analysis: dict of BodyAnalysis model fields
    Returns dict ready to be saved as DietaryPlan.
    """
    prompt = f"""
USER PROFILE:
{json.dumps(user, indent=2)}

BODY ANALYSIS:
{json.dumps(body_analysis, indent=2)}

Generate the optimal dietary plan for this user based on their goal, body composition, and lifestyle.
"""
    return _call_gemini(DIET_SYSTEM, prompt)