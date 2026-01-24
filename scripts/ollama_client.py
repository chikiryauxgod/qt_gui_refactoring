import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "rnj-1:8b"

SYSTEM_PROMPT = """
Ты — software architect.
Оцени изменения кода на соответствие принципам SOLID.

Ответ строго в JSON следующего формата:
{
  "solid_score": 0-10,
  "reason": ""
}

Никакого текста вне JSON.
"""

def analyze_chunk(chunk: str) -> dict:
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": SYSTEM_PROMPT + "\n\n" + chunk,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 400
                }
            },
            timeout=60
        )
    except requests.Timeout:
        return {"error": "timeout"}

    text = r.json().get("response", "").strip()

    if not text:
        return {"error": "empty_response"}

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return {
            "error": "no_json_found",
            "raw": text[:500]
        }

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        return {
            "error": "invalid_json",
            "raw": text[start:end + 1][:500]
        }
