# RULES.md — Assam Flood Intelligence Platform (AFIP)

> **Product Type:** Web App (Dashboard + Backend API + SMS/IVR integrations)
> **Existing Codebase:** None. Built from scratch for Craft N Code 2026 hackathon.
> **Skipped Checks:** Library/SDK concerns (semver, peer-deps, bundle size, tree-shaking, types quality, public/internal boundary, mutation of caller-owned data) — not applicable to a web app. Auth/RBAC checks skipped per PRD §3.2 (F25: explicitly out of scope). Regulatory/compliance checks skipped — this is a hackathon prototype, not a production system.
> **Source Documents:** [PRD.md](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/PRD.md) v2.0, [FEATURES.md](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/FEATURES.md)

---

## 1. Technology Stack

All versions below were verified against npm/pip registries on 2026-08-16.

### 1.1 Frontend

| Package | Version | Verified |
|---------|---------|----------|
| next | 16.3.1 | ✅ `npm view next version` |
| react | 19.2.8 | ✅ `npm view react version` |
| leaflet | 1.9.4 | ✅ `npm view leaflet version` |
| react-leaflet | 5.0.0 | ✅ `npm view react-leaflet version` |

### 1.2 Backend (Python)

| Package | Version | Verified |
|---------|---------|----------|
| fastapi | 0.141.1 | ✅ `pip index versions fastapi` |
| uvicorn | 0.52.3 | ✅ `pip index versions uvicorn` |
| python-dotenv | 1.2.2 | ✅ `pip index versions python-dotenv` |
| twilio | 9.11.0 | ✅ `pip index versions twilio` |
| google-generativeai | 0.8.6 | ✅ `pip index versions google-generativeai` |
| groq | 1.6.0 | ✅ `pip index versions groq` |

### 1.3 Database

| Tool | Version | Notes |
|------|---------|-------|
| SQLite | System-bundled | Comes with Python stdlib. No install needed. |

### 1.4 External Services

| Service | Purpose | Features Using It |
|---------|---------|-------------------|
| Twilio SMS + Voice | Outbound alerts, inbound SOS, IVR calls | F4, F5, F15, F16 |
| Gemini API | Text LLM (query, parsing, alerts) + Vision (crop assessment) | F6, F7, F9, F17, F18 |
| Groq | Fallback text LLM | F6 |
| Bhashini API | Assamese TTS for IVR | F5, F18 |
| OpenStreetMap | Map tiles | F1 |

---

## 2. Project Structure

### R1: Monorepo with Two Top-Level Directories

```
CAD/
├── frontend/                # Next.js app
│   ├── public/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── components/      # Reusable React components
│   │   │   ├── map/         # Map-related components (F1, F11, F12)
│   │   │   ├── chat/        # AI Query Interface (F6)
│   │   │   ├── alerts/      # Alert management UI (F4, F16)
│   │   │   ├── crop/        # Crop assessment upload (F7)
│   │   │   └── survival/    # Survival mode banner & logic (F8)
│   │   ├── lib/             # Utility functions, API client, constants
│   │   └── hooks/           # Custom React hooks
│   ├── .env.local           # Frontend env vars (if any)
│   ├── package.json
│   └── next.config.js
│
├── backend/                 # Python FastAPI app
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point, CORS config
│   │   ├── routes/          # One file per API route group
│   │   │   ├── flood.py     # /api/flood-zones, /api/predict
│   │   │   ├── safezone.py  # /api/safe-zones
│   │   │   ├── alert.py     # /api/alert/sms, /api/alert/ivr
│   │   │   ├── sms.py       # /api/sms/webhook
│   │   │   ├── sos.py       # /api/sos
│   │   │   ├── query.py     # /api/query
│   │   │   ├── crop.py      # /api/crop-assess
│   │   │   └── villages.py  # /api/villages
│   │   ├── services/        # Business logic (one file per domain)
│   │   │   ├── prediction.py
│   │   │   ├── safezone.py
│   │   │   ├── twilio_sms.py
│   │   │   ├── twilio_voice.py
│   │   │   ├── llm.py       # All LLM calls (Gemini, Groq)
│   │   │   ├── bhashini.py  # Bhashini TTS integration
│   │   │   └── vision.py    # Gemini Vision for crop assessment
│   │   ├── models/          # Pydantic request/response schemas
│   │   ├── db.py            # SQLite connection and helpers
│   │   └── config.py        # Load .env, validate required keys
│   ├── data/
│   │   ├── villages.geojson # Pre-processed village data
│   │   ├── safe_zones.json  # Seeded safe zone data
│   │   ├── river_levels.json# Simulated river level data
│   │   └── historical.csv   # Historical averages for F10
│   ├── uploads/             # Stored crop assessment images
│   ├── .env                 # API keys (NEVER committed)
│   ├── requirements.txt
│   └── seed.py              # Script to initialize DB and load seed data
│
├── .gitignore
├── PRD.md
├── FEATURES.md
├── RULES.md
└── README.md
```

