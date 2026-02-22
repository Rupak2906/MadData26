"""
ai_agent.py
-----------
Orchestrates the three Claude agents in sequence:
  workout → diet → timeline

Call run_full_agent_pipeline() with a user dict and body analysis dict.
Returns a dict with keys: transformation_plan, dietary_plan, timeline.
"""

from app.agents.workout_agent import run_workout_agent
from app.agents.diet_agent import run_diet_agent
from app.agents.timeline_agent import run_timeline_agent


def run_full_agent_pipeline(user: dict, body_analysis: dict) -> dict:
    """
    Run all three Claude agents in dependency order.

    Order matters:
      1. Workout agent — establishes peak potential and primary strategy
      2. Diet agent    — uses the strategy to set caloric targets
      3. Timeline agent — uses both to estimate phases and milestones

    Args:
        user: dict of User model fields
        body_analysis: dict of BodyAnalysis model fields + ML predictions

    Returns:
        {
            "transformation_plan": {...},
            "dietary_plan": {...},
            "timeline": {...},
        }

    Raises:
        ValueError if any agent returns invalid JSON.
    """
    transformation_plan = run_workout_agent(user, body_analysis)
    dietary_plan        = run_diet_agent(user, body_analysis)
    timeline            = run_timeline_agent(user, transformation_plan, dietary_plan)

    return {
        "transformation_plan": transformation_plan,
        "dietary_plan": dietary_plan,
        "timeline": timeline,
    }