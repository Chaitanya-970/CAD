from fastapi import APIRouter

router = APIRouter()

@router.get("/api/flood-zones")
async def get_flood_zones():
    return {"status": "not_implemented"}

@router.post("/api/predict")
async def predict_flood():
    return {"status": "not_implemented"}
