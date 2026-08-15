from fastapi import APIRouter

router = APIRouter()

@router.get("/api/safe-zones")
async def get_safe_zones():
    return {"status": "not_implemented"}
