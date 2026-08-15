# RFC-004: SMS/IVR Alerting & SOS System

> **Features:** F4 (Outbound SMS), F5 (IVR Voice Calls), F9 (Natural-Language Alert Gen), F15 (Inbound SMS SOS), F16 (SOS Status Management)
> **Predecessors:** RFC-001
> **Successors:** RFC-006 (indirectly — SOS data feeds the map in RFC-003)
> **Complexity:** High
> **Primary Track:** Backend + ML/AI
> **Applicable Rules:** R7, R8, R10, R11, R12, R16, R17, R18, R25, R26, R27, R28, R29, R31, R34

---

## Summary

This RFC builds the complete alert pipeline: generating natural-language warning messages (LLM), sending them via SMS and Assamese IVR voice calls (Twilio + Bhashini), receiving inbound SOS replies from farmers (Twilio webhook), parsing those SOS texts into structured data (LLM), and allowing dashboard users to manage SOS status.

This is the highest-complexity RFC because it integrates 4 external services (Twilio SMS, Twilio Voice, Bhashini TTS, Gemini/Groq LLM).

---

## Technical Specification

### 1. Service: `backend/app/services/llm.py` (Partial — Alert & SOS Functions)

This file is shared with RFC-005. This RFC creates the file and implements 2 of the 4 functions:

```python
# Constants (R27)
ALERT_GEN_PROMPT = """You are a disaster warning system for Assam, India.
Convert the following flood prediction data into a warning message in Assamese.
The message must:
- Be under 160 characters (SMS limit)
- Include village name, timeframe, and nearest safe zone
- Be urgent but calm — do not cause panic
- Be written entirely in Assamese script

Data: {data}
"""

SOS_PARSE_PROMPT = """You are an emergency response parser for Assam, India.
Extract the following fields from this SOS message. The message may be in Assamese, Hindi, or English.
- location: string or null (any place name mentioned)
- people_count: integer or null
- needs: list of strings (e.g., ["water", "rescue", "medical"])
- is_sos: boolean (is this actually a distress call?)

Return ONLY valid JSON. No markdown, no explanation.

Message: {message}
"""

async def generate_alert_message(village_data: dict) -> str:
    """Uses Gemini (primary) or Groq (fallback) per R29."""
    ...

async def parse_sos_text(raw_text: str) -> dict:
    """Uses Gemini (primary) or Groq (fallback) per R29.
    Validates output with Pydantic. On parse failure, returns safe default (R18, R28)."""
    ...
```

### 2. Service: `backend/app/services/twilio_sms.py`

```python
async def send_village_alert(village_id: int, message: str) -> dict:
    """
    1. Look up all phone numbers registered to this village
    2. Send SMS to each number via Twilio
    3. Log each send in alerts_log table
    4. Return {count: N, failed: [...]}
    """

async def handle_inbound_sms(from_number: str, body: str) -> dict:
    """
    1. Call llm.parse_sos_text(body)
    2. Look up from_number in phone_registry to get village_id
    3. Get village lat/lng as fallback coordinates
    4. If LLM extracted a location name, try to match against villages table
    5. Insert into sos_messages table
    6. Return the parsed SOS record
    """
```

### 3. Service: `backend/app/services/twilio_voice.py`

```python
async def send_ivr_alert(village_id: int, alert_text: str) -> dict:
    """
    1. Call bhashini.text_to_speech(alert_text) to get audio bytes
    2. Save audio to a temporary file or use Twilio <Play> with a hosted URL
    3. Look up all phone numbers for the village
    4. For each number, initiate a Twilio Voice call that plays the audio
    5. Log in alerts_log with alert_type='ivr'
    6. Return {count: N, failed: [...]}

    FALLBACK (R18): If Bhashini TTS fails, fall back to sending plain-text SMS via twilio_sms
    """
```

### 4. Service: `backend/app/services/bhashini.py`

```python
async def text_to_speech(text: str, language: str = "as") -> bytes:
    """
    1. Call Bhashini ULCA TTS endpoint with Assamese language code
    2. Return audio bytes (WAV or MP3)
    3. On failure: raise BhashiniError (caught by twilio_voice for fallback)
    """
```

### 5. Routes

#### `backend/app/routes/alert.py`

| Method | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| `POST` | `/api/alert/sms` | `{ "village_id": 1 }` | `{ "status": "sent", "recipients": 5, "message": "..." }` |
| `POST` | `/api/alert/ivr` | `{ "village_id": 1 }` | `{ "status": "sent", "recipients": 5, "audio_generated": true }` |