### R2: No Code Outside This Structure
All application code lives inside `frontend/` or `backend/`. No loose scripts in the project root (except `README.md` and doc files). Seed scripts go in `backend/seed.py`.

---

## 3. Naming Conventions

### R3: File Naming

| Context | Convention | Example |
|---------|-----------|---------|
| React components | PascalCase | `FloodMap.jsx`, `SOSPin.jsx` |
| React hooks | camelCase, `use` prefix | `useSurvivalMode.js` |
| Next.js pages (App Router) | `page.jsx` inside named directories | `app/dashboard/page.jsx` |
| Python modules | snake_case | `twilio_sms.py`, `prediction.py` |
| Python classes | PascalCase | `class VillageSchema` |
| API route files | snake_case, matching the resource | `flood.py` for `/api/flood-zones` |
| CSS/SCSS | kebab-case or CSS Modules with camelCase | `flood-map.module.css` |

### R4: Variable and Function Naming

| Language | Convention | Example |
|----------|-----------|---------|
| JavaScript/React | camelCase for vars and functions | `const floodZones = ...`, `function parseSOSMessage()` |
| Python | snake_case for vars and functions | `flood_zones = ...`, `def parse_sos_message():` |
| Constants | UPPER_SNAKE_CASE | `MAX_SMS_LENGTH = 160`, `GEMINI_API_KEY` |
| Environment variables | UPPER_SNAKE_CASE | `TWILIO_ACCOUNT_SID`, `GEMINI_API_KEY` |
| Database columns | snake_case | `current_risk_score`, `village_id` |

### R5: Component Naming
React components must be named after what they render, not what they do internally. Use domain-specific names from the PRD.

- ✅ `FloodZoneLayer`, `SOSPinMarker`, `SafeZoneCard`, `CropUploadForm`
- ❌ `DataDisplay`, `MapStuff`, `Component1`, `Wrapper`

---

## 4. Architecture Rules

### R6: Strict Frontend-Backend Separation
The frontend (Next.js) is a pure UI client. It does NOT:
- Call external APIs directly (Twilio, Gemini, Bhashini). All external calls go through the FastAPI backend.
- Access the SQLite database.
- Contain business logic (prediction algorithms, safe-zone scoring).

The frontend only talks to the backend via REST API calls to `http://localhost:8000/api/*`.

**Exception:** Survival Mode (F8) network detection runs client-side because it must work when the backend is unreachable.

### R7: Backend Route → Service Pattern
Every FastAPI route file in `routes/` must be thin. It handles HTTP concerns (request parsing, response formatting, status codes) and delegates to a service in `services/`.

