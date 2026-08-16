import os
import httpx
import base64
import time
import logging
from app.config import settings
from app.services import llm

logger = logging.getLogger("afip")

async def assess_crop_image(image_bytes: bytes) -> dict:
    """
    Send image to Colab-hosted fine-tuned Llama 3.1 model.
    Fallback: If Colab endpoint is down or not configured, fall back to Gemini Vision API.
    """
    if not settings.CROP_MODEL_URL:
        logger.warning("[Colab Model] CROP_MODEL_URL not set. Falling back to Gemini Vision.")
        return await llm.assess_crop_image_gemini(image_bytes)

    image_b64 = base64.b64encode(image_bytes).decode()
    
    try:
        start = time.time()
        # 30s timeout since Colab inference can be slow
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.CROP_MODEL_URL.rstrip('/')}/predict",
                json={"image": image_b64}
            )
            response.raise_for_status()
            duration_ms = (time.time() - start) * 1000
            logger.info(f"[Colab Model] predict — Success ({duration_ms:.0f}ms)")
            return response.json()
    except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
        logger.error(f"[Colab Model] failed: {e}. Falling back to Gemini Vision.")
        # FALLBACK: Use Gemini Vision API
        return await llm.assess_crop_image_gemini(image_bytes)
