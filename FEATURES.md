# FEATURES.md — Assam Flood Intelligence Platform (AFIP)

> **Source:** [PRD.md](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/PRD.md) v2.0 (Post-Review)
> **Date:** 2026-08-16

---

## Product Overview

AFIP is a proactive disaster-management web application for the Assam floods. It predicts flooding 48 hours ahead using elevation + river-level data, recommends safe zones for relief camps, delivers inclusive warnings via SMS/IVR (including Assamese voice calls), provides AI-driven post-flood crop damage assessment, and gives government officials a natural-language query interface. Built for the Craft N Code 2026 hackathon.

---

## Summary

### Feature Count by Priority

| Priority | Count | IDs |
|----------|-------|-----|
| **Must Have** | 11 | F1, F2, F3, F4, F5, F11, F12, F13, F14, F15, F16 |
| **Should Have** | 7 | F6, F7, F8, F9, F17, F18, F19 |
| **Could Have** | 3 | F10, F20, F21 |
| **Won't Have** | 4 | F22, F23, F24, F25 |
| **Total** | 25 | |

### Feature Count by Category

| Category | Count | IDs |
|----------|-------|-----|
| **Map & Visualization** | 3 | F1, F11, F12 |
| **Prediction & Analysis** | 3 | F2, F3, F10 |
| **Alerting & Communication** | 5 | F4, F5, F9, F15, F16 |
| **AI & Intelligence** | 3 | F6, F17, F18 |
| **Crop Assessment** | 2 | F7, F19 |
| **Resilience & Offline** | 2 | F8, F14 |
| **Data & Backend** | 3 | F13, F20, F21 |
| **Out of Scope (Won't Have)** | 4 | F22, F23, F24, F25 |

---

## Must Have — Critical for Hackathon Demo

---

### Category: Map & Visualization

#### F1: Interactive Flood-Risk Map
| Attribute | Detail |
|-----------|--------|
| **Description** | Leaflet.js map showing target districts with color-coded flood-risk zones: red (predicted flood in 48h), yellow (moderate risk), green (safe zone) |
| **Personas** | Commander Priya (official), Volunteer Rahul (NGO) |
| **Acceptance Criteria** | (1) Map loads within 3 seconds, (2) clicking a zone reveals village name, elevation, population, risk score, (3) zoom/pan works smoothly, (4) at least 3 toggleable layers: flood zones, safe zones, SOS pins |
| **Technical Constraints** | Leaflet.js + OpenStreetMap tiles (no API key needed). GeoJSON polygons pre-processed from NASA SRTM DEM |
| **Edge Cases** | GeoJSON fails to load → show "Data Stale" warning banner with last-known-good state (PRD §6.1) |
| **Complexity** | Medium |
| **Dependencies** | Pre-processed GeoJSON data (pre-hackathon prerequisite) |

#### F11: Bilingual Map Labels
| Attribute | Detail |
|-----------|--------|
| **Description** | All village names and geographic features on the map display both English and Assamese labels |
| **Personas** | All dashboard users |
| **Acceptance Criteria** | (1) Village popups show name in English and Assamese, (2) Assamese names sourced from `villages.name_assamese` column |
| **Technical Constraints** | Requires Assamese text in seed data. Font rendering must support Assamese Unicode script |
| **Edge Cases** | Missing Assamese name → fall back to English-only display |
| **Complexity** | Low |
| **Dependencies** | F1, seed data with `name_assamese` field |

#### F12: SOS Pin Display on Map
| Attribute | Detail |
|-----------|--------|
| **Description** | Incoming SOS messages from farmers appear as distinct markers (pins) on the dashboard map in real-time |
| **Personas** | Commander Priya, Volunteer Rahul |
| **Acceptance Criteria** | (1) SOS pins appear within 5 seconds of inbound SMS processing, (2) clicking a pin shows raw message, parsed needs, people count, and timestamp, (3) pins are visually distinct from flood-zone and safe-zone markers, (4) pins can be filtered by status (active/acknowledged/resolved) |
| **Technical Constraints** | Frontend polls `GET /api/sos` endpoint at a regular interval (e.g., every 10 seconds) |
| **Edge Cases** | Many SOS pins in same village → cluster markers to avoid visual clutter |
| **Complexity** | Medium |
| **Dependencies** | F1, F4 (inbound SMS) |

---

### Category: Prediction & Analysis

#### F2: 48-Hour Flood Forecasting Engine
| Attribute | Detail |
|-----------|--------|
| **Description** | Backend service that calculates which villages will be submerged based on current river water level + forecast rise + village elevation |
| **Personas** | Commander Priya (consumes output via dashboard) |
| **Acceptance Criteria** | (1) Given simulated river-level input, the engine returns updated risk scores for all villages within 500ms, (2) villages where `river_level + forecast_rise > village_elevation` are marked as high-risk (red), (3) output is valid GeoJSON consumable by F1 |
| **Technical Constraints** | Rule-based threshold logic in Python. No ML training. Uses `POST /api/predict` endpoint |
| **Edge Cases** | All villages above flood level → all green (no red zones). All villages below flood level → extreme scenario, verify UI handles 100% red gracefully |
| **Complexity** | Low |
| **Dependencies** | Pre-processed GeoJSON, simulated river-level data |

#### F3: Dynamic Safe-Zone Recommendation
| Attribute | Detail |
|-----------|--------|
| **Description** | Algorithm that identifies and ranks the safest high-ground locations for relief camps near at-risk villages |
| **Personas** | Commander Priya |
| **Acceptance Criteria** | (1) Safe zones appear as green markers on the map, (2) each safe zone shows a score breakdown card: elevation (40%), road access (25%), distance from river (20%), capacity (15%), (3) rankings update when prediction data changes |
| **Technical Constraints** | Formula: `SafeScore = (Elevation * 0.4) + (RoadAccess * 0.25) + (DistanceFromRiver * 0.2) + (Capacity * 0.15)`. RoadAccess and Capacity are seeded as static values in `safe_zones` table |
| **Edge Cases** | No safe zone within reasonable distance of a red village → flag as "No nearby safe zone — requires airlift" |
| **Complexity** | Medium |
| **Dependencies** | F2, seeded `safe_zones` table data |

---

### Category: Alerting & Communication

#### F4: Outbound SMS Alerts (Twilio)
| Attribute | Detail |
|-----------|--------|
| **Description** | When a village enters the red zone, the system sends an SMS alert in Assamese to all registered phone numbers linked to that village |
| **Personas** | Kisan Bimal (flip-phone farmer), Kisan Dipika (smartphone farmer) |
| **Acceptance Criteria** | (1) SMS is sent within 30 seconds of alert trigger, (2) message is in Assamese, (3) message contains village name, risk level, and nearest safe zone, (4) delivery status is logged in `alerts_log` table |
| **Technical Constraints** | Twilio Programmable SMS. ⚠️ Trial: max 5 pre-verified numbers, messages prefixed with "Sent from your Twilio trial account." Upgrade to paid (~$20) to remove limits |
| **Edge Cases** | Twilio API error → log error, show toast on dashboard: "SMS delivery failed — retry?" (PRD §6.1) |
| **Complexity** | Medium |
| **Dependencies** | F2 (triggers alerts), F9 (generates human-readable message text), phone_registry seed data |

#### F5: IVR Voice Call Alerts (Bhashini + Twilio)
| Attribute | Detail |
|-----------|--------|
| **Description** | For critical red-zone alerts, the system makes an automated phone call playing a pre-generated Assamese voice message |
| **Personas** | Kisan Bimal (flip-phone, low-literacy) |
| **Acceptance Criteria** | (1) Alert text is converted to Assamese audio via Bhashini TTS API, (2) Twilio Voice API places the call and plays the audio, (3) call is logged in `alerts_log` |
| **Technical Constraints** | ⚠️ Google Cloud TTS does NOT support Assamese. Must use Bhashini API. Fallback: AI4Bharat Indic-Parler-TTS. Same Twilio trial constraints as F4 |
| **Edge Cases** | Bhashini TTS API down → fall back to plain-text SMS instead of voice call (PRD §6.1) |
| **Complexity** | High |
| **Dependencies** | F4 (shares Twilio infra), F9 (alert text generation), Bhashini API registration |

#### F15: Inbound SMS SOS Reception & Parsing
| Attribute | Detail |
|-----------|--------|
| **Description** | Farmers reply to alert SMS with free-text messages. Twilio webhook receives the message, an LLM parses it into structured data `{location, people_count, needs}`, and it is stored as an SOS record |
| **Personas** | Kisan Bimal, Kisan Dipika (sending SOS), Commander Priya (viewing SOS on dashboard) |
| **Acceptance Criteria** | (1) Twilio webhook (`POST /api/sms/webhook`) receives the inbound SMS, (2) LLM extracts location, people count, and needs from the raw text, (3) SOS is stored in `sos_messages` table with parsed fields, (4) SOS pin is placed on map at farmer's registered village centroid |
| **Technical Constraints** | SMS contains no GPS. Geolocation resolved via `phone_registry.village_id → villages.lat/lng`. If LLM extracts a place name, geocode against village DB for more precise pin |
| **Edge Cases** | LLM returns malformed JSON → store raw text as-is, pin at village centroid, flag as "Unparsed — needs manual review" (PRD §6.1) |
| **Complexity** | High |
| **Dependencies** | F4 (Twilio setup), F12 (map display), LLM API |

#### F16: SOS Status Management
| Attribute | Detail |
|-----------|--------|
| **Description** | Dashboard users can update the status of incoming SOS messages: active → acknowledged → resolved |
| **Personas** | Commander Priya, Volunteer Rahul |
| **Acceptance Criteria** | (1) Each SOS pin/card has status buttons (Acknowledge, Resolve), (2) status change is persisted to `sos_messages.status`, (3) resolved SOS pins are visually dimmed or hidden from default view |
| **Technical Constraints** | Requires a `PATCH /api/sos/{id}` endpoint (not yet in PRD API list — implicit requirement) |
| **Edge Cases** | Duplicate SOS from same number → show both but flag as potential duplicate |
| **Complexity** | Low |
| **Dependencies** | F15, F12 |

---

### Category: Data & Backend

#### F13: SQLite Database & Schema Setup
| Attribute | Detail |
|-----------|--------|
| **Description** | Initialize SQLite database with 7 tables: `villages`, `safe_zones`, `alerts_log`, `sos_messages`, `crop_assessments`, `phone_registry`, `river_levels` |
| **Personas** | N/A (infrastructure) |
| **Acceptance Criteria** | (1) All 7 tables created per PRD §13 schema, (2) seed data loaded for villages (~50–100 records), safe zones, and phone registry (5 team numbers), (3) simulated river-level data seeded |
| **Technical Constraints** | SQLite file-based, zero external setup. Schema must match PRD §13 exactly |
| **Edge Cases** | DB file corruption → provide a reset script that rebuilds the schema from scratch |
| **Complexity** | Low |
| **Dependencies** | Pre-hackathon seed data preparation |

#### F14: FastAPI Backend with CORS
| Attribute | Detail |
|-----------|--------|
| **Description** | Python FastAPI server exposing 10 REST endpoints (PRD §12), with CORS middleware configured for `http://localhost:3000` |
| **Personas** | N/A (infrastructure) |
| **Acceptance Criteria** | (1) All 10 endpoints from PRD §12 are implemented and respond correctly, (2) CORS allows Next.js frontend requests, (3) API keys loaded from `.env` file — never hardcoded |
| **Technical Constraints** | Must include `fastapi.middleware.cors.CORSMiddleware`. All external API calls (Twilio, Gemini, Bhashini) use 10-second timeouts |
| **Edge Cases** | Missing `.env` file → server should fail fast with a clear error message listing required keys |
| **Complexity** | Medium |
| **Dependencies** | F13 (database) |

---

## Should Have — Differentiators

---

### Category: AI & Intelligence

#### F6: AI Query Interface ("Gov-GPT")
| Attribute | Detail |
|-----------|--------|
| **Description** | Chat/search bar on the dashboard where officials type natural-language questions about flood data |
| **Personas** | Commander Priya |
| **Acceptance Criteria** | (1) Chat bar is visible on the dashboard, (2) query is sent to `POST /api/query`, (3) backend passes current map state (villages JSON, risk scores, SOS data) as context to LLM, (4) LLM response appears in a chat bubble within 5 seconds, (5) example queries work: "Which villages near Dhubri are at risk?", "Where are the most SOS signals?" |
| **Technical Constraints** | Gemini API (primary), Groq (fallback). Context window must fit all village + SOS data — may need to summarize if dataset is large |
| **Edge Cases** | LLM times out → display: "I couldn't process that query. Try rephrasing, or view the map directly." (PRD §6.1). Judge spams queries → consider basic client-side rate limiting (1 query per 3 seconds) |
| **Complexity** | Medium |
| **Dependencies** | F14 (API), F2 (flood data), F15 (SOS data) |

#### F17: LLM-Based SOS Text Parsing
| Attribute | Detail |
|-----------|--------|
| **Description** | The LLM component that takes raw free-text SOS messages (potentially in Assamese, Hindi, or English) and extracts structured fields: location, people_count, needs |
| **Personas** | N/A (backend service consumed by F15) |
| **Acceptance Criteria** | (1) Correctly extracts data from ≥90% of 20 test SOS messages (mix of languages), (2) returns valid JSON, (3) handles messages with missing fields gracefully (e.g., no location mentioned → return null) |
| **Technical Constraints** | System prompt must instruct the LLM to return strict JSON. Use `json_mode` or structured output if available |
| **Edge Cases** | Assamese text with no clear location → return `{location: null}` and fall back to village centroid. Completely irrelevant text (spam) → return `{is_sos: false}` |
| **Complexity** | Low |
| **Dependencies** | LLM API key |

#### F18: Assamese Translation Layer
| Attribute | Detail |
|-----------|--------|
| **Description** | Translates English alert text and crop advisory into Assamese for SMS/IVR delivery and crop assessment output |
| **Personas** | Kisan Bimal, Kisan Dipika |
| **Acceptance Criteria** | (1) Crop assessment results (F7) are displayed in both English and Assamese, (2) alert messages (F9) are generated in Assamese |
| **Technical Constraints** | Can use LLM for translation, or Bhashini Translation API (confirmed Assamese support) |
| **Edge Cases** | Translation quality for agricultural terms may be poor → pre-build a small glossary of common Assamese agricultural terms to include in the LLM prompt |
| **Complexity** | Low |
| **Dependencies** | Bhashini API or LLM API |

---

### Category: Crop Assessment

#### F7: Crop Damage Photo Upload & AI Assessment
| Attribute | Detail |
|-----------|--------|
| **Description** | A page where farmers upload a photo of their flooded field. Gemini Vision API identifies the crop, estimates damage percentage, and provides 3 recovery steps |
| **Personas** | Kisan Dipika (smartphone farmer) |
| **Acceptance Criteria** | (1) Upload page accepts image from camera or gallery, (2) image is sent to `POST /api/crop-assess`, (3) results card shows: crop type, damage %, 3 advisory steps, (4) results displayed in both English and Assamese, (5) ≥80% accuracy on 10 test photos |
| **Technical Constraints** | Gemini Vision API with system prompt: "You are an agricultural expert in Assam…" Image should be compressed client-side before upload (max 5MB) |
| **Edge Cases** | Low-quality image → prompt user to retake. Non-crop image (e.g., selfie) → return "This doesn't appear to be a crop photo." (PRD §6.1) |
| **Complexity** | Medium |
| **Dependencies** | F14 (API), F18 (Assamese translation), Gemini Vision API key |

---

### Category: Resilience & Offline

#### F8: Survival Mode (Bandwidth Detection & Downgrading)
| Attribute | Detail |
|-----------|--------|
| **Description** | Client-side logic that detects network quality and adapts the UI — disabling map tiles on 2G, queuing messages when offline |
| **Personas** | Volunteer Rahul (weak signal in the field) |
| **Acceptance Criteria** | (1) Banner shows current mode: "Full Mode", "Low-Bandwidth Mode", or "Offline — Messages Queued", (2) on 2G: map tiles disabled, text-only alert list shown, (3) on offline: requests queued in IndexedDB, (4) queued requests fire automatically when connection returns, (5) queued messages persist across browser refresh |
| **Technical Constraints** | ⚠️ `navigator.connection` is Chromium-only. Demo must use Chrome. Fallback: `navigator.onLine` (boolean only). Retry loop: `setInterval` checking `navigator.onLine` every 10 seconds |
| **Edge Cases** | Browser doesn't support `navigator.connection` → degrade to online/offline only (PRD §6.1). IndexedDB full → show warning |
| **Complexity** | High |
| **Dependencies** | F1 (map), F14 (API) |

---

### Category: Alerting & Communication

#### F9: Natural-Language Risk Alert Generation
| Attribute | Detail |
|-----------|--------|
| **Description** | LLM converts raw prediction data into human-readable, urgent-but-calm alert messages for SMS/IVR |
| **Personas** | Kisan Bimal, Kisan Dipika (receive the alert) |
| **Acceptance Criteria** | (1) Input: `{village, risk_score, hours, nearest_safe_zone}` → Output: a natural-language warning message, (2) message includes village name, timeframe, and nearest safe zone with distance, (3) tone is urgent but not panic-inducing |
| **Technical Constraints** | Single LLM API call per alert. Should be built into the F4/F5 flow from the start |
| **Edge Cases** | LLM returns overly long message → truncate to 160 chars for SMS (SMS segment limit) |
| **Complexity** | Low |
| **Dependencies** | F2 (prediction data), F3 (safe zone data), LLM API |

---

### Category: Crop Assessment

#### F19: Crop Assessment History
| Attribute | Detail |
|-----------|--------|
| **Description** | Store all crop assessments in `crop_assessments` table so they can be reviewed later |
| **Personas** | Kisan Dipika, Commander Priya (for aggregate damage reports) |
| **Acceptance Criteria** | (1) Each assessment is persisted with image path, crop type, damage %, advisory text (EN + AS), and timestamp, (2) assessments can be retrieved via API |
| **Technical Constraints** | Images stored locally on the server filesystem. Metadata in SQLite |
| **Edge Cases** | Disk space limits for stored images → implement a max storage cap or warn when disk is low |
| **Complexity** | Low |
| **Dependencies** | F7, F13 |

---

## Could Have — Desirable, Can Be Deferred

---

### Category: Prediction & Analysis

#### F10: Anomaly Detection (Statistical Early Warning)
| Attribute | Detail |
|-----------|--------|
| **Description** | Compares incoming river-level data against historical averages. If the reading deviates by >2 standard deviations, triggers an early-warning flag before the main prediction engine |
| **Personas** | Commander Priya |
| **Acceptance Criteria** | (1) Z-score calculated against CSV of historical monthly averages, (2) anomaly flag appears on dashboard when z > 2, (3) flag includes: "River level is unusually high for this date — X standard deviations above average" |
| **Technical Constraints** | ~5 lines of Python. Requires a CSV of historical monthly river-level averages (can be manually created from public data) |
| **Edge Cases** | No historical data for current date → skip anomaly check, log warning |
| **Complexity** | Low |
| **Dependencies** | F2, historical data CSV |

---

### Category: Data & Backend

#### F20: River Level Simulation Controls
| Attribute | Detail |
|-----------|--------|
| **Description** | A dashboard control panel that allows the demo operator to manually adjust simulated river levels and trigger re-prediction |
| **Personas** | Demo operator (team member during presentation) |
| **Acceptance Criteria** | (1) Slider or input field for each river station's current level and forecast rise, (2) "Recalculate" button triggers `POST /api/predict`, (3) map updates in real-time after recalculation |
| **Technical Constraints** | Simple form component on the dashboard. Updates `river_levels` table then triggers F2 |
| **Edge Cases** | Unrealistic values entered → clamp to valid ranges |
| **Complexity** | Low |
| **Dependencies** | F2, F14 |

#### F21: Request Logging & Diagnostics
| Attribute | Detail |
|-----------|--------|
| **Description** | Basic server-side logging of all API requests, external API calls, and errors for debugging during the demo |
| **Personas** | Dev team (debugging) |
| **Acceptance Criteria** | (1) All FastAPI requests logged with timestamp, method, path, status code, (2) all external API calls (Twilio, Gemini, Bhashini) logged with response time and status, (3) logs written to a file or stdout |
| **Technical Constraints** | Python `logging` module. FastAPI middleware for request logging |
| **Edge Cases** | Log file grows too large → rotate or cap at 10MB |
| **Complexity** | Low |
| **Dependencies** | F14 |

---

## Won't Have — Out of Scope for Hackathon

---

#### F22: Real ML Model Training [WON'T HAVE]
| Attribute | Detail |
|-----------|--------|
| **Description** | Training LSTM, GNN, or other deep learning models for actual hydrological flood prediction |
| **Reason for Exclusion** | Requires years of historical data, GPU compute, and weeks of iteration. Impossible in a hackathon. Rule-based logic (F2) serves as a viable proxy |

#### F23: Native Mobile App [WON'T HAVE]
| Attribute | Detail |
|-----------|--------|
| **Description** | Android/iOS native application |
| **Reason for Exclusion** | Web app is sufficient for demo. Mobile-responsive web UI covers smartphone users. SMS/IVR covers non-smartphone users |

#### F24: Offline P2P Mesh Networking [WON'T HAVE]
| Attribute | Detail |
|-----------|--------|
| **Description** | BLE/Wi-Fi Direct peer-to-peer communication between phones when cellular towers are down |
| **Reason for Exclusion** | Extremely high complexity (8/10). Requires physical device testing. Was considered and deliberately cut in favor of Survival Mode (F8) which achieves similar resilience goals with far less effort |

#### F25: User Authentication & RBAC [WON'T HAVE]
| Attribute | Detail |
|-----------|--------|
| **Description** | Login system with role-based access control (admin, official, NGO, farmer) |
| **Reason for Exclusion** | Not needed for a local hackathon demo. All users access the same dashboard. Post-hackathon concern |

---

## Dependency Graph (Critical Path)

```
Pre-Hackathon Data Prep
         │
         ▼
   F13 (DB Schema)
         │
         ▼
   F14 (FastAPI + CORS)
      │         │
      ▼         ▼
   F2 (Predict) F4 (SMS Out)──► F5 (IVR)
      │              │
      ▼              ▼
   F3 (Safe Zone)  F15 (SMS In)──► F17 (LLM Parse)
      │              │
      ▼              ▼
   F1 (Map)◄────► F12 (SOS Pins)
      │
      ▼
   F11 (Bilingual Labels)
   F6 (Gov-GPT)
   F7 (Crop Upload)──► F19 (History)
   F8 (Survival Mode)
   F9 (Alert Text Gen)──► F4, F5
   F10 (Anomaly Detection)
```

**Critical path:** Data Prep → F13 → F14 → F2 → F3 → F1 → F12 (this chain must be completed first before anything else can be demoed).

---

## Third-Party Integration Summary

| Service | Features Using It | API Key Required | Free Tier | Pre-Hackathon Setup |
|---------|-------------------|------------------|-----------|---------------------|
| **Twilio** | F4, F5, F15, F16 | Yes | Yes (5 verified numbers) | Create account, buy number, verify 5 phones |
| **Gemini API** | F6, F7, F9, F17, F18 | Yes | Yes (free tier) | Get key from Google AI Studio |
| **Groq** | F6 (fallback) | Yes | Yes (free tier) | Get key from console.groq.com |
| **Bhashini API** | F5, F18 | Yes | Yes (free, gov-backed) | Register at bhashini.gov.in |
| **OpenStreetMap** | F1 | No | Yes (fully free) | None |
| **NASA SRTM** | F2 (pre-processed) | No | Yes (public data) | Download tiles, process with GDAL |

---

## Self-Check Results

1. **Summary table recount:** Must Have: F1, F2, F3, F4, F5, F11, F12, F13, F14, F15, F16 = **11**. Should Have: F6, F7, F8, F9, F17, F18, F19 = **7**. Could Have: F10, F20, F21 = **3**. Won't Have: F22, F23, F24, F25 = **4**. Total = **25**. ✅ Matches summary table.
2. **Category recount:** Map & Visualization: F1, F11, F12 = 3. Prediction & Analysis: F2, F3, F10 = 3. Alerting & Communication: F4, F5, F9, F15, F16 = 5. AI & Intelligence: F6, F17, F18 = 3. Crop Assessment: F7, F19 = 2. Resilience & Offline: F8, F14 = 2. Data & Backend: F13, F20, F21 = 3. Out of Scope: F22, F23, F24, F25 = 4. Total = **25**. ✅ Matches summary table.
3. **Cross-reference check:** All feature IDs are unique (F1–F25, no gaps, no duplicates). PRD feature IDs F1–F10 are preserved with identical meanings. F11–F25 are new features extracted from implicit PRD requirements. Dependency references (e.g., "F9 generates text for F4/F5") are verified correct. PRD §6.1 fallback references in edge cases all point to the correct feature.
4. **Inter-table consistency:** Priority table IDs match category table IDs. No feature appears in two priority levels. No feature appears in two categories.
5. **ID permanence:** No existing IDs were renumbered. F1–F10 retain their PRD meanings exactly. F11–F25 are new decompositions.

**Status:** Self-check complete. No inconsistencies found.
