# RFC-002: Flood Prediction & Safe Zone Engine

> **Features:** F2 (48-Hour Flood Forecasting), F3 (Dynamic Safe-Zone Recommendation), F10 (Anomaly Detection)
> **Predecessors:** RFC-001
> **Successors:** RFC-003
> **Complexity:** Medium
> **Primary Track:** Backend + ML/AI
> **Applicable Rules:** R7, R8, R10, R11, R12, R14, R25, R26

---

## Summary

This RFC implements the core prediction logic — the rule-based flood forecasting engine that determines which villages will flood, the weighted scoring algorithm that ranks safe zones, and the statistical anomaly detector that flags unusual river-level readings. All three are backend services consumed via REST API.

---

## Technical Specification

### 1. Service: `backend/app/services/prediction.py`

The flood prediction engine. Takes river-level data and village elevation data, outputs updated risk scores.

**Algorithm:**
```python
def predict_flood_zones(river_levels: list, villages: list) -> list:
    """
    For each village:
      1. Find the nearest river station
      2. projected_level = station.current_level_m + station.forecast_rise_m
      3. flood_depth = projected_level - village.elevation_m
      4. if flood_depth > 0: risk_score = min(flood_depth / 5.0, 1.0)  # normalized 0-1
         elif flood_depth > -2: risk_score = 0.3  # yellow zone (close to danger)
         else: risk_score = 0.0  # safe (green)
      5. Update village.current_risk_score in the database
    Return list of villages with updated risk scores
    """
```

**"Nearest river station" logic:** Use Euclidean distance between village lat/lng and station lat/lng. This is approximate but sufficient for a hackathon demo with 3–5 stations.

### 2. Service: `backend/app/services/safezone.py`

The safe-zone ranking algorithm.

**Algorithm (per FEATURES.md F3):**
```python
def rank_safe_zones(safe_zones: list, flood_data: list) -> list:
    """
    For each safe zone:
      1. Normalize elevation to 0-1 scale (relative to min/max in dataset)
      2. road_access_score is pre-seeded (0-1)
      3. distance_from_river: compute distance to nearest river station, normalize 0-1
      4. capacity_score: normalize capacity_est to 0-1
      5. safe_score = (elevation_norm * 0.4) +
                      (road_access_score * 0.25) +
                      (distance_norm * 0.2) +
                      (capacity_norm * 0.15)
      6. Exclude any safe zone that is itself in a flood zone (risk_score > 0.7)
      7. Update safe_zones.safe_score in the database
    Return ranked list, highest score first
    """
```

### 3. Service: Anomaly Detection (added to `prediction.py`)

**Algorithm (F10):**
```python
def check_anomalies(river_levels: list, historical_csv_path: str) -> list:
    """
    For each river station:
      1. Load historical average and std_dev for current month from CSV
      2. z_score = (current_level - historical_avg) / historical_std_dev
      3. if abs(z_score) > 2.0: flag as anomaly
    Return list of anomaly alerts with station name, z_score, and message
    """
```

### 4. Route: `backend/app/routes/flood.py`

Replace the RFC-001 stubs with:

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| `GET` | `/api/flood-zones` | — | GeoJSON FeatureCollection with risk scores |
| `POST` | `/api/predict` | `{ "river_levels": [...] }` (optional — if omitted, use DB data) | `{ "updated": 50, "anomalies": [...] }` |

**`GET /api/flood-zones` response format:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [lng, lat] },
      "properties": {
        "id": 1,
        "name": "Majuli",
        "name_assamese": "মাজুলী",
        "district": "Majuli",
        "elevation_m": 48.5,
        "population_est": 1200,
        "risk_score": 0.85,
        "risk_level": "high"
      }
    }
  ]
}
```

`risk_level` is derived from `risk_score`: ≥0.7 → "high" (red), ≥0.3 → "moderate" (yellow), <0.3 → "safe" (green).

### 5. Route: `backend/app/routes/safezone.py`

| Method | Endpoint | Response |
|--------|----------|----------|
| `GET` | `/api/safe-zones` | GeoJSON FeatureCollection with ranked safe zones |

Response includes `safe_score` and the 4 component scores in each feature's properties.

### 6. Pydantic Models: `backend/app/models/flood.py`

```python
class PredictRequest(BaseModel):
    river_levels: list[RiverLevelInput] | None = None

class RiverLevelInput(BaseModel):
    station_name: str
    current_level_m: float
    forecast_rise_m: float = 0.0

class PredictResponse(BaseModel):
    updated: int
    anomalies: list[AnomalyAlert]

class AnomalyAlert(BaseModel):
    station_name: str
    z_score: float
    message: str
```

---

## Acceptance Criteria

| # | Criterion | Verifiable By |
|---|-----------|---------------|
| AC1 | `GET /api/flood-zones` returns valid GeoJSON with `risk_score` for each village | curl + validate JSON structure |
| AC2 | Villages with elevation below projected flood level have `risk_score` > 0.7 | Verify with known seed data values |
| AC3 | Villages well above flood level have `risk_score` = 0.0 | Verify with known seed data values |
| AC4 | `POST /api/predict` recalculates risk scores and returns updated count | curl with custom river-level payload |
| AC5 | `GET /api/safe-zones` returns GeoJSON with `safe_score` and 4 component scores | curl + validate JSON structure |
| AC6 | Safe zones in a flood zone (risk > 0.7) are excluded from results | Raise river levels artificially high, verify exclusion |
| AC7 | Safe zones are returned sorted by `safe_score` descending | Verify JSON array order |
| AC8 | Anomaly detection flags stations where z-score > 2.0 | Seed a river level far above historical average, verify flag |
| AC9 | `POST /api/predict` with no body uses existing DB river-level data | curl with empty body |
| AC10 | All endpoints return JSON (R11) and respond within 500ms (R35) | Measure response time |

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/services/prediction.py` | NEW | Flood prediction + anomaly detection |
| `backend/app/services/safezone.py` | NEW | Safe-zone ranking algorithm |
| `backend/app/models/flood.py` | NEW | Pydantic schemas |
| `backend/app/routes/flood.py` | MODIFY | Replace stubs with real endpoints |
| `backend/app/routes/safezone.py` | MODIFY | Replace stubs with real endpoint |
