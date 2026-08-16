from fastapi import APIRouter
from app.models.query import QueryRequest, QueryResponse
from app.services import llm
from app.db import fetch_all

router = APIRouter()

@router.post("/api/query", response_model=QueryResponse)
async def query_ai(request: QueryRequest):
    # Build context from live DB data
    villages = fetch_all("SELECT * FROM villages")
    sos = fetch_all("SELECT * FROM sos_messages WHERE status = 'active'")
    safe_zones = fetch_all("SELECT * FROM safe_zones")
    
    context = {
        "villages": villages,
        "sos_messages": sos,
        "safe_zones": safe_zones
    }
    
    answer = await llm.answer_query(request.question, context)
    return QueryResponse(answer=answer)