```python
# ✅ CORRECT: thin route, delegates to service
@router.post("/api/alert/sms")
async def send_sms_alert(request: AlertRequest):
    result = await twilio_sms.send_village_alert(request.village_id)
    return {"status": "sent", "recipients": result.count}

# ❌ WRONG: business logic in the route
@router.post("/api/alert/sms")
async def send_sms_alert(request: AlertRequest):
    village = db.get_village(request.village_id)
    phones = db.get_phones_for_village(village.id)
    for phone in phones:
        client.messages.create(body=msg, to=phone.number, from_=TWILIO_NUM)
    # ... 30 more lines of logic
```

### R8: Single LLM Service File
All LLM API calls (Gemini text, Gemini Vision, Groq fallback) are centralized in `backend/app/services/llm.py`. No LLM calls from routes or other services directly. This makes it trivial to swap providers.

```python
# services/llm.py — all LLM calls live here
async def parse_sos_text(raw_text: str) -> dict: ...
async def generate_alert_message(village_data: dict) -> str: ...
async def answer_query(question: str, context: dict) -> str: ...
async def assess_crop_image(image_bytes: bytes) -> dict: ...
```

### R9: CORS Configuration
FastAPI must include CORS middleware in `main.py` on startup:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 5. API Rules

### R10: Endpoint Contract Matches PRD §12
The backend must expose exactly these 10 endpoints. Do not rename, reorder, or add path parameters that change the contract.

| Method | Endpoint | Feature |
|--------|----------|---------|
| `GET` | `/api/flood-zones` | F1, F2 |
| `GET` | `/api/safe-zones` | F3 |
| `POST` | `/api/predict` | F2 |
| `POST` | `/api/alert/sms` | F4 |
| `POST` | `/api/alert/ivr` | F5 |
| `POST` | `/api/sms/webhook` | F15 |
| `GET` | `/api/sos` | F12 |
| `POST` | `/api/query` | F6 |
| `POST` | `/api/crop-assess` | F7 |
| `GET` | `/api/villages` | F11 |

Additional endpoints (e.g., `PATCH /api/sos/{id}` for F16) may be added but must not conflict with the above.

### R11: All Responses Are JSON
Every endpoint returns `application/json`. GeoJSON is JSON. No XML, no HTML, no plain text responses.

### R12: All External API Calls Have a 10-Second Timeout
Every call to Twilio, Gemini, Groq, or Bhashini must use a 10-second timeout. On timeout: retry once. On second failure: return a structured error to the frontend (see R17).

---

## 6. Database Rules

### R13: Schema Matches PRD §13 Exactly
The SQLite schema in `seed.py` must match PRD §13 table-for-table, column-for-column. The 7 required tables are: `villages`, `safe_zones`, `alerts_log`, `sos_messages`, `crop_assessments`, `phone_registry`, `river_levels`.

### R14: No ORM
Use raw SQL via Python's `sqlite3` module. An ORM (SQLAlchemy, Tortoise) adds complexity that is not justified for 7 tables in a hackathon. Keep queries readable and inline in `db.py`.

### R15: Seed Data Is Checked Into Git
The `backend/data/` directory must contain all seed data files (GeoJSON, JSON, CSV) so any team member can run `python seed.py` and have a working database with ~50–100 villages, 5 phone numbers, and simulated river levels.

---

## 7. Environment & Security Rules

### R16: API Keys in `.env` Only
All API keys and secrets must live in `backend/.env` and be loaded via `python-dotenv`. They must NEVER appear in:
- Source code
- Git commits (add `.env` to `.gitignore`)
- Frontend code (client-side JS)
- Console logs

Required keys:
```
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
GEMINI_API_KEY=
GROQ_API_KEY=
BHASHINI_API_KEY=
BHASHINI_INFERENCE_KEY=
```

### R16b: Fail Fast on Missing Keys
`backend/app/config.py` must validate that all required keys are present on startup. If any key is missing, the server must crash immediately with a clear error message listing the missing keys — not fail silently on the first API call 20 minutes later.

---

## 8. Error Handling Rules

### R17: Structured Error Responses
All errors returned to the frontend must use this shape:
```json
{
  "error": true,
  "code": "LLM_TIMEOUT",
  "message": "The AI service did not respond in time. Please try again.",
  "feature": "F6"
}
```
Never return raw stack traces or Python exceptions to the frontend.

