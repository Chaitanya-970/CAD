from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from app.db import fetch_all, execute

router = APIRouter()

class UpdateSOSRequest(BaseModel):
    status: str

@router.get("/api/sos")
async def get_sos(status: str = None):
    if status:
        return fetch_all("SELECT * FROM sos_messages WHERE status = ?", (status,))
    return fetch_all("SELECT * FROM sos_messages")

@router.patch("/api/sos/{sos_id}")
async def update_sos_status(sos_id: int, request: UpdateSOSRequest):
    if request.status not in ('active', 'acknowledged', 'resolved'):
        raise HTTPException(status_code=400, detail="Invalid status")
    execute("UPDATE sos_messages SET status = ? WHERE id = ?", (request.status, sos_id))
    return {"status": "success"}
