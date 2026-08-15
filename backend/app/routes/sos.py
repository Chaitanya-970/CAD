from fastapi import APIRouter

router = APIRouter()

@router.get("/api/sos")
async def get_sos():
    return {"status": "not_implemented"}