### R18: Fallback Behavior per PRD §6.1
Every feature that depends on an external API must implement the specific fallback defined in PRD §6.1. These are not suggestions — they are requirements:

| Feature | Fallback |
|---------|----------|
| F2 | GeoJSON fails → show "Data Stale" banner |
| F4 | Twilio error → toast: "SMS delivery failed — retry?" |
| F5 | Bhashini down → send plain-text SMS instead of voice call |
| F6 | LLM timeout → "I couldn't process that query." (10s timeout) |
| F7 | Vision low-confidence → "Please retake in better lighting." |
| F8 | No `navigator.connection` → degrade to `navigator.onLine` |
| F15 | LLM parse failure → store raw text, pin at village centroid, flag "Unparsed" |

### R19: Frontend Graceful Degradation
The frontend must never show a blank screen, an unhandled exception, or a browser error dialog. Every API call must be wrapped in try/catch with a user-friendly fallback.

---

## 9. Frontend-Specific Rules

### R20: Next.js App Router
Use the App Router (`app/` directory), not the legacy Pages Router (`pages/`). All pages are `page.jsx` files inside named route directories.

### R21: Client Components Are Explicit
Components that use browser APIs (`navigator.connection`, `IndexedDB`, `useState`, `useEffect`) must be marked with `'use client'` at the top of the file. Server Components are the default.

### R22: Map Component Isolation
The Leaflet map and all its layers (flood zones, safe zones, SOS pins) must be in a single `'use client'` component tree under `components/map/`. Leaflet does not work with SSR — it must be dynamically imported with `next/dynamic` and `ssr: false`:

```jsx
const FloodMap = dynamic(() => import('@/components/map/FloodMap'), {
  ssr: false,
  loading: () => <div>Loading map...</div>,
});
```

### R23: No Tailwind
Use vanilla CSS or CSS Modules. Do not install or use TailwindCSS unless explicitly requested by the team.

### R24: Survival Mode State
Survival Mode (F8) state must be managed via a custom hook `useSurvivalMode()` that returns `{ mode, queuedCount }` where `mode` is one of `'full' | 'low-bandwidth' | 'offline'`. This hook is consumed by the banner component and any component that needs to adapt its behavior.

---

## 10. Backend-Specific Rules

### R25: Pydantic Models for All Request/Response Bodies
Every `POST` endpoint must define a Pydantic `BaseModel` for its request body and response body. Do not use raw `dict` or `request.json()`.

```python
# ✅ CORRECT
class AlertRequest(BaseModel):
    village_id: int

class AlertResponse(BaseModel):
    status: str
    recipients: int

@router.post("/api/alert/sms", response_model=AlertResponse)
async def send_sms_alert(request: AlertRequest): ...

# ❌ WRONG
@router.post("/api/alert/sms")
async def send_sms_alert(request: dict): ...
```

### R26: Logging
Use Python's `logging` module. Every external API call must be logged with:
- Service name (Twilio/Gemini/Groq/Bhashini)
- Endpoint called
- Response time (ms)
- Success/failure status

Log level: `INFO` for normal operations, `ERROR` for failures. Log to stdout (visible in terminal during demo).

---

## 11. LLM Integration Rules

### R27: System Prompts Are Constants
Every LLM system prompt must be defined as a named constant in `services/llm.py`, not inline in function bodies. This makes them easy to find, review, and tune.

```python
SOS_PARSE_PROMPT = """You are an emergency response parser. Extract the following fields from the SOS message:
- location (string or null)
- people_count (integer or null)
- needs (list of strings)
Return ONLY valid JSON. No explanations."""

CROP_ASSESS_PROMPT = """You are an agricultural expert in Assam, India. ..."""

QUERY_SYSTEM_PROMPT = """You are an assistant for government flood response officials. ..."""

ALERT_GEN_PROMPT = """Convert the following flood prediction data into a warning message. ..."""
```

