from fastapi import APIRouter

router = APIRouter()

@router.post("/api/sms/webhook")
async def sms_webhook():
    return {"status": "not_implemented"}
