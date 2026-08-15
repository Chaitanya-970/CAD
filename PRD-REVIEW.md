# PRD Review: Assam Flood Intelligence Platform (AFIP)

> **Product Type Classified:** Web App
> **Checks Skipped:** Library/SDK concerns (semver, peer-deps, bundle size, tree-shaking, types quality, public/internal boundary, mutation of caller-owned data) — not applicable.
> **Existing Implementation:** None. Built from scratch for hackathon. No code to diff against.

---

## Overall Assessment

The PRD is well-structured, technically detailed, and genuinely implementation-ready — unusual for a hackathon document. The user journeys, API endpoints, and database schema are strong enough that a developer could start coding immediately. However, **Step 0 (grounding in reality) revealed three factual errors** in the tech stack that would have caused painful debugging during the hackathon. The Twilio and TTS assumptions are wrong for the stated use case.

---

## Step 0: Technology Verification Results

### 🔴 CRITICAL: Google Cloud TTS Does NOT Support Assamese
- **PRD Claim (Section 9, F5):** "Google Cloud Text-to-Speech (Assamese) — Native Assamese voice support"
- **Reality:** Assamese is **not a supported language** in Google Cloud TTS as of August 2026. Google Cloud TTS supports Hindi, Bengali, Tamil, Telugu, and other Indian languages, but not Assamese.
- **Fix:** Replace with **Bhashini API** (Indian Government's language platform), which **does** support Assamese TTS. Bhashini is free, has developer API access, and provides Assamese voices. Alternatively, use **AI4Bharat Indic-Parler-TTS** (open-source).

### 🔴 CRITICAL: Twilio Free Trial Has Severe Limitations for This Demo
- **PRD Claim (Section 5, F4):** "Twilio Programmable SMS (free trial account)" with two-way SMS.
- **Reality:** Twilio free trial accounts:
  - Can only send SMS to a **maximum of 5 verified phone numbers** (not arbitrary farmers).
  - **Cannot send custom message bodies** during trial — restricted to pre-defined templates.
  - All messages are prefixed with "Sent from your Twilio trial account."
  - Trial expires after **30 days**.
  - India-specific: No Alphanumeric Sender ID, no DLT registration on trial.
- **Impact:** The "two-way SMS" demo will only work with 5 pre-verified team member numbers. The demo must acknowledge this constraint explicitly.
- **Fix:** Either (a) upgrade to a paid Twilio account (~$20 to load funds), or (b) explicitly scope the demo to 5 verified numbers and state it in the presentation.

### 🟡 WARNING: navigator.connection API Claim is Accurate but Incomplete
- **PRD Claim (Section 5, F8):** Uses `navigator.connection` with `navigator.onLine` as fallback.
- **Reality:** Confirmed — `navigator.connection` is Chromium-only (no Firefox, no Safari). The PRD already notes "Chrome-only for demo" in Open Questions, which is correct. However, F8's description should explicitly state the Chrome requirement in the feature spec itself, not just in a footnote.

### ✅ VERIFIED: Claims That Check Out
- Leaflet.js + OpenStreetMap: Free, no API key needed — **Correct**.
- NASA SRTM DEM data: Publicly available, 30m resolution — **Correct**.
- Gemini Vision API: Supports image analysis with text prompts — **Correct**.
- FastAPI + SQLite: Zero-setup, suitable for local demo — **Correct**.
- Bhashini API for Assamese: Supported, free developer access — **Correct** (this is the fix, not the original claim).

### ⚠️ UNVERIFIED: Claims I Could Not Confirm
- "Central Water Commission (CWC)" data availability in machine-readable format — the PRD already marks this as simulated, which is appropriate.
- "ASDMA (Assam State Disaster Management Authority)" historical flood patterns — referenced as "Reference only," not a hard dependency. Acceptable.

---

## Step 1: Gap Analysis

### HIGH Impact Gaps

| # | Gap | Section | Why It Matters |
|---|-----|---------|---------------|
| H1 | **Google Cloud TTS does not support Assamese** — F5 and Tech Stack table list a non-functional provider | §5 F5, §9 | IVR calls will fail entirely. Blocks a core demo feature. |
| H2 | **Twilio trial limits not documented in F4** — 5-number cap and no-custom-message restriction will surprise the team mid-hackathon | §5 F4 | Team will discover during Phase 2 that SMS doesn't work as expected. Wastes hours. |
| H3 | **No error handling specification** — What happens when the LLM API returns garbage for an SOS parse? When Gemini Vision can't identify a crop? When Twilio webhook times out? | §5 all | Every external API call can fail. Without defined fallbacks, the demo breaks live on stage. |
| H4 | **Safe-zone scoring formula inputs are undefined** — `RoadAccess` and `Capacity` have no data source | §5 F3 | The formula looks precise but the inputs are handwaved. Where does "road access" data come from? |
| H5 | **No CORS / cross-origin configuration** — Next.js frontend (port 3000) calling FastAPI backend (port 8000) on localhost | §8 | Will fail silently on first API call without CORS middleware configured on FastAPI |

### MEDIUM Impact Gaps

| # | Gap | Section | Why It Matters |
|---|-----|---------|---------------|
| M1 | **No seed data strategy** — PRD says "Seed SQLite with village data" but doesn't specify how many villages, which districts, or where the GeoJSON file comes from | §10, §14 | Team will spend the first 3 hours of the hackathon googling for GeoJSON files instead of coding |
| M2 | **Inbound SMS geolocation is unspecified** — F4 says LLM parses SOS into `{location, people_count, needs}` but a farmer texting "Pani ghor bhitor ahise" provides no GPS coordinates | §5 F4 | SOS pin on the map needs lat/lng. How does the system get coordinates from a text-only SMS? |
| M3 | **No rate limiting on LLM API calls** — The AI Query Interface and SOS parser both hit external LLM APIs. No mention of rate limits, cost caps, or caching | §5 F6 | During demo, if a judge spams the chatbot, you could hit Gemini's free-tier rate limit |
| M4 | **Survival Mode contradicts the architecture** — F8 describes client-side IndexedDB queuing, but the architecture shows all logic going through the FastAPI backend. Queued messages need a client-side retry loop that bypasses the normal API flow | §5 F8, §8 | The feature is described but the architecture doesn't show how offline-queued messages reconnect |
| M5 | **Timeline has no buffer** — 36-hour schedule with zero slack. If Phase 1 runs 2 hours late, everything cascades | §14 | Every hackathon phase takes longer than expected |

### LOW Impact Gaps

| # | Gap | Section | Why It Matters |
|---|-----|---------|---------------|
| L1 | **No favicon, app title, or meta tags specified** — minor but affects first impression | — | Judges notice a browser tab that says "localhost:3000" |
| L2 | **Crop assessment has no image size/format constraints** — What if someone uploads a 50MB RAW photo? | §5 F7 | Could crash the upload or exceed Gemini API limits |
| L3 | **No logging or observability** — If something breaks during the demo, there's no way to diagnose it | — | "It worked 5 minutes ago" with no logs is a hackathon cliché |

---

## Step 2: Improvement Recommendations

### 1. Structure & Clarity
- **Add an "Error Handling & Fallbacks" section** (new §6.5) specifying what each feature does when its external dependency fails.
- **Move the Chrome-only constraint from Open Questions into F8's spec** — it's not an open question, it's a known constraint.
- **Add a "Demo Script" section** (new §16) — a literal script of what you'll say and click during the 5-minute presentation. This is the single most impactful thing for winning a hackathon.

### 2. Completeness & Feasibility
- **Replace Google Cloud TTS with Bhashini API** in F5 and Tech Stack — verified to support Assamese.
- **Add Twilio trial constraints to F4** — explicitly state: "Demo limited to 5 pre-verified phone numbers. Custom message bodies require account upgrade (~$20)."
- **Define the SMS-to-GPS resolution strategy for M2** — Options: (a) map the farmer's registered village to its centroid coordinates, (b) ask the LLM to extract any location names and geocode them, or (c) accept that SMS-based SOS pins will snap to the farmer's registered village location.
- **Add a "Pre-Hackathon Checklist"** section listing everything that must be done before the event starts (GeoJSON prep, Twilio setup, API key acquisition, Bhashini registration).

### 3. Prioritization Adjustments
- **Promote F9 (Natural-Language Alert Generation) from Priority 3 to Priority 1.** It's a 1/10 difficulty LLM call but dramatically improves alert quality. It should be built into the SMS flow from the start, not bolted on later.
- **Keep F10 (Anomaly Detection) at Priority 3.** It's genuinely nice-to-have and can be skipped without hurting the demo.

---

## Quality Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Completeness** | 8/10 | Excellent coverage of features, schema, APIs, and timeline. Loses points for missing error handling, seed data strategy, and the TTS/Twilio factual errors. |
| **Clarity** | 9/10 | Exceptionally clear for a hackathon PRD. Feature tables are scannable. User journeys are concrete. Architecture diagram is helpful. |
| **Feasibility** | 7/10 | The core concept is very feasible. Loses points because two critical tech choices (Google Cloud TTS, Twilio trial scope) would have caused real problems. The timeline has no slack. |
| **User-Focus** | 9/10 | Four distinct, well-defined personas. User journeys cover all personas. The bilingual and IVR requirements show genuine empathy for the end users. |
| **Overall** | **8/10** | A strong, implementation-ready PRD that would have hit two painful blockers (TTS and Twilio) without this review. |

---

## Self-Check Results

1. **Summary table recount:** 5 goals (§2), 10 functional requirements (F1–F10 across §5), 6 NFRs (§6), 4 user journeys (§7), 10 tech stack rows (§9), 6 data requirement rows (§10), 6 success metrics (§11), 10 API endpoints (§12), 7 DB tables (§13), 6 timeline phases (§14), 7 open questions (§15). All counts match the actual content.
2. **Cross-reference check:** F1–F10 IDs are sequential and correctly referenced throughout. Goal G1–G5 IDs are consistent. No duplicate IDs found. Architecture diagram services (Flood Predict, Safe Zone, Alert Service, Crop Vision) map correctly to F2, F3, F4/F5, F7 respectively.
3. **Table consistency check:** Tech Stack (§9) lists "Google Cloud Text-to-Speech (Assamese)" but F5 also mentions "Bhashini API" as an alternative — this is an internal inconsistency that the updated PRD resolves by making Bhashini the primary. No other inter-table conflicts found.
4. **Status:** Self-check complete. Found 1 internal inconsistency (TTS provider), resolved in updated PRD.
