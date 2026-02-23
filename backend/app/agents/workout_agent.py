import json
from app.agents.gemini_client import call_gemini, parse_json


def run_workout_agent(user: dict, body_analysis: dict) -> dict:
    """
    Call Gemini to generate a personalized workout strategy.
    """
    prompt = f"""
You are an expert fitness coach and biomechanics AI.
Analyze the user and their structural body data to provide a deterministic workout plan.

User Data: {json.dumps(user)}
Body Analysis: {json.dumps(body_analysis)}

Return ONLY valid JSON with exactly the following keys and appropriate types:
- peak_lean_mass_kg (float)
- target_bf_pct (float)
- peak_ffmi (float)
- muscle_gain_required_kg (float)
- fat_loss_required_pct (float)
- muscle_gaps (dict with float values for: chest, back, legs, arms, shoulders)
- primary_strategy (string: "bulk", "cut", or "recomp")
- agent_reasoning (string describing your logic based on the user's data and consistency)

Ensure peak physiological parameters stay within realistic human bounds based on the user's structural frame.
Output ONLY JSON, no markdown formatting like ```json.
"""
    try:
        text = call_gemini(prompt)
        return parse_json(text)
    except Exception as e:
        print(f"Workout agent error: {e}")
        return {
            "peak_lean_mass_kg": body_analysis.get("peak_lean_mass_kg") or 72.5,
            "target_bf_pct": 12.0,
            "peak_ffmi": body_analysis.get("peak_ffmi") or 23.8,
            "muscle_gain_required_kg": body_analysis.get("lean_mass_gap_kg") or 6.0,
            "fat_loss_required_pct": 5.0,
            "muscle_gaps": {"chest": 2.0, "back": 2.0, "legs": 2.5, "arms": 1.2, "shoulders": 1.5},
            "primary_strategy": "recomp",
            "agent_reasoning": f"Fallback plan due to API error: {e}",
        }
