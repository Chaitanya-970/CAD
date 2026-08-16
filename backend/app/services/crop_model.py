import os
import httpx
import base64
import time
import logging
import tempfile
import re
from app.config import settings
from app.services import llm

logger = logging.getLogger("afip")

async def assess_crop_image(image_bytes: bytes) -> dict:
    """
    Send image to Colab-hosted fine-tuned Qwen2-VL model via Gradio.
    Fallback: If Colab endpoint is down or not configured, fall back to Gemini Vision API.
    """
    if not settings.CROP_MODEL_URL:
        logger.warning("[Qwen2-VL] CROP_MODEL_URL not set. Falling back to Gemini Vision.")
        return await llm.assess_crop_image_gemini(image_bytes)

    # Check if the URL is a Gradio link
    if "gradio" in settings.CROP_MODEL_URL:
        try:
            # gradio_client is synchronous but it runs fast enough for demo
            from gradio_client import Client, handle_file
            
            start = time.time()
            client = Client(settings.CROP_MODEL_URL)
            
            # Write bytes to temp file since Gradio expects a file path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
                
            result = client.predict(
                image=handle_file(tmp_path),
                lat=26.2,  # Hardcoded default center for Assam
                lon=92.9,
                api_name="/predict"
            )
            
            os.remove(tmp_path)
            
            duration_ms = (time.time() - start) * 1000
            logger.info(f"[Qwen2-VL Gradio] predict — Success ({duration_ms:.0f}ms)")
            
            # Parse the Markdown output
            # Format: **Diagnosis:** Rice blast \n\n **Treatment:** ... \n\n **Cost:** ... \n\n Rain likely...
            crop_type = "Unknown Disease"
            diagnosis_match = re.search(r"\*\*Diagnosis:\*\*\s*(.*?)(?=\\n|$)", result)
            if diagnosis_match:
                crop_type = diagnosis_match.group(1).strip()
            
            return {
                "crop_type": crop_type,
                "damage_pct": 75, # Harcoded because Gradio model doesn't return damage pct
                "advisory_en": result,
                "advisory_as": "Assamese translation pending." # The frontend won't render this if language='en'
            }
            
        except Exception as e:
            logger.error(f"[Qwen2-VL Gradio] failed: {e}. Falling back to Gemini Vision.")
            return await llm.assess_crop_image_gemini(image_bytes)
    
    # Original httpx logic for legacy API
    image_b64 = base64.b64encode(image_bytes).decode()
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.CROP_MODEL_URL.rstrip('/')}/predict",
                json={"image": image_b64}
            )
            response.raise_for_status()
            duration_ms = (time.time() - start) * 1000
            logger.info(f"[Legacy API] predict — Success ({duration_ms:.0f}ms)")
            return response.json()
    except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
        logger.error(f"[Legacy API] failed: {e}. Falling back to Gemini Vision.")
        return await llm.assess_crop_image_gemini(image_bytes)
