import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import crop_model
from app.db import execute
from app.models.crop import CropAssessmentResult

router = APIRouter()

@router.post("/api/crop-assess", response_model=CropAssessmentResult)
async def assess_crop(image: UploadFile = File(...)):
    contents = await image.read()
    
    # Validate image size (<5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds 5MB limit")
    
    # Save image to uploads/ folder
    file_ext = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = f"uploads/{filename}"
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Call fine-tuned model (with Gemini fallback inside the service)
    result_dict = await crop_model.assess_crop_image(contents)
    
    # Validate result against schema
    result = CropAssessmentResult(**result_dict)
    
    # Store in DB (F19 - Crop Assessment History)
    execute("""
        INSERT INTO crop_assessments (image_path, crop_type, damage_pct, advisory_en, advisory_as)
        VALUES (?, ?, ?, ?, ?)
    """, (filepath, result.crop_type, result.damage_pct, result.advisory_en, result.advisory_as))
    
    return result
