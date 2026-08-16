import math
import logging
from typing import List, Dict, Any
from app.db import execute
from app.services.prediction import get_station_coords

logger = logging.getLogger(__name__)

def rank_safe_zones(safe_zones: List[Dict[str, Any]], river_stations: List[Dict[str, Any]], villages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks safe zones based on elevation, road access, distance to river stations, and capacity.
    Excludes safe zones that are near a village with a flood risk > 0.7.
    """
    if not safe_zones:
        return []
        
    ranked_zones = []
    
    # Calculate min/max for normalization
    elevations = [float(z.get('elevation_m', 0.0)) for z in safe_zones]
    capacities = [float(z.get('capacity_est', 0.0)) for z in safe_zones]
    
    min_elev = min(elevations) if elevations else 0.0
    max_elev = max(elevations) if elevations else 1.0
    if min_elev == max_elev: max_elev = min_elev + 1.0
        
    min_cap = min(capacities) if capacities else 0.0
    max_cap = max(capacities) if capacities else 1.0
    if min_cap == max_cap: max_cap = min_cap + 1.0

    # We need to find the max distance for normalization
    # Pre-calculate distances
    distances = []
    for z in safe_zones:
        z_lat = float(z.get('latitude', 0.0))
        z_lng = float(z.get('longitude', 0.0))
        
        min_dist = float('inf')
        for station in river_stations:
            s_lat, s_lng = get_station_coords(station.get('station_name', ''))
            dist = math.dist([z_lat, z_lng], [s_lat, s_lng])
            if dist < min_dist:
                min_dist = dist
        distances.append(min_dist if min_dist != float('inf') else 0.0)
        
    min_dist_val = min(distances) if distances else 0.0
    max_dist_val = max(distances) if distances else 1.0
    if min_dist_val == max_dist_val: max_dist_val = min_dist_val + 1.0

    for i, z in enumerate(safe_zones):
        # 1. Normalize elevation (higher is better)
        elev = float(z.get('elevation_m', 0.0))
        elev_norm = (elev - min_elev) / (max_elev - min_elev)
        
        # 2. Road access is pre-seeded 0-1
        road_norm = float(z.get('road_access_score', 0.0))
        
        # 3. Distance from river (further is better)
        dist = distances[i]
        dist_norm = (dist - min_dist_val) / (max_dist_val - min_dist_val)
        
        # 4. Capacity (higher is better)
        cap = float(z.get('capacity_est', 0.0))
        cap_norm = (cap - min_cap) / (max_cap - min_cap)
        
        # 5. Weighted score
        safe_score = (elev_norm * 0.4) + (road_norm * 0.25) + (dist_norm * 0.2) + (cap_norm * 0.15)
        
        # 6. Update database
        execute("UPDATE safe_zones SET safe_score = ? WHERE id = ?", (safe_score, z['id']))
        z['safe_score'] = round(safe_score, 3)
        z['component_scores'] = {
            "elevation": round(elev_norm, 3),
            "road_access": round(road_norm, 3),
            "distance": round(dist_norm, 3),
            "capacity": round(cap_norm, 3)
        }
        ranked_zones.append(z)
            
    # 7. Sort by safe_score descending
    ranked_zones.sort(key=lambda x: x['safe_score'], reverse=True)
    
    logger.info(f"Ranked {len(safe_zones)} safe zones.")
    return ranked_zones
