"""
Shared Gemini REST API helper used by all agents.
Uses only Python built-ins (urllib) so no extra pip packages are needed.
"""
import json
import urllib.request
import urllib.error
from app.core.config import settings

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
)


def call_gemini(prompt: str) -> str:
    """
    Call the Gemini REST API and return the raw text response.
    Uses urllib so it works even if `requests` or `google-generativeai` aren't installed.
    """
    url = f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return body["candidates"][0]["content"]["parts"][0]["text"]


def parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON from LLM output."""
    text = text.strip()
    # Handle ```json ... ``` blocks
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())
