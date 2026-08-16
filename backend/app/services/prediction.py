import math
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any
from app.db import execute
from app.models.flood import AnomalyAlert

logger = logging.getLogger(__name__)

def predict_flood_zones(river_levels: List[Dict[str, Any]], villages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Predicts flood risk for each village based on current river levels and elevation.
    Updates the database with the new current_risk_score.
    """
    updated_villages = []
    
    # If no river levels exist, risk is effectively 0 for all, but let's safely handle that.
    if not river_levels:
        return villages

    for village in villages:
        v_lat = village.get('latitude', 0.0)
        v_lng = village.get('longitude', 0.0)
        
        # 1. Find the nearest river station
        nearest_station = None
        min_dist = float('inf')
        
        for station in river_levels:
            # river_levels table has no coordinates; map station names to known positions for distance calc
            s_lat, s_lng = get_station_coords(station.get('station_name', ''))
            
            dist = math.dist([v_lat, v_lng], [s_lat, s_lng])
            if dist < min_dist:
                min_dist = dist
                nearest_station = station
                
        if not nearest_station:
            continue

        # 2. projected_level = station.current_level_m + station.forecast_rise_m
        current_level = float(nearest_station.get('current_level_m', 0.0))
        forecast_rise = float(nearest_station.get('forecast_rise_m', 0.0))
        projected_level = current_level + forecast_rise
        
        # 3. flood_depth = projected_level - village.elevation_m
        elevation = float(village.get('elevation_m', 0.0))
        flood_depth = projected_level - elevation
        
        # 4. Calculate risk score
        if flood_depth > 0:
            risk_score = min(flood_depth / 5.0, 1.0)
        elif flood_depth > -2:
            risk_score = 0.3
        else:
            risk_score = 0.0
            
        village['current_risk_score'] = risk_score
        updated_villages.append(village)

    # 5. Batch update all village.current_risk_score in the database
    update_data = [(v['current_risk_score'], v['id']) for v in updated_villages]
    if update_data:
        from app.db import execute_many
        execute_many("UPDATE villages SET current_risk_score = ? WHERE id = ?", update_data)
        
    logger.info(f"Processed flood risk for {len(villages)} villages against {len(river_levels)} stations.")
    return updated_villages

def get_station_coords(station_name: str):
    """Fallback coordinates for river stations since they aren't in the DB schema."""
    name = station_name.lower()
    if 'majuli' in name:
        return (26.95, 94.16)
    elif 'dhubri' in name:
        return (26.02, 89.97)
    elif 'silchar' in name:
        return (24.83, 92.77)
    return (26.0, 92.0) # generic center of Assam

def check_anomalies(river_levels: List[Dict[str, Any]], historical_csv_path: str) -> List[AnomalyAlert]:
    """
    Checks river levels against historical averages to flag anomalies.
    """
    anomalies = []
    current_month = str(datetime.now().month)
    
    historical_data = {}
    try:
        with open(historical_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('month') == current_month:
                    station = row.get('station_name', '').lower()
                    historical_data[station] = {
                        'avg': float(row.get('avg_level_m', 0.0)),
                        'std': float(row.get('std_dev_m', 0.5))
                    }
    except FileNotFoundError:
        logger.warning(f"Historical CSV not found at {historical_csv_path}")

    for station in river_levels:
        name = station.get('station_name', '')
        current_level = float(station.get('current_level_m', 0.0))
        
        # Match station
        hist = historical_data.get(name.lower())
        
        # If no match found, use a fallback
        if not hist:
            hist_avg = float(station.get('danger_level_m', 100.0)) - 2.0
            std_dev = 2.5
        else:
            hist_avg = hist['avg']
            std_dev = hist['std']
            
        z_score = (current_level - hist_avg) / std_dev
        
        if abs(z_score) > 2.0:
            anomalies.append(AnomalyAlert(
                station_name=name,
                z_score=round(z_score, 2),
                message=f"Unusual water level detected at {name}. Z-Score: {round(z_score, 2)}"
            ))
            
    logger.info(f"Anomaly check completed: found {len(anomalies)} anomalies.")
    return anomalies
