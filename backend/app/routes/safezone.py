from fastapi import APIRouter
from app.db import fetch_all
from app.services.safezone import rank_safe_zones

router = APIRouter()

@router.get("/api/safe-zones")
async def get_safe_zones():
    # 1. Fetch data
    safe_zones = fetch_all("SELECT * FROM safe_zones")
    river_stations = fetch_all("SELECT * FROM river_levels")
    villages = fetch_all("SELECT * FROM villages")
    
    # 2. Rank and filter
    ranked_zones = rank_safe_zones(safe_zones, river_stations, villages)
    
    # 3. Format as GeoJSON FeatureCollection
    features = []
    for sz in ranked_zones:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [sz['longitude'], sz['latitude']]
            },
            "properties": {
                "id": sz['id'],
                "name": sz['name'],
                "elevation_m": sz['elevation_m'],
                "road_access_score": sz.get('road_access_score', 0.0),
                "capacity_est": sz['capacity_est'],
                "safe_score": sz.get('safe_score', 0.0),
                "scores": sz.get('component_scores', {})
            }
        }
        features.append(feature)
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