**Flow for `/api/alert/sms`:**
1. Fetch village data + nearest safe zone from DB
2. Call `llm.generate_alert_message(village_data)` → get Assamese alert text (F9)
3. Call `twilio_sms.send_village_alert(village_id, alert_text)` → send SMS (F4)
4. Return result

**Flow for `/api/alert/ivr`:**
1. Same as above for alert text generation
2. Call `twilio_voice.send_ivr_alert(village_id, alert_text)` → TTS + call (F5)
3. On Bhashini failure → fall back to SMS (R18)

#### `backend/app/routes/sms.py`

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| `POST` | `/api/sms/webhook` | Twilio webhook form data (`From`, `Body`) | TwiML `<Response>` or `200 OK` |

This is called by Twilio when a farmer replies to an SMS. It must:
1. Extract `From` and `Body` from the form data
2. Call `twilio_sms.handle_inbound_sms(from_number, body)`
3. Return 200 OK (Twilio expects a response)

#### `backend/app/routes/sos.py`

| Method | Endpoint | Request | Response |
|--------|----------|---------|----------|
| `GET` | `/api/sos` | Query params: `?status=active` (optional) | Array of SOS records |
| `PATCH` | `/api/sos/{id}` | `{ "status": "acknowledged" }` | Updated SOS record |

### 6. Pydantic Models: `backend/app/models/alert.py`

```python
class AlertRequest(BaseModel):
    village_id: int

class AlertResponse(BaseModel):
    status: str
    recipients: int
    message: str | None = None
    audio_generated: bool | None = None

class SOSMessage(BaseModel):
    id: int
    from_number: str
    raw_text: str
    parsed_location: str | None
    parsed_needs: str | None
    parsed_people_count: int | None
    latitude: float
    longitude: float
    status: str
    received_at: str

class SOSStatusUpdate(BaseModel):
    status: str  # "acknowledged" or "resolved"
```

---

## Error Handling (R17, R18)

| Scenario | Fallback |
|----------|----------|
| Twilio SMS fails | Log error, return `{ "error": true, "code": "TWILIO_SMS_FAILED", "message": "SMS delivery failed — retry?" }` |
| Bhashini TTS fails | Fall back to plain-text SMS |
| LLM parse failure on SOS | Store raw text, pin at village centroid, flag "Unparsed — needs manual review" |
| LLM alert gen failure | Use a pre-written template: "⚠️ Flood warning for {village_name}. Move to higher ground." |

---

## Acceptance Criteria

| # | Criterion | Verifiable By |
|---|-----------|---------------|
| AC1 | `POST /api/alert/sms` sends an SMS in Assamese to verified Twilio numbers | Receive SMS on a verified phone |
| AC2 | SMS message is ≤160 characters and contains village name + safe zone | Read received SMS |
| AC3 | Alert is logged in `alerts_log` table with `alert_type='sms'` | SQL query |
| AC4 | `POST /api/alert/ivr` generates Assamese audio via Bhashini and places a voice call | Receive call on verified phone |
| AC5 | If Bhashini fails, IVR falls back to sending SMS | Mock Bhashini failure, verify SMS sent |
| AC6 | `POST /api/sms/webhook` with a simulated Twilio payload creates an SOS record | curl with test payload, check `sos_messages` table |
| AC7 | SOS text is parsed by LLM into structured fields (location, people_count, needs) | Verify parsed fields in DB |
| AC8 | If LLM parse fails, raw text is stored and SOS is pinned at village centroid | Send unparseable text, verify fallback |
| AC9 | `GET /api/sos` returns all active SOS messages with lat/lng | curl and validate JSON |
| AC10 | `PATCH /api/sos/{id}` updates status from "active" to "acknowledged" | curl, then verify in DB |
| AC11 | `services/llm.py` tries Gemini first, falls back to Groq on failure (R29) | Mock Gemini failure, verify Groq is called |
| AC12 | System prompts are defined as constants (R27) | Code review |
| AC13 | All LLM output is validated with Pydantic (R28) | Code review |

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/services/llm.py` | NEW | LLM calls (2 of 4 functions — alert gen + SOS parse) |
| `backend/app/services/twilio_sms.py` | NEW | Twilio SMS outbound + inbound handling |
| `backend/app/services/twilio_voice.py` | NEW | Twilio Voice + Bhashini TTS integration |
| `backend/app/services/bhashini.py` | NEW | Bhashini TTS API wrapper |
| `backend/app/models/alert.py` | NEW | Pydantic schemas for alerts and SOS |
| `backend/app/routes/alert.py` | MODIFY | Replace stubs with SMS and IVR endpoints |
| `backend/app/routes/sms.py` | MODIFY | Replace stub with Twilio webhook handler |
| `backend/app/routes/sos.py` | MODIFY | Replace stub with GET + PATCH endpoints |
