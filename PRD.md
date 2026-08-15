# PRD: Assam Flood Intelligence Platform (AFIP)

> **Product Type:** Web App (Dashboard + Backend API + SMS/IVR integrations)
> **Skipped Checks:** Library/SDK concerns (semver, peer-deps, bundle size, tree-shaking, types quality, public/internal boundary, mutation of caller-owned data) — not applicable to a web app.
> **Status:** v2.0 (Post-Review)
> **Date:** 2026-08-16

---

## 1. Overview

The **Assam Flood Intelligence Platform (AFIP)** is a proactive disaster-management web application that predicts flooding 48 hours in advance, dynamically recommends safe zones for relief camps, delivers inclusive warnings via SMS/IVR to non-smartphone users, provides AI-powered post-flood crop damage assessment, and offers a natural-language query interface for government officials.

**Value Proposition:** Instead of solving one isolated piece (a chatbot, a map, an alert app), AFIP closes all three major gaps in Assam's flood response — **prediction**, **delivery**, and **inclusion** — in one connected system.

**Context:** This product is being built for a hackathon ("Craft N Code 2026"). There is no existing codebase; the project is being built from scratch.

---

## 2. Goals and Objectives

| # | Goal | Measurable Target |
|---|------|-------------------|
| G1 | Predict which villages will flood before it happens | System generates a flood-risk map for at least 2–3 districts along the Brahmaputra using elevation + river-level data |
| G2 | Ensure warnings reach everyone, regardless of device or literacy | SMS and Assamese IVR voice calls are sent to registered phone numbers; farmers can reply via SMS to send SOS |
| G3 | Minimize crop loss through timely advisory | Pre-flood advisories are generated and sent; post-flood photo upload returns AI-driven damage assessment |
| G4 | Give officials instant situational awareness | Dashboard shows live flood zones, safe zones, and incoming SOS; officials can query the system in natural language |
| G5 | Maintain functionality under degraded network conditions | "Survival Mode" detects weak signal and downgrades payloads; queues unsent messages for retry |

---

## 3. Scope

### 3.1 In Scope (Hackathon MVP)

- 48-hour flood prediction using pre-processed GeoJSON elevation data and rule-based threshold logic
- Interactive map dashboard (Leaflet.js) with red/green zone visualization
- Dynamic safe-zone recommendation with multi-factor weighted scoring
- Two-way SMS integration (Twilio): outbound alerts + inbound SOS replies displayed on dashboard
- IVR voice call alerts in Assamese (Bhashini TTS + Twilio Voice)
- Post-flood crop damage assessment via photo upload (Gemini Vision API)
- AI Query Interface ("Gov-GPT") for natural-language questions against live data
- Survival Mode: bandwidth detection + message queuing with automatic retry
- Full bilingual support (English dashboard + Assamese SMS/IVR)
- Geographic scope: 2–3 districts along the Brahmaputra
- Local deployment (laptop demo for judges)

### 3.2 Out of Scope (Post-Hackathon / Future)

- Real ML model training (LSTM, GNN) for hydrological prediction
- Real-time CWC/IMD API integration (will use simulated or cached data for demo)
- Native mobile app (Android/iOS)
- Offline P2P mesh networking (BLE/Wi-Fi Direct)
- User authentication and role-based access control
- Production-grade deployment, horizontal scaling, load balancing
- Integration with government databases (NDRF, SDRF, revenue records)
- Historical flood analytics and reporting

---

## 4. User Personas

### Persona 1: District Emergency Officer ("Commander Priya")
- **Role:** NDRF/SDRF/District Magistrate office
- **Device:** Laptop or desktop with stable internet
- **Needs:** A single dashboard showing which villages are at risk, where to place camps, and where SOS signals are coming from. Wants to ask questions in plain English and get instant answers.
- **Pain Point:** Currently relies on phone calls and WhatsApp groups to coordinate — information is fragmented and stale within minutes.

