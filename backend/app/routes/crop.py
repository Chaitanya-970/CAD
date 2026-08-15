from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/api/crop-assess")
async def assess_crop(image: UploadFile = File(...)):
    return {"status": "not_implemented"}
