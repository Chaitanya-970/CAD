from pydantic import BaseModel

class CropAssessmentResult(BaseModel):
    crop_type: str
    damage_pct: int
    advisory_en: str
    advisory_as: str
