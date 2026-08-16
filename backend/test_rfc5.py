import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from app.models.query import QueryRequest, QueryResponse
from app.models.crop import CropAssessmentResult
from app.services.llm import parse_sos_text

async def run_tests():
    print("Running RFC-005 Tests...")

    # 1. Test Pydantic Schemas
    print("1. Testing Query Schemas...")
    q_req = QueryRequest(question="Where are the floods?")
    q_res = QueryResponse(answer="In Majuli")
    assert q_req.question == "Where are the floods?"
    assert q_res.answer == "In Majuli"
    print("   Schemas OK.")

    print("2. Testing Crop Schemas...")
    c_res = CropAssessmentResult(
        crop_type="Paddy", 
        damage_pct=50, 
        advisory_en="Drain water", 
        advisory_as="পানী উলিয়াই দিয়ক"
    )
    assert c_res.crop_type == "Paddy"
    print("   Schemas OK.")

    # 3. Test LLM parsing logic
    print("3. Testing SOS Parsing Logic...")
    # NOTE: Since this actually calls the Gemini API, we'll only run it if the key is present.
    if os.getenv("GEMINI_API_KEY"):
        sample_text = "Help, there are 5 of us stuck on the roof in Majuli, we need a boat and food."
        result = await parse_sos_text(sample_text)
        print(f"   Parsed Result: {result}")
        assert result.get("location") is not None
        assert result.get("people_count") in [5, "5"]
        assert result.get("needs") is not None
        print("   LLM Parsing OK.")
    else:
        print("   Skipping LLM tests: GEMINI_API_KEY not found.")

    print("All RFC-005 verification tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
