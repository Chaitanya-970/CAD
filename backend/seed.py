import sqlite3
import os
import random
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "afip.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

SCHEMA = """
CREATE TABLE IF NOT EXISTS villages (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    name_assamese TEXT,
    district TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    elevation_m REAL NOT NULL,
    population_est INTEGER,
    current_risk_score REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS safe_zones (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    elevation_m REAL NOT NULL,
    road_access_score REAL DEFAULT 0.5,
    capacity_est INTEGER,
    safe_score REAL DEFAULT 0.0,
    nearest_village_id INTEGER REFERENCES villages(id)
);

CREATE TABLE IF NOT EXISTS alerts_log (
    id INTEGER PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id),
    alert_type TEXT CHECK(alert_type IN ('sms', 'ivr', 'both')),
    message_text TEXT,
    recipients_count INTEGER,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    twilio_status TEXT
);

CREATE TABLE IF NOT EXISTS sos_messages (
    id INTEGER PRIMARY KEY,
    from_number TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    parsed_location TEXT,
    parsed_needs TEXT,
    parsed_people_count INTEGER,
    latitude REAL,
    longitude REAL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'acknowledged', 'resolved')),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crop_assessments (
    id INTEGER PRIMARY KEY,
    image_path TEXT NOT NULL,
    crop_type TEXT,
    damage_pct REAL,
    advisory_en TEXT,
    advisory_as TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS phone_registry (
    id INTEGER PRIMARY KEY,
    phone_number TEXT NOT NULL UNIQUE,
    village_id INTEGER REFERENCES villages(id),
    name TEXT,
    language_pref TEXT DEFAULT 'as' CHECK(language_pref IN ('en', 'as', 'bn'))
);

CREATE TABLE IF NOT EXISTS river_levels (
    id INTEGER PRIMARY KEY,
    station_name TEXT NOT NULL,
    current_level_m REAL NOT NULL,
    danger_level_m REAL NOT NULL,
    forecast_rise_m REAL DEFAULT 0.0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DISTRICTS = {
    "Majuli": {"lat": 26.95, "lng": 94.16, "base_elev": 85.0},
    "Dhubri": {"lat": 26.02, "lng": 89.97, "base_elev": 34.0},
    "Silchar": {"lat": 24.83, "lng": 92.77, "base_elev": 22.0},
}

def generate_villages(count=50):
    villages = []
    for i in range(1, count + 1):
        district = random.choice(list(DISTRICTS.keys()))
        base = DISTRICTS[district]
        
        # Add random offset for lat/lng (approx 10km radius)
        lat_offset = random.uniform(-0.1, 0.1)
        lng_offset = random.uniform(-0.1, 0.1)
        elev_offset = random.uniform(-5.0, 15.0)
        
        villages.append({
            "id": i,
            "name": f"{district} Village {i}",
            "name_assamese": f"গাওঁ {i}",
            "district": district,
            "latitude": round(base["lat"] + lat_offset, 4),
            "longitude": round(base["lng"] + lng_offset, 4),
            "elevation_m": round(base["base_elev"] + elev_offset, 1),
            "population_est": random.randint(500, 5000)
        })
    return villages

def generate_safe_zones(villages):
    zones = []
    for i in range(1, 11):
        v = random.choice(villages)
        zones.append({
            "id": i,
            "name": f"Safe Zone {i}",
            "latitude": v["latitude"] + random.uniform(-0.02, 0.02),
            "longitude": v["longitude"] + random.uniform(-0.02, 0.02),
            "elevation_m": v["elevation_m"] + random.uniform(5.0, 20.0),
            "road_access_score": round(random.uniform(0.3, 1.0), 2),
            "capacity_est": random.randint(500, 2000),
            "safe_score": 0.0,
            "nearest_village_id": v["id"]
        })
    return zones

def seed():
    print("Initializing Database Schema...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA)

    print("Generating Seed Data...")
    villages = generate_villages(60)
    safe_zones = generate_safe_zones(villages)
    
    # Insert Villages
    for v in villages:
        cursor.execute(
            """INSERT OR IGNORE INTO villages (id, name, name_assamese, district, latitude, longitude, elevation_m, population_est) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (v["id"], v["name"], v["name_assamese"], v["district"], v["latitude"], v["longitude"], v["elevation_m"], v["population_est"])
        )
        
    # Insert Safe Zones
    for sz in safe_zones:
        cursor.execute(
            """INSERT OR IGNORE INTO safe_zones (id, name, latitude, longitude, elevation_m, road_access_score, capacity_est, safe_score, nearest_village_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (sz["id"], sz["name"], sz["latitude"], sz["longitude"], sz["elevation_m"], sz["road_access_score"], sz["capacity_est"], sz["safe_score"], sz["nearest_village_id"])
        )

    # Insert Phone Registry (Team members)
    phones = [
        (1, "+1234567890", 1, "Alice", "en"),
        (2, "+0987654321", 2, "Bob", "as"),
        (3, "+1122334455", 3, "Charlie", "bn"),
        (4, "+5544332211", 4, "David", "en"),
        (5, "+9988776655", 5, "Eve", "as"),
    ]
    for p in phones:
        cursor.execute(
            """INSERT OR IGNORE INTO phone_registry (id, phone_number, village_id, name, language_pref)
               VALUES (?, ?, ?, ?, ?)""",
            p
        )

    # Insert River Levels
    rivers = [
        (1, "Brahmaputra at Majuli", 84.5, 85.0, 0.2),
        (2, "Brahmaputra at Dhubri", 33.5, 34.0, 0.1),
        (3, "Barak at Silchar", 21.0, 22.0, 0.5),
    ]
    for r in rivers:
        cursor.execute(
            """INSERT OR IGNORE INTO river_levels (id, station_name, current_level_m, danger_level_m, forecast_rise_m)
               VALUES (?, ?, ?, ?, ?)""",
            r
        )

    conn.commit()
    conn.close()
    print(f"Database successfully seeded at {DB_PATH}!")
    
    # Save to data directory for reference/GeoJSON layers
    os.makedirs(DATA_DIR, exist_ok=True)
    
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [v["longitude"], v["latitude"]]},
                "properties": v
            } for v in villages
        ]
    }
    
    with open(os.path.join(DATA_DIR, "villages.geojson"), "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
        
    with open(os.path.join(DATA_DIR, "safe_zones.json"), "w", encoding="utf-8") as f:
        json.dump(safe_zones, f, indent=2, ensure_ascii=False)
        
    print(f"Data files written to {DATA_DIR}")

if __name__ == "__main__":
    seed()
