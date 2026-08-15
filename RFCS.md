# RFCS.md — Assam Flood Intelligence Platform (AFIP)

> **Product Type:** Web App
> **Skipped Checks:** Library/SDK concerns, auth/RBAC (PRD §3.2 F25), regulatory compliance (hackathon prototype).
> **Authority Order:** PRD.md > FEATURES.md > RULES.md > RFCs. No conflicts detected between source documents.
> **Implementation:** Each RFC is implemented by running `/implement-rfc <id>`

---

## Overview

The project is divided into **6 RFCs** following the critical-path dependency order from FEATURES.md and the phased implementation mandate from RULES.md R37.

### Key Architecture Decision: QLoRA Fine-Tuned Model

The crop damage assessment (F7) uses a **Llama 3.1 7B/8B model fine-tuned via QLoRA** on flood-damaged crop images, hosted on **Google Colab (free T4 GPU) and exposed via ngrok**. This replaces the original Gemini Vision API for crop assessment. All other LLM tasks (Gov-GPT, SOS parsing, alert generation) still use Gemini API (primary) / Groq (fallback).

---

## RFC Index

| RFC | Title | Features | Predecessors | Complexity | Owner |
|-----|-------|----------|-------------|------------|-------|
| [RFC-001](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/RFCs/RFC-001-Project-Foundation.md) | Project Foundation & Data Layer | F13, F14 | None | Medium | **Backend** |
| [RFC-002](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/RFCs/RFC-002-Prediction-Engine.md) | Flood Prediction & Safe Zone Engine | F2, F3, F10 | RFC-001 | Medium | **Backend** |
| [RFC-003](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/RFCs/RFC-003-Map-Dashboard.md) | Map Dashboard & Visualization | F1, F11, F12, F20 | RFC-002 | Medium | **Frontend** |
| [RFC-004](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/RFCs/RFC-004-Alerting-System.md) | SMS/IVR Alerting & SOS System | F4, F5, F9, F15, F16 | RFC-001 | High | **Backend** |
| [RFC-005](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/RFCs/RFC-005-AI-Intelligence.md) | AI Intelligence Layer | F6, F7, F17, F18, F19 | RFC-001 | High | **ML/AI** (backend + training) + **Frontend** (UI) |
| [RFC-006](file:///c:/Users/LOQ/OneDrive/Desktop/CAD/RFCs/RFC-006-Survival-Polish.md) | Survival Mode & Polish | F8, F21 | RFC-003 | Medium | **Frontend** + **Backend** (logging) |

---

## Dependency Graph

```
RFC-001 (Foundation) ◄── Backend builds this first
   │
   ├──────────────────────┐──────────────────────┐
   ▼                      ▼                      ▼
RFC-002 (Prediction)    RFC-004 (Alerts)       RFC-005 (AI Layer)
   │ Backend              │ Backend              │ ML/AI person
   ▼                      │                      │
RFC-003 (Map)             │                      │
   │ Frontend             │                      │
   ▼                      ▼                      ▼
RFC-006 (Survival + Polish) ◄── everyone finishes here
```

---

## 👥 Team Assignment — 3-Person Split

### 🔧 Person A: Backend Developer

Owns the FastAPI server, database, Twilio/Bhashini integrations, and all API endpoints.

| Time Block | RFC | Tasks |
|------------|-----|-------|
| **Hour 0–4** | RFC-001 | FastAPI scaffolding, CORS, SQLite schema, seed script, `.env` config, all route stubs |
| **Hour 4–6** | RFC-002 | Prediction engine (`services/prediction.py`), safe-zone ranking (`services/safezone.py`), flood/safezone routes |
| **Hour 6–14** | RFC-004 | Twilio SMS outbound, Twilio webhook for inbound SOS, Twilio Voice + Bhashini TTS, alert routes, SOS routes |
| **Hour 14–18** | RFC-005 (backend parts) | `services/llm.py` — Gov-GPT query endpoint, SOS text parsing, alert generation, Assamese translation. Crop assessment route (calls ML person's Colab endpoint) |
| **Hour 18–20** | RFC-006 | Request logging middleware, external API call logging |
| **Hour 20–36** | Integration | Help with end-to-end testing, bug fixes, demo prep |

**Files owned by Backend person:**
- All `backend/` files
- Except: `backend/app/services/crop_model.py` (ML person owns this)

---

### 🤖 Person B: ML/AI & Models

Owns the QLoRA fine-tuning pipeline, crop damage model training, Colab notebook, and the inference endpoint.

| Time Block | RFC | Tasks |
|------------|-----|-------|
| **Hour 0–4** | Pre-work | Collect/curate training dataset: flood-damaged crop images + labels (crop_type, damage_pct, advisory). Need ~200–500 labeled image-text pairs |
| **Hour 4–12** | RFC-005 (model training) | Fine-tune Llama 3.1 7B/8B with QLoRA on Colab. Set up training notebook: load base model → apply QLoRA adapters → train on crop assessment dataset → save adapter weights |
| **Hour 12–16** | RFC-005 (inference) | Create Colab inference notebook: load base model + QLoRA adapters → expose as HTTP endpoint via ngrok. Test endpoint with sample images |
| **Hour 16–20** | RFC-005 (integration) | Write `backend/app/services/crop_model.py` that calls the Colab ngrok endpoint. Coordinate with Backend person on the `/api/crop-assess` route |
| **Hour 20–24** | RFC-005 (prompt tuning) | Tune system prompts for `llm.py` functions: SOS parsing accuracy, alert generation quality, Gov-GPT relevance. Test with sample data from PRD §11 |
| **Hour 24–36** | Integration | Help with end-to-end testing, prompt fixes, model quality checks |

**Files owned by ML person:**
- `backend/app/services/crop_model.py` (NEW — calls Colab endpoint)
- Colab notebooks (training + inference)
- System prompt constants in `backend/app/services/llm.py` (content of prompts)
- Training dataset curation

---

### 🎨 Person C: Frontend Developer

Owns the entire Next.js frontend — map dashboard, chat UI, crop upload page, survival mode.

| Time Block | RFC | Tasks |
|------------|-----|-------|
| **Hour 0–4** | RFC-001 (frontend) | Next.js scaffolding, `src/lib/api.js`, basic layout, page placeholders |
| **Hour 4–14** | RFC-003 | Leaflet map with flood zones, safe zones, SOS pins, village popups (bilingual), safe-zone popups, simulation panel, status bar |
| **Hour 14–18** | RFC-005 (frontend) | Chat UI for Gov-GPT (`QueryChat.jsx`), crop upload page with image compression, results card (English + Assamese) |
| **Hour 18–24** | RFC-006 | `useSurvivalMode` hook, IndexedDB offline queue, mode banner, error boundary |
| **Hour 24–28** | Polish | Loading states, responsive layout (1366x768), favicon, page title, alert send buttons on map popups |
| **Hour 28–36** | Integration | Connect to backend APIs, end-to-end testing, demo prep |

**Files owned by Frontend person:**
- All `frontend/` files

---

## Feature-to-Person Mapping

| Feature | ID | Owner | RFC |
|---------|----|-------|-----|
| Interactive Flood-Risk Map | F1 | 🎨 Frontend | RFC-003 |
| 48-Hour Flood Forecasting | F2 | 🔧 Backend | RFC-002 |
| Safe-Zone Recommendation | F3 | 🔧 Backend | RFC-002 |
| Outbound SMS Alerts | F4 | 🔧 Backend | RFC-004 |
| IVR Voice Call Alerts | F5 | 🔧 Backend | RFC-004 |
| AI Query Interface (Gov-GPT) | F6 | 🔧 Backend (endpoint) + 🎨 Frontend (UI) | RFC-005 |
| Crop Damage Assessment | F7 | 🤖 ML/AI (model + service) + 🎨 Frontend (upload UI) | RFC-005 |
| Survival Mode | F8 | 🎨 Frontend | RFC-006 |
| Alert Text Generation | F9 | 🔧 Backend | RFC-004 |
| Anomaly Detection | F10 | 🔧 Backend | RFC-002 |
| Bilingual Map Labels | F11 | 🎨 Frontend | RFC-003 |
| SOS Pin Display | F12 | 🎨 Frontend | RFC-003 |
| Database & Schema | F13 | 🔧 Backend | RFC-001 |
| FastAPI Backend | F14 | 🔧 Backend | RFC-001 |
| Inbound SMS SOS | F15 | 🔧 Backend | RFC-004 |
| SOS Status Management | F16 | 🔧 Backend | RFC-004 |
| LLM SOS Parsing | F17 | 🤖 ML/AI (prompts) + 🔧 Backend (integration) | RFC-005 |
| Assamese Translation | F18 | 🤖 ML/AI (prompts) + 🔧 Backend (integration) | RFC-005 |
| Crop Assessment History | F19 | 🔧 Backend | RFC-005 |
| Simulation Controls | F20 | 🎨 Frontend | RFC-003 |
| Request Logging | F21 | 🔧 Backend | RFC-006 |

---

## QLoRA Model Architecture

### Training Setup (Colab)
```
Base Model:  meta-llama/Llama-3.1-8B-Instruct (or 7B)
Method:      QLoRA (4-bit quantization + LoRA adapters)
GPU:         Google Colab free T4 (16GB VRAM)
Dataset:     ~200-500 labeled flood-damaged crop images
Task:        Given an image of a flooded field → output JSON:
             { crop_type, damage_pct, advisory_en, advisory_as }
Framework:   Hugging Face Transformers + PEFT + bitsandbytes
```

### Inference Setup (Colab → ngrok)
```
Colab notebook loads base model + QLoRA adapters
Exposes a Flask/FastAPI endpoint on port 5000
ngrok tunnels it to a public URL (e.g., https://abc123.ngrok.io)
Backend's crop_model.py calls this URL
```

### Integration with Backend
```python
# backend/app/services/crop_model.py
COLAB_ENDPOINT = os.getenv("CROP_MODEL_URL")  # ngrok URL from .env

async def assess_crop_image(image_bytes: bytes) -> dict:
    """
    POST image to Colab-hosted fine-tuned model.
    Returns { crop_type, damage_pct, advisory_en, advisory_as }
    
    Fallback: If Colab endpoint is down, fall back to Gemini Vision API.
    """
```

### New .env Key
```
CROP_MODEL_URL=https://abc123.ngrok.io/predict
```

---

## Feature Coverage Verification

21 features (F1–F21) assigned to RFCs. 4 Won't Have (F22–F25) excluded. Each feature has exactly one owner. ✅

---

## Self-Check Results

1. **RFC count:** 6 RFCs (001–006). No gaps, no duplicates. ✅
2. **Feature coverage:** 21/21 in-scope features mapped. 4/4 out-of-scope excluded. ✅
3. **Predecessor references:** RFC-001 has none. RFC-002→001, RFC-003→002, RFC-004→001, RFC-005→001, RFC-006→003. No circular deps. ✅
4. **Person assignment:** Every feature has exactly one primary owner. Shared features (F6, F7, F17, F18) have clear backend/frontend/ML splits. ✅
5. **QLoRA change:** F7 now uses fine-tuned Llama 3.1 via Colab+ngrok instead of Gemini Vision. Fallback to Gemini Vision if Colab is down. ✅
