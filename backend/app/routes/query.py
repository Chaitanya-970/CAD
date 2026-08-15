from fastapi import APIRouter

router = APIRouter()

@router.post("/api/query")
async def query_ai():
    return {"status": "not_implemented"}
