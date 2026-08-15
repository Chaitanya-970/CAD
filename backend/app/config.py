import os
import sys
from dotenv import load_dotenv

load_dotenv()

def get_env_or_exit(key: str) -> str:
    val = os.getenv(key)
    if not val:
        print(f"CRITICAL: Missing required environment variable: {key}")
        sys.exit(1)
    return val

class Settings:
    TWILIO_ACCOUNT_SID = get_env_or_exit("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = get_env_or_exit("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = get_env_or_exit("TWILIO_PHONE_NUMBER")
    
    GEMINI_API_KEY = get_env_or_exit("GEMINI_API_KEY")
    GROQ_API_KEY = get_env_or_exit("GROQ_API_KEY")
    
    BHASHINI_API_KEY = get_env_or_exit("BHASHINI_API_KEY")
    BHASHINI_INFERENCE_KEY = get_env_or_exit("BHASHINI_INFERENCE_KEY")
    
    # CROP_MODEL_URL is optional (fallback is Gemini Vision per PRD)
    CROP_MODEL_URL = os.getenv("CROP_MODEL_URL", "")

settings = Settings()