### Persona 2: NGO Field Coordinator ("Volunteer Rahul")
- **Role:** Relief supply coordinator for a grassroots NGO
- **Device:** Smartphone with intermittent 3G/4G
- **Needs:** Knows which areas are underserved (no duplicate supplies), sees incoming SOS locations on a map, gets route guidance to safe zones.
- **Pain Point:** Drives supplies to areas that already have aid because there is no centralized view of who has what.

### Persona 3: Rural Farmer ("Kisan Bimal")
- **Role:** Rice farmer in a low-elevation village near the Brahmaputra
- **Device:** Basic flip-phone (no smartphone, no data)
- **Needs:** A phone call or SMS in Assamese telling him to harvest early or move livestock. After the flood, wants to know how badly his crops are damaged and what to do next.
- **Pain Point:** Learns about the flood only when water enters his house. Has no way to ask for help except shouting.

### Persona 4: Farmer with Smartphone ("Kisan Dipika")
- **Role:** Young farmer or farmer's family member with an Android phone
- **Device:** Low-end Android smartphone with weak signal
- **Needs:** Receives push/SMS alerts. After flood recedes, uploads a photo of her flooded field and gets instant AI advice on crop recovery.
- **Pain Point:** App-based alerts fail when the tower is congested. Doesn't know what to do with waterlogged soil.

---

## 5. Functional Requirements

### 5.1 Priority 1 — Must Have (Core Demo)

#### F1: Risk Visualization Dashboard
| Attribute | Detail |
|-----------|--------|
| **Description** | Interactive map (Leaflet.js) showing the target districts with color-coded flood-risk zones (red = predicted flood in 48h, yellow = moderate risk, green = safe zone) |
| **Data Source** | Pre-processed GeoJSON polygons derived from NASA SRTM DEM data, overlaid with simulated river-level data |
| **Interactions** | Click on a zone to see village name, elevation, population estimate, risk score. Zoom/pan. Toggle layers (flood zones, safe zones, SOS pins, population density) |
| **Language** | Dashboard UI in English. Zone names and village labels bilingual (English + Assamese) |

#### F2: 48-Hour Flood Forecasting Engine
| Attribute | Detail |
|-----------|--------|
| **Description** | Backend service that takes current river water level + elevation data and calculates which areas will be submerged if water rises by X meters |
| **Approach** | Rule-based threshold logic: `if river_level + forecast_rise > village_elevation → mark as flooded`. No ML model training required |
| **Input** | Simulated/cached river level data (mocking CWC API), pre-processed DEM-derived village elevation data (GeoJSON) |
| **Output** | Updated GeoJSON with risk scores for each village/zone, served to frontend via API |

#### F3: Dynamic Safe-Zone Recommendation
| Attribute | Detail |
|-----------|--------|
| **Description** | Algorithm that identifies and ranks the safest locations for relief camps and stockpiles near at-risk villages |
| **Scoring Formula** | `SafeScore = (Elevation * 0.4) + (RoadAccess * 0.25) + (DistanceFromRiver * 0.2) + (Capacity * 0.15)` |
| **Output** | Green markers on the map with ranked safe-zone cards showing score breakdown |
| **Update Frequency** | Recalculates whenever river-level input changes |

#### F4: Two-Way SMS Integration (Twilio)
| Attribute | Detail |
|-----------|--------|
| **Outbound** | When a village enters the red zone, the system sends an SMS alert in Assamese to all registered phone numbers in that village |
| **Inbound** | Farmers can reply to the SMS with a free-text message (e.g., "Need help, 4 people stuck"). Twilio webhook receives the message, LLM parses it into structured data `{location, people_count, needs}`, and it appears as an SOS pin on the dashboard |
| **Geolocation** | SMS contains no GPS data. SOS pins are placed at the **centroid of the farmer's registered village** (from `phone_registry.village_id → villages.latitude/longitude`). If the LLM extracts a specific location name from the text, it is geocoded against the village database for a more precise pin |
| **Provider** | Twilio Programmable SMS |
| **⚠️ Trial Constraints** | Twilio free trial limits: (1) SMS can only be sent to a **maximum of 5 pre-verified phone numbers**, (2) custom message bodies may be restricted to templates, (3) all messages are prefixed with "Sent from your Twilio trial account." **For the demo:** Pre-verify all team members' numbers during Phase 0. Acknowledge the 5-number limit in the presentation. To remove limits, upgrade the account (~$20 to load funds). |

