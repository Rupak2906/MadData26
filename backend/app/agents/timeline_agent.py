import os
import json
import re
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"



def _call_gemini(system: str, user: str) -> dict:
    """Call Gemini and parse the JSON response. Raises ValueError on bad output."""
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system,
    )
    response = model.generate_content(user)
    raw = response.text.strip()
    raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\n\nRaw response:\n{raw}")


TIMELINE_SYSTEM = """
You are a fitness coach specialising in realistic body transformation timelines.
Given a user profile, their transformation plan, and dietary plan, estimate achievable timelines
and phase milestones.
Respond ONLY with a valid JSON object — no explanation, no markdown, no preamble.
Use exactly these keys:
{
  "total_months_optimistic": <int>,
  "total_months_realistic": <int>,
  "total_months_conservative": <int>,
  "confidence_level": <"low" | "medium" | "high">,
  "consistency_score": <float, 0.0-1.0>,
  "consistency_impact": <string, e.g. "Increasing consistency to 80% could save 3 months">,
  "phase_1_goal": <string>,
  "phase_1_months": <int>,
  "phase_2_goal": <string or null>,
  "phase_2_months": <int or null>,
  "phase_3_goal": <string or null>,
  "phase_3_months": <int or null>,
  "milestone_1_month": <int>,
  "milestone_1_description": <string>,
  "milestone_2_month": <int>,
  "milestone_2_description": <string>,
  "milestone_3_month": <int>,
  "milestone_3_description": <string>
}
"""


def run_timeline_agent(user: dict, transformation_plan: dict, dietary_plan: dict) -> dict:
    """
    Returns dict ready to be saved as Timeline.
    """
    prompt = f"""
USER PROFILE:
{json.dumps(user, indent=2)}

TRANSFORMATION PLAN:
{json.dumps(transformation_plan, indent=2)}

DIETARY PLAN:
{json.dumps(dietary_plan, indent=2)}

Estimate realistic transformation timelines and milestones. Factor in the user's
consistency score ({user.get('consistency_score', 0.7)}), experience level, and
the size of their transformation gap.
"""
    return _call_gemini(TIMELINE_SYSTEM, prompt)