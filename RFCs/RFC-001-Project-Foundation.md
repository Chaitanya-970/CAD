# RFC-001: Project Foundation & Data Layer

> **Features:** F13 (SQLite Database & Schema), F14 (FastAPI Backend with CORS)
> **Predecessors:** None
> **Successors:** RFC-002, RFC-003, RFC-004, RFC-005, RFC-006
> **Complexity:** Medium
> **Primary Track:** Backend
> **Applicable Rules:** R1, R2, R6, R7, R9, R13, R14, R15, R16, R16b, R25, R26, R43, R46

---

## Summary

This RFC establishes the entire project skeleton — both the Next.js frontend and the Python FastAPI backend — along with the SQLite database, seed data, and configuration system. Every other RFC depends on this being complete and functional.

---

## Scope

### What This RFC Builds
1. Monorepo directory structure per RULES.md R1
2. Next.js frontend scaffolding (empty app with basic layout)
3. FastAPI backend with CORS middleware
4. SQLite database with all 7 tables per PRD §13
5. Seed script that populates villages, safe zones, phone registry, and simulated river levels
6. Environment variable validation (`config.py`)
7. `requirements.txt` and `package.json` with pinned versions

### What This RFC Does NOT Build
- Any UI components (RFC-003)
- Any business logic (RFC-002)
- Any external API integrations (RFC-004, RFC-005)

---

## Technical Specification

### 1. Directory Structure

Create the full structure defined in RULES.md R1. At the end of this RFC, running `cd frontend && npm run dev` should show the Next.js default page, and running `cd backend && uvicorn app.main:app --reload` should show the FastAPI docs at `http://localhost:8000/docs`.

### 2. Backend: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AFIP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
```

### 3. Backend: `backend/app/config.py`

Must load `.env` via `python-dotenv` and validate all required keys on import. If any key is missing, raise `SystemExit` with a clear message listing missing keys (per R16b).

Required keys (all may be empty strings during RFC-001, but the validation structure must exist):
```
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER
GEMINI_API_KEY
GROQ_API_KEY
BHASHINI_API_KEY
BHASHINI_INFERENCE_KEY
```

### 4. Backend: `backend/app/db.py`

SQLite connection helper. Must create the database file if it doesn't exist. Must provide:
- `get_db()` — returns a connection
- `init_db()` — creates all 7 tables if they don't exist
- Helper functions: `fetch_one(query, params)`, `fetch_all(query, params)`, `execute(query, params)`

### 5. Database Schema

Exactly as defined in PRD §13. 7 tables: `villages`, `safe_zones`, `alerts_log`, `sos_messages`, `crop_assessments`, `phone_registry`, `river_levels`.

### 6. Backend: `backend/seed.py`

A standalone script (`python seed.py`) that:
1. Calls `init_db()` to create tables
2. Loads `data/villages.geojson` and inserts ~50–100 village records
3. Loads `data/safe_zones.json` and inserts ~10–15 safe zone records
4. Loads `data/river_levels.json` and inserts 3–5 river station records
5. Inserts 5 phone registry records (placeholder numbers for demo)
6. Is idempotent — can be run multiple times without duplicating data

### 7. Seed Data Files

#### `backend/data/villages.geojson`
GeoJSON FeatureCollection with ~50–100 villages across Dhubri, Majuli, and Silchar districts. Each feature must have properties: `name`, `name_assamese`, `district`, `elevation_m`, `population_est`.

For the hackathon, these can be hand-created with realistic but approximate data. Coordinates must be in the correct geographic region (Brahmaputra valley, Assam).

#### `backend/data/safe_zones.json`
Array of ~10–15 safe zone objects with: `name`, `latitude`, `longitude`, `elevation_m`, `road_access_score` (0–1), `capacity_est`, `nearest_village_name`.

#### `backend/data/river_levels.json`
Array of 3–5 river stations with: `station_name`, `current_level_m`, `danger_level_m`, `forecast_rise_m`.

#### `backend/data/historical.csv`
CSV with columns: `station_name`, `month`, `avg_level_m`, `std_dev_m`. Used by F10 (anomaly detection) in RFC-002.

### 8. Backend: Stub Route Files

Create all 8 route files listed in R1 (`flood.py`, `safezone.py`, `alert.py`, `sms.py`, `sos.py`, `query.py`, `crop.py`, `villages.py`). Each file contains a single placeholder endpoint that returns `{"status": "not_implemented"}`. These stubs will be filled by subsequent RFCs.

Register all routers in `main.py`.

### 9. Frontend: Next.js Scaffolding

Initialize Next.js via `npx -y create-next-app@latest ./frontend` with App Router. Create the basic layout structure:
- `app/layout.jsx` — root layout with page title "AFIP — Flood Intelligence"
- `app/page.jsx` — landing page (can redirect to `/dashboard`)
- `app/dashboard/page.jsx` — empty dashboard placeholder
- `app/crop/page.jsx` — empty crop assessment placeholder
- `src/lib/api.js` — API client with `BASE_URL = 'http://localhost:8000'` and a `fetchAPI(endpoint, options)` helper that wraps `fetch` with error handling and the 10-second timeout from R12

### 10. Git Configuration

Create `.gitignore` per R43. Create `backend/.env.example` with all key names (no values).

---

## Acceptance Criteria

| # | Criterion | Verifiable By |
|---|-----------|---------------|
| AC1 | Running `cd backend && pip install -r requirements.txt && python seed.py && uvicorn app.main:app` starts the server on port 8000 | Manual: visit `http://localhost:8000/api/health` returns `{"status": "ok"}` |
| AC2 | CORS allows requests from `http://localhost:3000` | Manual: frontend `fetch('/api/health')` succeeds without CORS error |
| AC3 | SQLite database contains 7 tables after running `seed.py` | Manual: open DB with `sqlite3 afip.db ".tables"` shows all 7 |
| AC4 | Villages table has ≥50 records with lat/lng in Assam region | SQL: `SELECT COUNT(*) FROM villages` ≥ 50 |
| AC5 | All 10 API stub endpoints return `{"status": "not_implemented"}` | Manual: visit each endpoint in browser or curl |
| AC6 | `config.py` raises `SystemExit` with missing key names when `.env` is absent | Manual: delete `.env`, start server, observe error listing all keys |
| AC7 | Running `cd frontend && npm install && npm run dev` starts Next.js on port 3000 | Manual: visit `http://localhost:3000` |
| AC8 | `frontend/src/lib/api.js` exports `fetchAPI` function with 10-second timeout | Code review |
| AC9 | `.gitignore` excludes `.env`, `node_modules/`, `__pycache__/`, `*.db`, `uploads/*` | Code review |
| AC10 | `seed.py` is idempotent — running it twice does not duplicate records | Manual: run twice, check `SELECT COUNT(*) FROM villages` unchanged |
| AC11 | `backend/.env.example` lists all 7 required key names | Code review |
| AC12 | All route files are created and registered in `main.py` | Manual: `/docs` shows all endpoints |

