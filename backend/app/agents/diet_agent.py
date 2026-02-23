import json
from app.agents.gemini_client import call_gemini, parse_json


def run_diet_agent(user: dict, body_analysis: dict) -> dict:
    """
    Call Gemini to generate a personalized diet plan.
    """
    prompt = f"""
You are an expert clinical nutritionist AI.
Analyze the user and their structural body data to provide a deterministic nutrition plan.

User Data: {json.dumps(user)}
Body Analysis: {json.dumps(body_analysis)}

Return ONLY valid JSON with exactly the following keys and appropriate types:
- tdee (float)
- daily_calories (int)
- caloric_strategy (string: "bulk", "cut", or "recomp")
- caloric_adjustment (int: added or subtracted calories from TDEE)
- protein_g (int)
- carbs_g (int)
- fats_g (int)
- meals_per_day (int)
- meal_complexity (string: "simple", "moderate", "complex")
- water_intake_liters (float)
- cheat_meals_per_week (int)
- dietary_preference (string based on user constraints)
- foods_to_avoid (string based on user constraints)
- diet_reasoning (string describing your logic based on the targets and user preferences)

Ensure the macros make physiological sense for the caloric target.
Output ONLY JSON, no markdown formatting like ```json.
"""
    try:
        text = call_gemini(prompt)
        return parse_json(text)
    except Exception as e:
        print(f"Diet agent error: {e}")
        return {
            "tdee": 2500.0,
            "daily_calories": 2450,
            "caloric_strategy": "recomp",
            "caloric_adjustment": -50,
            "protein_g": 170,
            "carbs_g": 280,
            "fats_g": 75,
            "meals_per_day": 4,
            "meal_complexity": "simple",
            "water_intake_liters": 3.2,
            "cheat_meals_per_week": 1,
            "dietary_preference": "high-protein balanced",
            "foods_to_avoid": "sugary drinks, deep-fried foods",
            "diet_reasoning": f"Fallback dietary targets due to API error: {e}",
        }