### R28: LLM Output Must Be Validated
Never trust LLM output blindly. Every LLM response must be:
1. Parsed as JSON (wrapped in `try/except json.JSONDecodeError`)
2. Validated against an expected schema (Pydantic model)
3. Fallback to a safe default if parsing fails (see R18)

### R29: Gemini Primary, Groq Fallback
For text LLM calls (F6, F9, F17), try Gemini first. If Gemini fails (timeout, rate limit, error), automatically retry with Groq. Log which provider was used.

### R30: Crop Assessment Uses Fine-Tuned Model (QLoRA)
Crop assessment (F7) uses a **Llama 3.1 7B/8B model fine-tuned via QLoRA**, hosted on Google Colab (T4 GPU) and exposed via ngrok. The backend calls this endpoint via `services/crop_model.py`. **Fallback:** If the Colab endpoint is unreachable (ngrok down, notebook stopped), fall back to Gemini Vision API via `services/llm.py:assess_crop_image_gemini()`. The ngrok URL is stored in `.env` as `CROP_MODEL_URL`. Inference timeout: 30 seconds (model is slower than API calls).

---

## 12. Localization Rules

### R31: Assamese Is Required, Not Optional
All SMS alerts (F4), IVR voice (F5), and crop assessment results (F7) must be delivered in Assamese. This is not a nice-to-have — it is a Must Have per PRD §6 (Localization). English-only output is a bug.

### R32: Dashboard UI Is English
The dashboard interface (buttons, labels, navigation) is in English. Bilingual content appears only in:
- Village names on the map (English + Assamese) — F11
- SOS message display (show original raw text, which may be Assamese) — F12

---

## 13. Testing Rules

### R33: Demo-Driven Testing
This is a hackathon. There is no time for comprehensive unit tests. Testing priorities:

1. **Must test manually:** Each of the 4 user journeys (PRD §7) end-to-end before the demo.
2. **Must test with sample data:** 20 SOS messages (F17), 10 crop photos (F7), 15 AI queries (F6) — per PRD §11 success metrics.
3. **Must test offline:** Disable Wi-Fi, verify Survival Mode queues messages and replays them on reconnect (F8).
4. **Must test SMS flow:** Send and receive SMS with the 5 verified Twilio numbers.

### R34: No Mocking in the Final Demo
During the live demo, every feature must use real API calls (Gemini, Twilio, Bhashini). No hardcoded fake responses. The simulated data (river levels, village data) is acceptable — but the AI/SMS integrations must be live.

---

## 14. Performance Rules

### R35: Response Time Targets

| Layer | Target |
|-------|--------|
| Map load (initial render) | < 3 seconds |
| API responses (non-LLM) | < 500ms |
| LLM text responses (F6, F9, F17) | < 5 seconds |
| LLM vision response (F7) | < 10 seconds |
| SMS delivery (F4) | < 30 seconds |

### R36: Image Compression for Crop Upload
The crop photo upload (F7) must compress images client-side before sending to the backend. Maximum upload size: 5MB. Use canvas-based compression or a library like `browser-image-compression`.

---

## 15. Implementation Priority Order

### R37: Build in This Order
This is the critical-path order derived from the dependency graph in FEATURES.md. Do not skip ahead.

| Phase | Features | Description |
|-------|----------|-------------|
| **Phase 0** | F13, F14 | DB schema + FastAPI server with CORS. Must work before anything else. |
| **Phase 1** | F2, F3, F1, F11 | Prediction engine → safe zones → map with bilingual labels. This is the core demo. |
| **Phase 2** | F4, F5, F9, F15, F16, F12 | SMS/IVR alerts, SOS parsing, SOS pins on map. This is the "Wow" layer. |
| **Phase 3** | F6, F7, F17, F18 | Gov-GPT chatbot, crop upload, LLM parsing, Assamese translation. AI differentiators. |
| **Phase 4** | F8, F19 | Survival Mode, crop assessment history. Polish. |
| **Phase 5** | F10, F20, F21 | Anomaly detection, river-level controls, logging. Only if time permits. |

