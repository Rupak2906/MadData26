import json
from app.agents.gemini_client import call_gemini, parse_json


def run_timeline_agent(user: dict, transformation_plan: dict, dietary_plan: dict) -> dict:
    """
    Call Gemini to generate a realistic physiological timeline.
    """
    prompt = f"""
You are an expert training periodization AI.
Analyze the user, their transformation plan, and dietary plan to project a realistic timeline.

User Data: {json.dumps(user)}
Workout Plan: {json.dumps(transformation_plan)}
Diet Plan: {json.dumps(dietary_plan)}

Return ONLY valid JSON with exactly the following keys and appropriate types:
- total_months_optimistic (int)
- total_months_realistic (int)
- total_months_conservative (int)
- confidence_level (string: "low", "medium", "high")
- consistency_score (float: user consistency 0.0 to 1.0)
- consistency_impact (string: explanation of how their consistency score affected the timeline)
- phase_1_goal (string)
- phase_1_months (int)
- phase_2_goal (string)
- phase_2_months (int)
- phase_3_goal (string)
- phase_3_months (int)
- milestone_1_month (int)
- milestone_1_description (string)
- milestone_2_month (int)
- milestone_2_description (string)
- milestone_3_month (int)
- milestone_3_description (string)

Ensure month sums and milestones align chronologically.
Output ONLY JSON, no markdown formatting like ```json.
"""
    try:
        text = call_gemini(prompt)
        return parse_json(text)
    except Exception as e:
        print(f"Timeline agent error: {e}")
        score = user.get("consistency_score")
        if score is None:
            score = 0.75

        return {
            "total_months_optimistic": 8,
            "total_months_realistic": 10,
            "total_months_conservative": 14,
            "confidence_level": "medium",
            "consistency_score": float(score),
            "consistency_impact": "Maintaining >80% consistency can reduce timeline by 2 months.",
            "phase_1_goal": "Movement quality and habit consistency",
            "phase_1_months": 3,
            "phase_2_goal": "Primary recomposition block",
            "phase_2_months": 5,
            "phase_3_goal": "Refinement and maintenance",
            "phase_3_months": 2,
            "milestone_1_month": 2,
            "milestone_1_description": "Better recovery and training adherence",
            "milestone_2_month": 6,
            "milestone_2_description": "Noticeable visual and strength improvements",
            "milestone_3_month": 10,
            "milestone_3_description": "Sustainable near-goal physique baseline",
        }
