from fastapi import APIRouter

router = APIRouter()

@router.post("/api/alert/sms")
async def alert_sms():
    return {"status": "not_implemented"}

@router.post("/api/alert/ivr")
async def alert_ivr():
    return {"status": "not_implemented"}