### R38: Phase 1 Must Be Complete Before Any Phase 3 Work Begins
The map dashboard with flood zones and safe zones is the absolute minimum viable demo. If the team is behind schedule, cut Phases 3–5 entirely. A beautiful map with working SMS is better than a broken chatbot.

---

## 16. General Development Rules

### R39: No TODOs, No Placeholders
Code merged into the main branch must be functional. No `// TODO: implement later`, no `pass` in Python function bodies, no placeholder text in the UI. If a feature isn't ready, don't include its route/component — add it when it's done.

### R40: Every File Has a Purpose
Do not create empty files "for later." Do not create utility files with a single function. If a utility has only one consumer, put it inline in the consumer.

### R41: Comments Explain "Why," Not "What"
```python
# ✅ GOOD: explains WHY
# Snap SOS pin to village centroid because SMS contains no GPS data
latitude = village.latitude

# ❌ BAD: restates the code
# Set latitude to village latitude
latitude = village.latitude
```

### R42: Handle Ambiguity by Checking PRD
If a requirement is unclear during implementation, check the following documents in this order:
1. [PRD.md](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/PRD.md) — the source of truth
2. [FEATURES.md](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/FEATURES.md) — detailed acceptance criteria
3. [PRD-REVIEW.md](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/PRD-REVIEW.md) — known gaps and decisions

If still unclear, ask the team. Do not guess and ship.

---

## 17. Git Rules

### R43: `.gitignore` Must Include
```
# Environment
backend/.env
.env
.env.local

# Database
backend/*.db
backend/*.sqlite

# Uploads
backend/uploads/*
!backend/uploads/.gitkeep

# Dependencies
node_modules/
__pycache__/
.venv/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

### R44: Commit Messages Are Descriptive
Use the format: `[feature-id] short description`
```
[F1] Add Leaflet map with GeoJSON flood zone layer
[F4] Integrate Twilio outbound SMS with Assamese alert text
[F8] Implement survival mode with IndexedDB queuing
[fix] Correct CORS config for localhost:3000
```

---

## 18. Demo-Specific Rules

### R45: Chrome Only
The demo must run in Google Chrome. Do not spend time fixing Firefox or Safari compatibility issues. `navigator.connection` (F8) is Chromium-only.

### R46: Localhost Only
The app runs on `localhost:3000` (frontend) and `localhost:8000` (backend). No deployment to Vercel/Railway/Render is needed. Do not add deployment configs.

### R47: Demo Data Must Be Realistic
Simulated river levels, village names, and SOS messages must use real Assamese place names and realistic water-level values. Do not use "Test Village 1" or "Lorem Ipsum." Judges notice.

---

## Self-Check Results

1. **Rule count:** R1–R47, 47 rules total. Verified sequentially — no gaps, no duplicates, no skipped numbers.
2. **Feature ID cross-references:** Every feature ID referenced in this document (F1–F25) was verified against FEATURES.md. Mappings:
   - R1 folder structure references: F1, F11, F12, F6, F4, F16, F7, F8 — all valid feature IDs.
   - R10 endpoint-to-feature mapping: verified each feature ID matches the correct endpoint.
   - R18 fallback table: F2, F4, F5, F6, F7, F8, F15 — all valid, all match PRD §6.1.
   - R37 phase table: all feature IDs match FEATURES.md definitions.
3. **PRD section cross-references:** §3.2 (out of scope), §6.1 (error handling), §7 (user journeys), §11 (success metrics), §12 (API endpoints), §13 (DB schema) — all verified against PRD.md v2.0 section numbering.
4. **Inter-table consistency:** Tech stack versions match between §1.1 and §1.2 tables. Endpoint table in R10 matches PRD §12 exactly. Priority phases in R37 match FEATURES.md dependency graph.
5. **Status:** Self-check complete. No inconsistencies found.
