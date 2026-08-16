import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "afip.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dict-like objects
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute(query: str, args: tuple = ()):
    """Execute a query that modifies the database (INSERT, UPDATE, DELETE)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        return cursor.lastrowid

def execute_many(query: str, args_list: list):
    """Execute a query multiple times with different arguments."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, args_list)
        conn.commit()
        return cursor.rowcount

def fetch_all(query: str, args: tuple = ()):
    """Fetch multiple rows from the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return [dict(row) for row in cursor.fetchall()]

def fetch_one(query: str, args: tuple = ()):
    """Fetch a single row from the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        row = cursor.fetchone()
        return dict(row) if row else None

def init_db():
    """Initializes the database schema if it doesn't exist."""
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
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executescript(SCHEMA)
        conn.commit()
