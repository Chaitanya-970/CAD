from pydantic import BaseModel
from typing import List, Optional

class RiverLevelInput(BaseModel):
    station_name: str
    current_level_m: float
    forecast_rise_m: float = 0.0

class PredictRequest(BaseModel):
    river_levels: Optional[List[RiverLevelInput]] = None

class AnomalyAlert(BaseModel):
    station_name: str
    z_score: float
    message: str

class PredictResponse(BaseModel):
    updated: int
    anomalies: List[AnomalyAlert]
