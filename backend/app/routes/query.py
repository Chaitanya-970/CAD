from fastapi import APIRouter
from app.models.query import QueryRequest, QueryResponse
from app.services import llm
from app.db import fetch_all

router = APIRouter()

@router.post("/api/query", response_model=QueryResponse)
async def query_ai(request: QueryRequest):
    # Build context from live DB data
    # Fetch only necessary columns to keep token count under Groq's 6000 TPM limit
    villages = fetch_all("SELECT id, name, district, current_risk_score FROM villages")
    sos = fetch_all("SELECT id, parsed_location, parsed_needs, parsed_people_count FROM sos_messages WHERE status = 'active'")
    safe_zones = fetch_all("SELECT id, name, capacity_est, safe_score, nearest_village_id FROM safe_zones")
    
    context = {
        "villages": villages,
        "sos_messages": sos,
        "safe_zones": safe_zones
    }
    
    answer = await llm.answer_query(request.question, context)
    return QueryResponse(answer=answer)
