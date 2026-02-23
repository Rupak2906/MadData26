"""Test the Gemini API using urllib (no pip packages needed)."""
import json
import urllib.request

API_KEY = "AIzaSyCcFWQO7BfOKw-GEkjvkqKaSYkJWc715tI"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

payload = json.dumps({"contents": [{"parts": [{"text": "Say HELLO_OK in one word"}]}]}).encode("utf-8")

req = urllib.request.Request(URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        print(f"SUCCESS: {text.strip()}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode("utf-8") if e.fp else "no body"
    print(f"HTTP ERROR {e.code}: {error_body}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
