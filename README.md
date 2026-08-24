# AFIP — Assam Flood Intelligence Platform

AFIP is an AI-powered flood early-warning and community-alert dashboard. It predicts which villages along the Brahmaputra valley will flood up to 48 hours in advance, ranks safe zones for relief camps, sends warnings via SMS/IVR (in English and Assamese), lets farmers request help through reply-SOS messages, assesses flood-damaged crops from a photo, and gives government officials a natural-language ("Gov-GPT") query interface over live data — all wrapped in an offline-tolerant "Survival Mode."

It serves three audiences at once: **district officials** (situational-awareness dashboard), **NGO field coordinators** (SOS pins and safe-zone routing on weak connections), and **rural farmers** (SMS/IVR alerts and crop advisories on any phone).

---

## Problem & Motivation

Assam's annual floods expose three gaps that no single tool solves today:

1. **Prediction** — communities learn about flooding only when water reaches their door.
2. **Delivery** — warnings fail to reach people on basic phones or weak networks.
3. **Inclusion** — farmers have no way to call for help or assess crop damage afterward.

AFIP closes all three gaps in one connected system instead of building isolated pieces (a chatbot, a map, an alert app).

---

## Key Features

### Flood Prediction & Alerts
- Rule-based 48-hour forecast: compares projected river level (`current + forecast rise`) against each village's elevation to compute a 0–1 risk score.
- Risk tiers: **high** (≥ 0.7), **moderate** (0.3–0.7), **safe** (< 0.3).
- Statistical anomaly detection (z-score vs. monthly historical averages) flags unusual river levels early.
- LLM-generated, human-readable alert text (urgent but calm, ~160 chars).

### Interactive Map Dashboard
- Leaflet map with color-coded village markers (red/yellow/green), safe-zone markers, and live SOS pins.
- Bilingual village labels (English + Assamese) in popups.
- Status bar: villages tracked, red zones, active SOS count.
- Falls back to bundled demo data automatically if the backend is unreachable.

### AI-Powered Query / Chat ("Gov-GPT")
- Officials ask questions in plain English ("Which villages near Dhubri are at risk?").
- Answers are grounded strictly in a live database context (villages, safe zones, active SOS).
- Groq (Llama 3.1) primary for speed, Gemini fallback.

### Crop Advisories
- Farmers upload a photo of a flooded field (auto-compressed client-side to ≤ 5 MB).
- Fine-tuned Qwen2-VL model hosted on Google Colab assesses damage; automatic **Gemini Vision fallback** if the Colab endpoint is down.
- Returns crop type, damage %, and recovery advisory in **English and Assamese**; history stored in the database.

### SOS & Safe Zones
- Inbound SOS replies are parsed by an LLM into `{location, people_count, needs}` and pinned on the map (village centroid geolocation).
- SOS lifecycle: `active → acknowledged → resolved`.
- Safe zones ranked by weighted score: elevation × 0.4 + road access × 0.25 + distance-from-river × 0.2 + capacity × 0.15; zones near high-risk villages are excluded under extreme scenarios.

### SMS Integration (Twilio)
- Outbound SMS alerts to registered phone numbers when a village enters the red zone.
- Inbound webhook receives farmer replies and turns them into SOS records.
- IVR voice calls in Assamese via Bhashini TTS + Twilio Voice (planned/stubbed).

### Survival / Offline Mode
- Detects network quality via `navigator.connection` (Chromium) with `navigator.onLine` fallback.
- Three modes: **Full**, **Low-Bandwidth** (map replaced by text list view), **Offline**.
- Outbound requests queue in **IndexedDB** and auto-flush when connectivity returns (10 s polling + online event), with a banner showing mode and queued count.