---

## Files Created

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app entry point with CORS |
| `backend/app/config.py` | Environment variable loading and validation |
| `backend/app/db.py` | SQLite connection helpers and schema init |
| `backend/app/routes/flood.py` | Stub for `/api/flood-zones`, `/api/predict` |
| `backend/app/routes/safezone.py` | Stub for `/api/safe-zones` |
| `backend/app/routes/alert.py` | Stub for `/api/alert/sms`, `/api/alert/ivr` |
| `backend/app/routes/sms.py` | Stub for `/api/sms/webhook` |
| `backend/app/routes/sos.py` | Stub for `/api/sos` |
| `backend/app/routes/query.py` | Stub for `/api/query` |
| `backend/app/routes/crop.py` | Stub for `/api/crop-assess` |
| `backend/app/routes/villages.py` | Stub for `/api/villages` |
| `backend/app/models/` | Empty directory for Pydantic schemas |
| `backend/app/services/` | Empty directory for business logic |
| `backend/seed.py` | Database seeding script |
| `backend/data/villages.geojson` | Village seed data |
| `backend/data/safe_zones.json` | Safe zone seed data |
| `backend/data/river_levels.json` | Simulated river level data |
| `backend/data/historical.csv` | Historical averages for anomaly detection |
| `backend/requirements.txt` | Python dependencies with pinned versions |
| `backend/.env.example` | Template for environment variables |
| `frontend/` | Next.js app (scaffolded via create-next-app) |
| `frontend/src/lib/api.js` | API client helper |
| `frontend/src/app/dashboard/page.jsx` | Dashboard placeholder |
| `frontend/src/app/crop/page.jsx` | Crop assessment placeholder |
| `.gitignore` | Git exclusion rules |
