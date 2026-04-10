import os, json, re
from typing import Dict, List

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """You are a professional dermatologist AI assistant.
Respond ONLY with a valid JSON object — no extra text:

{
  "recommendations": ["...", "...", "..."],
  "next_steps": ["...", "...", "..."],
  "tips": ["...", "...", "..."]
}

3-5 items each. Be concise and medically accurate.
Always recommend consulting a licensed dermatologist."""


def _fallback(disease: str) -> Dict[str, List[str]]:
    return {
        "recommendations": [
            f"AI detected {disease} — preliminary screening only.",
            "Do not self-medicate based on this result.",
            "Consult a licensed dermatologist for accurate diagnosis.",
        ],
        "next_steps": [
            "Book an appointment with a dermatologist.",
            "Avoid scratching or picking the affected area.",
            "Photograph the area to show your doctor.",
        ],
        "tips": [
            "Keep the area clean and moisturized.",
            "Avoid harsh soaps and skin irritants.",
            "Wear loose breathable clothing.",
            "Stay hydrated and maintain a balanced diet.",
        ],
    }


def get_llm_recommendations(disease: str, confidence: float) -> Dict[str, List[str]]:
    if not GEMINI_API_KEY:
        return _fallback(disease)
    try:
        from google import genai                              
        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Detected condition: {disease}\nConfidence: {confidence*100:.1f}%\nProvide recommendations.",
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        raw = resp.text.strip()
        match = re.search(r"```(?:json)?(.*?)```", raw, re.DOTALL)
        return json.loads(match.group(1).strip() if match else raw)
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return _fallback(disease)
