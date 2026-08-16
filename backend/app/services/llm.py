import json
import time
import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger("afip")

# Initialize Gemini Client
genai.configure(api_key=settings.GEMINI_API_KEY)
# We use gemini-flash-latest as the fast, cheap default for most tasks.
model = genai.GenerativeModel('gemini-flash-latest')
vision_model = genai.GenerativeModel('gemini-flash-latest') # flash also handles vision

# -----------------------------------------------------------------------------
# Prompt Constants (To be tuned by ML Teammate)
# -----------------------------------------------------------------------------

SOS_PARSE_PROMPT = """
You are an emergency response parser for the Assam Floods.
Extract the following information from the SOS message:
- location: The name of the village or area mentioned. Null if not found.
- people_count: The number of people stranded. Null if not found.
- needs: A short summary of what they need (e.g. "food, boat, medical"). Null if not found.

Return strictly valid JSON matching this schema:
{"location": "string|null", "people_count": "integer|null", "needs": "string|null"}
"""

ALERT_GEN_PROMPT = """
You are an emergency alert system for the Assam Floods.
Based on the provided data, generate a short, urgent, but calm SMS alert in English.
The message must include the village name, the risk level, and the nearest safe zone.
Keep it under 160 characters if possible.
"""

QUERY_SYSTEM_PROMPT = """
You are 'Gov-GPT', an AI assistant for Assam government officials managing floods.
Answer the user's question based strictly on the provided context (database dump of villages, safe zones, and active SOS messages).
If the context does not contain the answer, say "I cannot answer this based on current data."
Cite specific village names and numbers from the context.
"""

TRANSLATE_PROMPT = """
You are a professional translator fluent in English and Assamese.
Translate the following English text into clear, natural Assamese.
Return ONLY the Assamese text. Do not add any introductory or concluding remarks.
"""

# -----------------------------------------------------------------------------
# LLM Service Functions
# -----------------------------------------------------------------------------

async def answer_query(question: str, context: dict) -> str:
    """Answers a natural language query based on the live database context."""
    full_prompt = f"{QUERY_SYSTEM_PROMPT}\n\nContext:\n{json.dumps(context, default=str)}\n\nQuestion:\n{question}"
    try:
        start = time.time()
        response = model.generate_content(full_prompt)
        duration_ms = (time.time() - start) * 1000
        logger.info(f"[Gemini] answer_query — Success ({duration_ms:.0f}ms)")
        return response.text.strip()
    except Exception as e:
        logger.error(f"[Gemini] answer_query failed — {e}")
        return "I couldn't process that query. Try rephrasing, or view the map directly."

async def parse_sos_text(raw_text: str) -> dict:
    """Parses raw text into structured SOS data (location, people_count, needs)."""
    full_prompt = f"{SOS_PARSE_PROMPT}\n\nMessage: {raw_text}"
    try:
        start = time.time()
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            ),
        )
        duration_ms = (time.time() - start) * 1000
        logger.info(f"[Gemini] parse_sos_text — Success ({duration_ms:.0f}ms)")
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"[Gemini] parse_sos_text failed — {e}")
        return {"location": None, "people_count": None, "needs": None}

async def generate_alert_message(village_data: dict) -> str:
    """Generates an urgent but calm SMS alert based on prediction data."""
    full_prompt = f"{ALERT_GEN_PROMPT}\n\nData: {json.dumps(village_data, default=str)}"
    try:
        start = time.time()
        response = model.generate_content(full_prompt)
        duration_ms = (time.time() - start) * 1000
        logger.info(f"[Gemini] generate_alert_message — Success ({duration_ms:.0f}ms)")
        return response.text.strip()
    except Exception as e:
        logger.error(f"[Gemini] generate_alert_message failed — {e}")
        # Fallback to standard template if LLM fails
        return f"ALERT: High flood risk for {village_data.get('name', 'your village')}. Evacuate immediately."

async def translate_to_assamese(text: str) -> str:
    """Translates English text to Assamese."""
    full_prompt = f"{TRANSLATE_PROMPT}\n\nText: {text}"
    try:
        start = time.time()
        response = model.generate_content(full_prompt)
        duration_ms = (time.time() - start) * 1000
        logger.info(f"[Gemini] translate_to_assamese — Success ({duration_ms:.0f}ms)")
        return response.text.strip()
    except Exception as e:
        logger.error(f"[Gemini] translate_to_assamese failed — {e}")
        # Return original English if translation fails
        return text

async def assess_crop_image_gemini(image_bytes: bytes) -> dict:
    """
    Fallback method to assess crop damage using Gemini Vision.
    Used when the fine-tuned Colab endpoint is down.
    """
    prompt = """
    You are an agricultural expert in Assam, India.
    Analyze this flood-damaged crop image and return ONLY valid JSON:
    {"crop_type": "string", "damage_pct": int, "advisory_en": "string", "advisory_as": "string"}
    Make sure advisory_as is the Assamese translation of advisory_en.
    """
    try:
        # Wrap the image bytes in the format expected by the SDK
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }
        start = time.time()
        response = vision_model.generate_content(
            [prompt, image_part],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            ),
        )
        duration_ms = (time.time() - start) * 1000
        logger.info(f"[Gemini] assess_crop_image_gemini — Success ({duration_ms:.0f}ms)")
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"[Gemini] assess_crop_image_gemini failed — {e}")
        # Return safe default indicating failure to assess
        return {
            "crop_type": "Unknown", 
            "damage_pct": 0, 
            "advisory_en": "Unable to analyze image. Please try again later.", 
            "advisory_as": "চিত্ৰ বিশ্লেষণ কৰিব পৰা নগ'ল। অনুগ্ৰহ কৰি পিছত পুনৰ চেষ্টা কৰক।"
        }
