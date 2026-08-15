from fastapi import APIRouter

router = APIRouter()

@router.get("/api/villages")
async def get_villages():
    return {"status": "not_implemented"}