#### F5: IVR Voice Call Alerts
| Attribute | Detail |
|-----------|--------|
| **Description** | For critical red-zone alerts, the system makes an automated phone call to registered numbers, playing a pre-generated Assamese voice message |
| **TTS Engine** | **Bhashini API** (Indian Government's language platform — confirmed Assamese TTS support). Fallback: AI4Bharat Indic-Parler-TTS (open-source). ⚠️ Google Cloud TTS does **NOT** support Assamese as of Aug 2026. |
| **Call Flow** | System generates alert text → Bhashini TTS converts to Assamese audio file → Twilio Voice API places the call and plays the audio |

### 5.2 Priority 2 — Should Have (Differentiators)

#### F6: AI Query Interface ("Gov-GPT")
| Attribute | Detail |
|-----------|--------|
| **Description** | A chat/search bar on the dashboard where officials type natural-language questions |
| **Example Queries** | "Which villages near Dhubri are at risk?", "Where are the most SOS signals coming from?", "Suggest a safe zone for 500 people near Majuli" |
| **Implementation** | Pass the current state of the map data (JSON of villages, risk scores, SOS pins) as context to the LLM API along with the user's question. Return the LLM's response in a chat bubble |
| **LLM Provider** | Gemini API (primary), Groq (fallback for speed), via OpenRouter or direct |

#### F7: Post-Flood Crop Damage & Advisory Portal
| Attribute | Detail |
|-----------|--------|
| **Description** | A simple page (or WhatsApp bot entry point) where a farmer uploads a photo of their flooded field |
| **AI Processing** | Photo is sent to Gemini Vision API with the system prompt: *"You are an agricultural expert in Assam. Identify the crop, estimate flood damage percentage, and provide 3 actionable recovery steps."* |
| **Output** | A results card showing: crop type, damage severity (%), and recovery advisory in both English and Assamese |
| **Fallback** | If image quality is too low, prompt the user to retake the photo |

#### F8: Survival Mode (Bandwidth-Aware Downgrader)
| Attribute | Detail |
|-----------|--------|
| **Description** | Client-side logic that detects network quality and adapts behavior |
| **Detection** | Uses the browser's `navigator.connection` API (or `navigator.onLine` as fallback) to detect effective connection type (4g, 3g, 2g, slow-2g, offline). **⚠️ Chromium-only — demo must use Chrome.** |
| **Behavior** | On 2G/slow-2g: disable map tiles, switch to text-only list of alerts. On offline: queue all outbound requests (SOS, reports) in IndexedDB and auto-retry via a client-side polling loop (`setInterval`) that checks `navigator.onLine` every 10 seconds |
| **Visual Indicator** | A banner at the top of the app showing current mode: "Full Mode", "Low-Bandwidth Mode", or "Offline — Messages Queued" |

#### F9: Natural-Language Risk Alert Generation
| Attribute | Detail |
|-----------|--------|
| **Description** | Instead of sending raw data in SMS, the LLM converts model output into a human-readable, urgent but calm alert message. This should be built into the SMS/IVR flow from the start (F4/F5), not bolted on later. |
| **Example** | Input: `{village: "Majuli", risk: 0.92, hours: 18}` → Output: "⚠️ Warning: Majuli is at high risk of flooding within 18 hours. Please move to higher ground immediately. Nearest safe zone: Kamalabari Hill (3.2 km north)." |

### 5.3 Priority 3 — Nice to Have

#### F10: Anomaly Detection
| Attribute | Detail |
|-----------|--------|
| **Description** | Compares incoming river-level data against historical averages for the same date. If the current reading deviates by more than 2 standard deviations, trigger an early-warning flag before the main prediction engine would |
| **Implementation** | Simple statistical check (z-score) against a CSV of historical monthly averages |

---

## 6. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | Dashboard map should load within 3 seconds on a local machine. API responses should return within 500ms (excluding LLM calls, which may take 2–5s) |
| **Reliability** | Survival Mode must gracefully handle total network loss without crashing. Queued messages must persist across browser refreshes (IndexedDB) |
| **Security** | API keys (Twilio, Gemini, Bhashini) must not be hardcoded in frontend code. Use `.env` files on the backend. No user authentication required for hackathon scope |
| **Accessibility** | Dashboard must be usable on a standard laptop screen (1366x768 minimum). SMS/IVR must work on any phone (smartphone or basic) |
| **Localization** | All user-facing SMS and IVR content must be in Assamese. Dashboard UI in English with Assamese labels for geographic features |
| **Data Privacy** | Phone numbers collected for SMS/IVR are stored locally in SQLite. No data leaves the local machine except via Twilio API calls, LLM API calls, and Bhashini API calls |
| **CORS** | FastAPI backend must include CORS middleware allowing requests from `http://localhost:3000` (Next.js dev server) |

### 6.1 Error Handling & Fallbacks

| Feature | Failure Scenario | Fallback Behavior |
|---------|-------------------|--------------------|
| F2: Flood Prediction | GeoJSON file fails to load | Show last-known-good prediction state with a "Data Stale" warning banner |
| F4: SMS Outbound | Twilio API returns error (rate limit, auth failure) | Log the error, show a toast notification on the dashboard: "SMS delivery failed — retry?" |
| F4: SOS Parsing | LLM returns malformed JSON or hallucinated data | Store the raw SMS text as-is in `sos_messages.raw_text`, place the SOS pin at the farmer's registered village centroid, flag as "Unparsed — needs manual review" |
| F5: IVR Call | Bhashini TTS API is down | Fall back to sending a plain-text SMS instead of a voice call |
| F6: AI Query | LLM API times out or returns irrelevant answer | Display: "I couldn't process that query. Try rephrasing, or view the map directly." with a 10-second timeout |
| F7: Crop Assessment | Gemini Vision returns low-confidence result or cannot identify crop | Display: "We couldn't confidently assess this image. Please retake in better lighting, or describe your crop manually." |
| F8: Survival Mode | `navigator.connection` API not available (non-Chrome browser) | Degrade to `navigator.onLine` (boolean online/offline only — no 2G/3G/4G granularity) |
| All external APIs | Network timeout | All LLM/Twilio/Bhashini calls use a 10-second timeout. On failure, retry once, then surface the error to the UI. |

---

## 7. User Journeys

### Journey 1: Government Official Monitors Flood Risk
```
1. Official opens the AFIP dashboard on their laptop browser
2. The map loads showing 2-3 Brahmaputra districts with current flood-risk zones
3. Red zones are clearly visible — official clicks on one to see affected villages
4. Official types into the AI Query bar: "Which villages will flood in the next 24 hours?"
5. The system responds conversationally with a ranked list
6. Official clicks "Send Alert" on a critical village — SMS and IVR calls go out
7. Within minutes, inbound SOS replies from farmers appear as pins on the map
8. Official uses the safe-zone layer to identify the best camp location nearby
```

### Journey 2: Rural Farmer Receives Warning and Sends SOS
```
1. Farmer Bimal receives an automated phone call in Assamese:
   "Warning: Your village Majuli is at high risk of flooding within 18 hours.
    Please move livestock to higher ground. Nearest safe zone: Kamalabari Hill."
2. Bimal moves his cattle and harvests what he can
3. 12 hours later, water starts rising faster than expected
4. Bimal replies to the SMS he received earlier: "Pani ghor bhitor ahise, 4 jon ase"
   (Water entered house, 4 people here)
5. The system parses this via LLM, creates an SOS pin on the dashboard
6. An NGO coordinator sees the pin and dispatches a boat
```

### Journey 3: Farmer Assesses Crop Damage Post-Flood
```
1. After waters recede, farmer Dipika opens the AFIP web app on her Android phone
2. She taps "Upload Crop Photo" and takes a picture of her waterlogged paddy field
3. The system sends the photo to Gemini Vision API
4. Within seconds, a result card appears:
   "Crop: Paddy (Rice) | Damage: ~70% submergence rot |
    Advisory: 1) Drain standing water immediately, 2) Apply potash fertilizer,
    3) Consider re-sowing short-duration Sali rice variety"
5. The same advisory is available in Assamese
```

### Journey 4: System Enters Survival Mode
```
1. During peak flooding, the cellular tower near an NGO coordinator degrades to 2G
2. The AFIP dashboard detects the weak connection via navigator.connection API
3. A yellow banner appears: "Low-Bandwidth Mode — Map tiles disabled"
4. The dashboard switches to a text-only list view of alerts and SOS pins
5. The coordinator submits a supply request — it is queued in IndexedDB
6. 20 minutes later, signal briefly strengthens — the queued request fires automatically
7. A green notification appears: "3 queued messages sent successfully"
```

---

## 8. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ Map View │  │ AI Chat  │  │ Crop     │  │ Survival    │ │
│  │(Leaflet) │  │ (Query)  │  │ Upload   │  │ Mode Logic  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘ │
│       │              │             │               │        │
│       └──────────────┴─────────────┴───────────────┘        │
│                          │  REST API calls                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND (Python FastAPI)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ Flood    │  │ Safe     │  │ Alert    │  │ Crop Vision │  │
│  │ Predict  │  │ Zone     │  │ Service  │  │ Service     │  │
│  │ Engine   │  │ Ranker   │  │(Twilio)  │  │(Gemini VLM) │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘  │
│       │              │             │               │         │
│  ┌────┴──────────────┴─────────────┴───────────────┴──────┐  │
│  │                    SQLite Database                      │  │
│  │  villages | safe_zones | alerts_log | sos_messages      │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Twilio   │ │ Gemini / │ │ Bhashini │
        │ SMS/Voice│ │ Groq API │ │ TTS API  │
        └──────────┘ └──────────┘ └──────────┘
```

---

## 9. Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js (React) | Team preference; SSR capabilities; easy API routes |
| **Mapping** | Leaflet.js + OpenStreetMap tiles | Free, open-source, lightweight, no API key needed |
| **Backend** | Python + FastAPI (with CORS middleware) | Team's strongest language; excellent for data processing and ML |
| **Database** | SQLite | Zero-setup, file-based, perfect for local demo |
| **Elevation Data** | Pre-processed GeoJSON (derived from NASA SRTM) | Avoids heavy raster processing at runtime |
| **LLM (Text)** | Gemini API (primary), Groq (fallback) | Free tiers available; fast inference |
| **LLM (Vision)** | Gemini Vision API | Handles crop photo analysis without custom model training |
| **SMS/Voice** | Twilio Programmable SMS + Voice | Industry standard; trial limited to 5 verified numbers |
| **TTS (Assamese)** | Bhashini API (primary), AI4Bharat Indic-Parler-TTS (fallback) | Google Cloud TTS does NOT support Assamese. Bhashini is free and government-backed. |
| **Flood Prediction** | Rule-based threshold logic (Python) | Realistic for hackathon scope; swappable for ML model later |

---

## 10. Data Requirements

| Data | Source | Format | Pre-processing Needed |
|------|--------|--------|-----------------------|
| Village locations & names | OpenStreetMap / manual GeoJSON | GeoJSON | Extract villages for target districts |
| Elevation per village | NASA SRTM DEM (30m resolution) | GeoTIFF → GeoJSON | Sample elevation at each village point using GDAL/Rasterio, export as JSON property |
| River water levels | Central Water Commission (CWC) | CSV/manual | For hackathon: use simulated data with realistic ranges |
| Rainfall forecasts | India Meteorological Department (IMD) | CSV/manual | For hackathon: use simulated data |
| Registered phone numbers | Manual seed data | SQLite table | Pre-populate with team members' numbers for demo |
| Historical flood patterns | ASDMA (Assam State Disaster Management Authority) | Reference only | Used to validate simulated scenarios |

---

## 11. Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Flood Prediction Accuracy** | Correctly identifies ≥80% of villages that would flood based on elevation logic | Compare output against known historical flood footprints |
| **Alert Delivery** | 100% of registered numbers receive SMS within 30 seconds of alert trigger | Twilio delivery logs |
| **SOS Parsing Accuracy** | LLM correctly extracts location + need from ≥90% of test SOS messages | Test with 20 sample messages (mix of English, Hindi, Assamese) |
| **Crop Assessment Quality** | Vision API provides relevant crop identification and damage estimate in ≥80% of test photos | Test with 10 sample flood-damaged crop images |
| **Query Interface Relevance** | AI returns a factually correct, data-backed answer for ≥80% of test queries | Test with 15 predefined questions |
| **Survival Mode** | App remains functional (text-only view + message queuing) when network is throttled to 2G or disabled | Manual testing: disable Wi-Fi, verify queued messages fire on reconnect |

---

## 12. API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/flood-zones` | Returns current flood-risk GeoJSON with risk scores |
| `GET` | `/api/safe-zones` | Returns ranked safe-zone locations as GeoJSON |
| `POST` | `/api/predict` | Triggers prediction recalculation with new river-level input |
| `POST` | `/api/alert/sms` | Sends SMS alert to all numbers in a given village/zone |
| `POST` | `/api/alert/ivr` | Triggers IVR voice call to specified numbers |
| `POST` | `/api/sms/webhook` | Twilio webhook — receives inbound SMS, parses via LLM, stores SOS |
| `GET` | `/api/sos` | Returns all active SOS messages for dashboard display |
| `POST` | `/api/query` | Accepts a natural-language question, returns AI-generated answer |
| `POST` | `/api/crop-assess` | Accepts an uploaded image, returns crop damage assessment |
| `GET` | `/api/villages` | Returns village metadata (name, elevation, population, district) |

---

## 13. Database Schema (SQLite)

```sql
-- Core village data with elevation and risk
CREATE TABLE villages (
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

-- Recommended safe zones
CREATE TABLE safe_zones (
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

-- Outbound alerts log
CREATE TABLE alerts_log (
    id INTEGER PRIMARY KEY,
    village_id INTEGER REFERENCES villages(id),
    alert_type TEXT CHECK(alert_type IN ('sms', 'ivr', 'both')),
    message_text TEXT,
    recipients_count INTEGER,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    twilio_status TEXT
);

-- Inbound SOS messages from farmers
CREATE TABLE sos_messages (
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

-- Crop damage assessments
CREATE TABLE crop_assessments (
    id INTEGER PRIMARY KEY,
    image_path TEXT NOT NULL,
    crop_type TEXT,
    damage_pct REAL,
    advisory_en TEXT,
    advisory_as TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Registered phone numbers for alerts
CREATE TABLE phone_registry (
    id INTEGER PRIMARY KEY,
    phone_number TEXT NOT NULL UNIQUE,
    village_id INTEGER REFERENCES villages(id),
    name TEXT,
    language_pref TEXT DEFAULT 'as' CHECK(language_pref IN ('en', 'as', 'bn'))
);

-- Simulated river level data
CREATE TABLE river_levels (
    id INTEGER PRIMARY KEY,
    station_name TEXT NOT NULL,
    current_level_m REAL NOT NULL,
    danger_level_m REAL NOT NULL,
    forecast_rise_m REAL DEFAULT 0.0,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 14. Timeline

This is a hackathon project — all work happens in a compressed sprint. The timeline below assumes the team works in parallel.

| Phase | Tasks | Owner |
|-------|-------|-------|
| **Phase 0: Setup (Hour 0–2)** | Initialize Next.js + FastAPI repos. Set up SQLite schema. Configure Twilio account. Get API keys (Gemini, Google Cloud TTS). Download and pre-process GeoJSON data for target districts. | Full team |
| **Phase 1: Core Map + Prediction (Hour 2–8)** | Build the Leaflet.js map dashboard with GeoJSON layers. Implement the flood prediction engine (rule-based). Implement safe-zone ranking algorithm. Seed SQLite with village data. | Frontend + Backend |
| **Phase 2: Alerts + SMS/IVR (Hour 8–14)** | Integrate Twilio SMS (outbound alerts). Set up Twilio webhook for inbound SOS. Implement LLM parsing of incoming SOS texts. Build IVR voice call flow with Google Cloud TTS. | Backend + AI |
| **Phase 3: AI Features (Hour 14–20)** | Build the AI Query Interface chat component. Implement crop photo upload + Gemini Vision integration. Add natural-language alert generation. | Frontend + AI |
| **Phase 4: Survival Mode + Polish (Hour 20–28)** | Implement bandwidth detection + IndexedDB queuing. Add bilingual Assamese labels and translations. UI polish — responsive layout, loading states, error handling. | Frontend |
| **Phase 5: Integration + Demo Prep (Hour 28–36)** | End-to-end testing of all user journeys. Fix bugs. Prepare demo script. Record backup demo video. | Full team |

---

## 15. Open Questions / Assumptions

| # | Item | Type | Status |
|---|------|------|--------|
| 1 | Which specific 2–3 districts along the Brahmaputra will be the demo scope? (Suggested: Dhubri, Majuli, Silchar) | Decision | **Open — team to decide** |
| 2 | Will CWC river-level data be simulated, or will the team attempt to scrape real data from the CWC website? | Decision | Assumed: **Simulated for hackathon** |
| 3 | Twilio free trial limits: outbound SMS to max 5 verified numbers, no custom message bodies, 30-day expiry. Team needs to verify all demo phone numbers during setup. Consider upgrading (~$20) to remove limits. | Constraint | **Must be done during setup** |
| 4 | ~~Google Cloud TTS Assamese voice quality may vary.~~ **RESOLVED:** Google Cloud TTS does NOT support Assamese. Replaced with Bhashini API (confirmed Assamese support). Register for Bhashini API keys before hackathon. | Risk | **Resolved — use Bhashini** |
| 5 | Gemini Vision API accuracy on flood-damaged crop photos is unvalidated. May need prompt tuning. | Risk | **Test in Phase 3** |
| 6 | The `navigator.connection` API for Survival Mode is Chromium-only (no Firefox/Safari). Demo must use Chrome. | Constraint | Assumed: **Chrome-only for demo** |
| 7 | Pre-processed GeoJSON for target districts needs to be prepared before the hackathon. Source: download SRTM tiles, process with GDAL, export village-level elevation data. | Prerequisite | **Must be done before hackathon** |
| 8 | Bhashini API registration and key acquisition must be completed before the hackathon. Portal: bhashini.gov.in | Prerequisite | **Must be done before hackathon** |

---

## 16. Pre-Hackathon Checklist

- [ ] **Decide target districts** (Dhubri, Majuli, Silchar recommended)
- [ ] **Download & process GeoJSON** — Get SRTM DEM tiles for target area, extract village elevations using GDAL/Rasterio, export as GeoJSON
- [ ] **Register for Bhashini API** — Get UlcaApiKey and InferenceApiKey from bhashini.gov.in
- [ ] **Set up Twilio account** — Create account, get phone number, verify 5 team member phone numbers for demo
- [ ] **Get Gemini API key** — From Google AI Studio (free tier)
- [ ] **Get Groq API key** — From console.groq.com (free tier, fallback LLM)
- [ ] **Seed village data** — Prepare a CSV/JSON of ~50–100 villages across target districts with: name, name_assamese, district, lat, lng, elevation_m, population_est
- [ ] **Collect 10 sample crop damage photos** — For testing Gemini Vision API prompt accuracy
- [ ] **Write 20 sample SOS messages** — Mix of English, Hindi, Assamese for testing LLM parsing
- [ ] **Test Bhashini Assamese TTS** — Generate a sample audio file and verify quality