### Simulation Panel
- Simulate river-level changes from the UI and re-run predictions instantly to demo how risk zones shift (RFC-003 F20).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Next.js](https://nextjs.org/) 16 (App Router) · React 19 · react-leaflet 5 / Leaflet 1.9 · lucide-react icons · CSS Modules |
| Backend | Python · FastAPI · Uvicorn · Pydantic · SQLite (file-based, zero-config) |
| AI / ML | Groq API (Llama 3.1 8B) · Google Gemini (`gemini-flash-latest`, incl. Vision) · QLoRA fine-tuned model via Gradio/Colab endpoint |
| Comms | Twilio (SMS/Voice) · Bhashini TTS (Assamese voice) |

Backend dependencies ([requirements.txt](backend/requirements.txt)): `fastapi`, `uvicorn`, `python-dotenv`, `httpx`, `python-multipart`, `twilio`, `google-generativeai`, `groq`, `gradio-client`.

---

## Architecture Overview

```
Next.js frontend (:3000)  ──REST/JSON + GeoJSON──►  FastAPI backend (:8000)
        │                                              │
        │ IndexedDB offline queue                      ├─► SQLite (backend/afip.db)
        │ (Survival Mode retry)                        │     villages · safe_zones · alerts_log
        ▼                                              │     sos_messages · crop_assessments
   Mock/demo data                                      │     phone_registry · river_levels
   (when backend unreachable)                          │
                                                       ├─► services/: prediction · safezone
                                                       │    ranking · llm orchestration · crop model
                                                       ▼
                                          Twilio · Gemini · Groq · Bhashini · Colab (ngrok)
```

- The frontend calls the backend through a thin typed client ([frontend/src/lib/api.js](frontend/src/lib/api.js)); map layers consume **GeoJSON FeatureCollections** served by the backend.
- Route modules stay thin; business logic lives in `services/` (prediction math, safe-zone scoring, LLM provider fallback chains, crop-model proxying).
- `seed.py` creates and populates the SQLite database and regenerates the static files in `backend/data/`.

---

## Project Structure

```
CAD/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, logging middleware, routers
│   │   ├── config.py          # Env-var loading (exits if required keys missing)
│   │   ├── db.py              # SQLite helpers + schema (7 tables)
│   │   ├── models/            # Pydantic request/response schemas
│   │   ├── routes/            # One router per resource (villages, flood, sos, …)
│   │   └── services/          # Business logic: prediction, safezone, llm, crop_model
│   ├── data/                  # Generated/reference datasets (see Data Files below)
│   ├── uploads/               # Uploaded crop photos land here
│   ├── seed.py                # Creates afip.db + seed data + data/ files
│   ├── test_rfc2.py           # E2E checks for prediction/safe-zone APIs
│   ├── test_rfc5.py           # Schema + LLM SOS-parsing checks
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Template for backend environment variables
├── frontend/
│   ├── src/
│   │   ├── app/               # App Router pages: / (landing), /dashboard, /crop
│   │   ├── components/        # map/, chat/, alerts/, survival/, layout/ + ErrorBoundary
│   │   ├── hooks/useSurvivalMode.js  # Network detection + offline queue flushing
│   │   └── lib/               # api.js (fetch client), offlineQueue.js (IndexedDB), mockData.js
│   ├── package.json           # Scripts + dependencies
│   └── .env.local.example     # Template for frontend environment variables
├── RFCs/                      # RFC-001 … RFC-006 implementation specs
├── PRD.md                     # Product requirements (personas, features, journeys)
├── FEATURES.md                # MoSCoW feature breakdown
├── DESIGN.md                  # Brand palette, typography, component specs
├── TESTING.md                 # Demo-driven test plan by RFC phase
├── RULES.md                   # Project engineering rules
└── RFCS.md                    # RFC index, dependency graph, team split
```

---

## Prerequisites

- **Python 3.10+**
- **Node.js 20+** (required by Next.js 16) and npm
- A Chromium-based browser (Chrome/Edge) for full Survival Mode network detection
- Optional: Twilio, Gemini, Groq, and Bhashini accounts for live integrations (the app degrades gracefully without real keys)

---

## Setup

### 1. Backend (FastAPI)

From the repository root:

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows PowerShell
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create your .env from the template, then fill in values (see table below)
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux

# Create and populate the SQLite database (backend/afip.db)
python seed.py

# Start the API server (defaults to http://localhost:8000)
python -m uvicorn app.main:app --reload
```

> ⚠️ `config.py` **exits at startup** if any required variable in `.env` is empty. For local testing without real accounts, placeholder values such as `dummy` are accepted — AI calls then fall back to safe default responses.

### 2. Frontend (Next.js)

Open a second terminal:

```bash
cd frontend

npm install

# Create your .env.local from the template
copy .env.local.example .env.local    # Windows
# cp .env.local.example .env.local    # macOS/Linux

npm run dev
```

---

## Environment Variables

### Backend — `backend/.env`

| Variable | Required | Description |
|---|---|---|
| `TWILIO_ACCOUNT_SID` | YES | Twilio account SID used for outbound SMS/Voice. |
| `TWILIO_AUTH_TOKEN` | YES | Twilio auth token paired with the account SID. |
| `TWILIO_PHONE_NUMBER` | YES | Twilio phone number that sends alerts / receives SOS replies. |
| `GEMINI_API_KEY` | YES | Google Gemini API key — vision crop assessment, SOS parsing, translations, LLM fallback. Treated as disabled when set to `dummy`. |
| `GROQ_API_KEY` | YES | Groq API key — primary LLM for Gov-GPT queries (fast text inference). |
| `BHASHINI_API_KEY` | YES | Bhashini API key for Assamese text-to-speech (IVR alerts). |
| `BHASHINI_INFERENCE_KEY` | YES | Bhashini inference key accompanying the API key. |
| `CROP_MODEL_URL` | Optional | Public (ngrok) URL of the Colab-hosted fine-tuned crop model. If unset or unreachable, assessment falls back to Gemini Vision. |

### Frontend — `frontend/.env.local`

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ➖ Optional | Base URL of the FastAPI backend. Defaults to `http://localhost:8000` if unset. |

---

## Running the App

| Service | URL | Notes |
|---|---|---|
| Frontend (dashboard) | http://localhost:3000 | Landing page at `/`, dashboard at `/dashboard`, crop upload at `/crop` |
| Backend API root | http://localhost:8000 | `{"status": "AFIP Backend is running"}` |
| Health check | http://localhost:8000/api/health | `{"status": "ok"}` |
| Interactive API docs | http://localhost:8000/docs | Auto-generated Swagger UI (FastAPI) |

The dashboard polls for new SOS messages every 10 seconds and shows a **"Demo data — backend unreachable"** badge whenever it falls back to mock data.

---

## API Endpoints Summary

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Root status message. |
| GET | `/api/health` | Health check. |
| GET | `/api/villages` | Village metadata (name, bilingual name, district, coords, elevation, population). |
| GET | `/api/flood-zones` | All villages as a GeoJSON FeatureCollection with `risk_score` / `risk_level`. |
| POST | `/api/predict` | Run the flood-prediction engine. Accepts optional simulated `river_levels`; persists scores and returns `{updated, anomalies}`. |
| GET | `/api/safe-zones` | Ranked safe zones as GeoJSON, including score breakdowns. |
| GET | `/api/sos` | List SOS messages; optional `?status=` filter (`active`/`acknowledged`/`resolved`). |
| PATCH | `/api/sos/{sos_id}` | Update an SOS message's status. |
| POST | `/api/query` | Gov-GPT: natural-language question answered against live database context. |
| POST | `/api/crop-assess` | Multipart image upload → AI crop-damage assessment (≤ 5 MB). |
| GET | `/api/crop-assessments` | Crop assessment history. |
| POST | `/api/alert/sms` | Send SMS alerts for a village *(stub — returns `not_implemented`)*. |
| POST | `/api/alert/ivr` | Trigger IVR voice alerts *(stub — returns `not_implemented`)*. |
| POST | `/api/sms/webhook` | Inbound Twilio SMS webhook *(stub — returns `not_implemented`)*. |

---

## Data Files (`backend/data/`)

| File | What it is |
|---|---|
| `historical.csv` | Monthly average river levels + standard deviation per station (regenerated by `seed.py`). Used by the anomaly detector for z-score checks. |
| `river_history.csv` | Checked-in copy of the same historical monthly river-level series per station/month. |
| `river_levels.json` | Small snapshot of current simulated river levels (station → level). |
| `safe_zones.json` | JSON dump of the seeded safe zones (written by `seed.py`). |
| `villages.geojson` | GeoJSON FeatureCollection of the seeded villages (written by `seed.py`) for map layer reference. |

Seeding creates **60 villages** across Majuli, Dhubri, and Silchar, **10 safe zones**, **3 river-gauge stations**, and **5 registered phone numbers**.

---

## Testing

Per [RULES.md](RULES.md) this project follows **demo-driven testing** (manual E2E journeys over exhaustive unit suites) — see [TESTING.md](TESTING.md) for the full plan by RFC phase.

Two script-style checks live in `backend/`:

```bash
# Terminal 1 — start the backend first
python -m uvicorn app.main:app --reload

# Terminal 2 — RFC-002 checks: /api/predict, /api/flood-zones, /api/safe-zones,
# sorting, and the extreme-flood safe-zone exclusion (AC6)
python test_rfc2.py

# RFC-005 checks: Pydantic schemas + LLM SOS parsing.
# The LLM portion is skipped unless GEMINI_API_KEY is set in backend/.env
python test_rfc5.py
```

`test_rfc2.py` targets `http://127.0.0.1:8000`, so keep the backend on its default port.

---

## Troubleshooting

| Symptom | Cause & Fix |
|---|---|
| Backend exits immediately with `CRITICAL: Missing required environment variable: …` | A required key in `backend/.env` is empty. Fill **all seven required variables** (placeholder values like `dummy` are accepted for local runs). |
| Dashboard shows "Demo data — backend unreachable" | Backend isn't running, or `NEXT_PUBLIC_API_URL` points elsewhere. Start uvicorn and confirm port 8000. |
| Map renders no villages | Database not seeded. Run `python seed.py` inside `backend/`. |
| CORS errors in the browser console | The backend only allows `http://localhost:3000`. Keep the frontend on the default dev port. |
| AI answers are always "I couldn't process that query…" | Both LLM providers failed — usually invalid/dummy API keys. Add real `GROQ_API_KEY` / `GEMINI_API_KEY` and restart. |
| Crop assessment takes 10–30 s or returns the generic failure card | The Colab model endpoint (`CROP_MODEL_URL`) is slow/down; the service falls back to Gemini Vision, which needs a working `GEMINI_API_KEY`. |
| `GET /api/crop-assessments` returns a server error | Known mismatch: the route orders by a `created_at` column while the schema defines `assessed_at`. Use the DB column name to fix. |
| Survival Mode never leaves "Full"/"Offline" granularity | `navigator.connection` is Chromium-only; other browsers degrade to simple online/offline detection. Use Chrome for the full demo. |
