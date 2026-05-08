import os
import json
import base64
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"  # Free, fast, very smart


# ─────────────────────────────────────────────
# FALLBACKS
# ─────────────────────────────────────────────

def _fallback_text_result() -> dict:
    return {
        "credibility_score": 50,
        "verdict": "UNVERIFIABLE",
        "summary": "Could not analyze right now. Please try again in a moment.",
        "red_flags": ["Analysis incomplete — please retry"],
        "positive_signals": [],
        "fact_check_sources": [
            {"name": "AltNews", "url": "https://www.altnews.in", "relevance": "Indian fact-checker"},
            {"name": "Snopes", "url": "https://www.snopes.com", "relevance": "International fact-checker"},
            {"name": "Boom", "url": "https://www.boomlive.in", "relevance": "India fact-checking"}
        ],
        "recommendation": "Verify manually before sharing."
    }


def _fallback_image_result() -> dict:
    return {
        "credibility_score": 50,
        "verdict": "UNVERIFIABLE",
        "image_description": "Image received but analysis incomplete.",
        "red_flags": ["Analysis incomplete — please retry"],
        "positive_signals": [],
        "manipulation_indicators": [],
        "fact_check_sources": [
            {"name": "Google Reverse Image", "url": "https://images.google.com", "relevance": "Find original source"},
            {"name": "TinEye", "url": "https://tineye.com", "relevance": "Reverse image search"}
        ],
        "recommendation": "Use reverse image search to verify origin."
    }


# ─────────────────────────────────────────────
# TEXT FACT-CHECKER
# ─────────────────────────────────────────────

def fact_check_text(text: str) -> dict:
    prompt = f"""You are FakeRadar, an expert AI fact-checker and misinformation detector.

Analyze the following news article or text for credibility and misinformation:

---
{text}
---

Respond ONLY in this exact JSON format (no markdown, no backticks, no extra text):
{{
  "credibility_score": <number 0-100>,
  "verdict": "<one of: LIKELY TRUE | MOSTLY TRUE | MIXED | MOSTLY FALSE | LIKELY FALSE | UNVERIFIABLE>",
  "summary": "<2-3 sentence plain-English summary of what this content claims>",
  "red_flags": [
    "<specific red flag 1>",
    "<specific red flag 2>"
  ],
  "positive_signals": [
    "<credibility signal 1>"
  ],
  "fact_check_sources": [
    {{
      "name": "<fact-check site name>",
      "url": "<real URL>",
      "relevance": "<why relevant>"
    }}
  ],
  "recommendation": "<one clear action: share / don't share / verify first>"
}}

Rules:
- credibility_score: 0 = pure disinformation, 100 = fully verified truth
- Be very specific in red flags
- Include Indian fact-checkers like AltNews, Boom, FactChecker.in when relevant
- If content is in Hindi or regional language, still analyze in English
- If only a URL or domain is given, analyze the reputation of that news source
- Return ONLY the JSON object, absolutely nothing else"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are FakeRadar, an expert fact-checker. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1500,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw.strip())

    except json.JSONDecodeError:
        return _fallback_text_result()
    except Exception as e:
        print(f"Groq text error: {e}")
        return _fallback_text_result()


def fact_check_article_url(scraped: dict) -> dict:
    """Fact-check a scraped article or analyze domain reputation."""
    if scraped.get("success") and len(scraped.get("content", "")) > 100:
        combined = f"""
Source Domain: {scraped.get('domain', 'Unknown')}
Article Title: {scraped.get('title', 'Unknown')}
Article Content:
{scraped.get('content', '')}
"""
        return fact_check_text(combined)
    else:
        domain_text = f"""
The user submitted this news website URL: {scraped.get('url', '')}
Domain: {scraped.get('domain', 'Unknown')}
Please analyze the credibility and reputation of this news source/domain.
"""
        return fact_check_text(domain_text)


# ─────────────────────────────────────────────
# IMAGE FACT-CHECKER (uses llava vision model)
# ─────────────────────────────────────────────

def fact_check_image(image_base64: str, mime_type: str = "image/jpeg") -> dict:
    prompt = """You are FakeRadar, an expert AI fact-checker specializing in image-based misinformation.

Analyze this image for signs of manipulation, fake news, or misinformation.

Look for:
- Visual manipulation or deepfake signs
- Misleading text overlays or captions
- Out-of-context imagery
- Propaganda patterns
- Inconsistent lighting, shadows, or artifacts
- Any text visible in the image that could be misleading

Respond ONLY in this exact JSON format (no markdown, no backticks):
{
  "credibility_score": <number 0-100>,
  "verdict": "<one of: LIKELY AUTHENTIC | PROBABLY AUTHENTIC | MIXED | LIKELY MANIPULATED | LIKELY FAKE | UNVERIFIABLE>",
  "image_description": "<what this image shows>",
  "red_flags": ["<red flag 1>", "<red flag 2>"],
  "positive_signals": ["<signal 1>"],
  "manipulation_indicators": ["<indicator 1>"],
  "fact_check_sources": [
    {
      "name": "<source>",
      "url": "<url>",
      "relevance": "<why>"
    }
  ],
  "recommendation": "<clear action>"
}

Return ONLY the JSON object, nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",  # Free vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=1500,
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw.strip())

    except json.JSONDecodeError:
        return _fallback_image_result()
    except Exception as e:
        print(f"Groq image error: {e}")
        return _fallback_image_result()