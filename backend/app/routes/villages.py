from fastapi import APIRouter
from app.db import fetch_all

router = APIRouter()

@router.get("/api/villages")
async def get_villages():
    """Simple read-only endpoint returning village metadata for frontend use."""
    villages = fetch_all("SELECT id, name_english, name_assamese, district, latitude, longitude, elevation_m, population FROM villages")
    return {"villages": villages}
