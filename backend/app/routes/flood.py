import os
from fastapi import APIRouter
from app.db import fetch_all
from app.models.flood import PredictRequest, PredictResponse
from app.services.prediction import predict_flood_zones, check_anomalies

router = APIRouter()

def get_risk_level(score: float) -> str:
    if score >= 0.7:
        return "high"
    elif score >= 0.3:
        return "moderate"
    return "safe"

@router.get("/api/flood-zones")
async def get_flood_zones():
    villages = fetch_all("SELECT * FROM villages")
    
    features = []
    for v in villages:
        risk_score = v.get('current_risk_score', 0.0)
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [v['longitude'], v['latitude']]
            },
            "properties": {
                "id": v['id'],
                "name": v['name'],
                "name_assamese": v.get('name_assamese', ''),
                "district": v['district'],
                "elevation_m": v['elevation_m'],
                "population_est": v['population_est'],
                "risk_score": risk_score,
                "risk_level": get_risk_level(risk_score)
            }
        }
        features.append(feature)
        
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.post("/api/predict", response_model=PredictResponse)
async def predict_flood(request: PredictRequest = None):
    # 1. Get and update river levels
    river_levels = []
    if request and request.river_levels:
        river_levels = [rl.model_dump() for rl in request.river_levels]
        # Update DB with simulation values (F20)
        from app.db import execute_many
        update_data = [(rl['current_level_m'], rl['forecast_rise_m'], rl['station_name']) for rl in river_levels]
        execute_many("UPDATE river_levels SET current_level_m = ?, forecast_rise_m = ? WHERE station_name = ?", update_data)
    else:
        # Use DB data if no payload provided
        river_levels = fetch_all("SELECT * FROM river_levels")
        
    # 2. Get villages
    villages = fetch_all("SELECT * FROM villages")
    
    # 3. Predict flood zones and update DB
    updated_villages = predict_flood_zones(river_levels, villages)
    
    # 4. Check anomalies
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "historical.csv")
    anomalies = check_anomalies(river_levels, csv_path)
    
    return PredictResponse(
        updated=len(updated_villages),
        anomalies=anomalies
    )
