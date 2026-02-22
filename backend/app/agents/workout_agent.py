# Creates workout routines tailored to predicted body outcomes.

import os
import json
import re
import anthropic

WORKOUT_SYSTEM = """
You are an elite strength and conditioning coach and body transformation specialist.
Given a user profile and their body analysis, produce a personalised transformation plan
that identifies their peak potential and the gaps they need to close.
Respond ONLY with a valid JSON object — no explanation, no markdown, no preamble.
Use exactly these keys:
{
  "peak_lean_mass_kg": <float, estimated natural peak lean mass>,
  "target_bf_pct": <float, ideal target body fat %>,
  "peak_ffmi": <float, projected peak FFMI>,
  "muscle_gain_required_kg": <float>,
  "fat_loss_required_pct": <float>,
  "muscle_gaps": {
    "chest": <float, kg to gain>,
    "back": <float>,
    "legs": <float>,
    "arms": <float>,
    "shoulders": <float>
  },
  "primary_strategy": <"bulk" | "cut" | "recomp">,
  "agent_reasoning": <string, 2-3 sentence explanation>
}
"""

def run_workout_agent(user: dict, body_analysis: dict) -> dict:
    """
    Returns dict ready to be saved as TransformationPlan.
    """
    prompt = f"""
USER PROFILE:
{json.dumps(user, indent=2)}

BODY ANALYSIS:
{json.dumps(body_analysis, indent=2)}

Estimate this user's peak natural physique potential and identify the transformation gaps.
Consider their frame type, current FFMI, experience level, and primary goal.
"""
    return _call_claude(WORKOUT_SYSTEM, prompt)