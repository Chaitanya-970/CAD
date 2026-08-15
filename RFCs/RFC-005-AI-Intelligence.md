# RFC-005: AI Intelligence Layer

> **Features:** F6 (AI Query Interface), F7 (Crop Damage Assessment), F17 (LLM SOS Parsing), F18 (Assamese Translation), F19 (Crop Assessment History)
> **Predecessors:** RFC-001
> **Successors:** None (leaf node)
> **Complexity:** High
> **Primary Track:** ML/AI (model training + inference + prompts) + Frontend (chat UI + crop upload UI)
> **Applicable Rules:** R6, R7, R8, R21, R25, R27, R28, R29, R31, R35, R36

---

## Summary

This RFC builds all AI-powered features. The major architecture change from the original design: **crop damage assessment (F7) now uses a Llama 3.1 7B/8B model fine-tuned via QLoRA** on flood-damaged crop data, hosted on Google Colab and exposed via ngrok — instead of Gemini Vision API. All other LLM tasks (Gov-GPT, SOS parsing, alert generation) still use Gemini API (primary) / Groq (fallback).

---

## Part 1: ML/AI Person — Model Training & Inference

### 1.1 Training Dataset Preparation

Curate a dataset of ~200–500 labeled examples:

| Field | Type | Example |
|-------|------|---------|
| `image` | JPEG/PNG | Photo of flooded paddy field |
| `crop_type` | string | "Paddy (Rice)" |
| `damage_pct` | integer | 70 |
| `advisory_en` | string | "1) Drain standing water immediately. 2) Apply potash fertilizer. 3) Re-sow short-duration Sali rice." |
| `advisory_as` | string | Assamese translation of above |

**Data sources:**
- Search for flood-damaged crop images from Assam agricultural extension reports
- Use open datasets (e.g., PlantVillage for crop identification, combined with synthetic flood damage labels)
- Manually label 50–100 high-quality examples, augment the rest

### 1.2 QLoRA Fine-Tuning (Colab Notebook)

Create a Colab notebook `AFIP_Crop_Model_Training.ipynb`:

```python
# Setup
!pip install transformers peft bitsandbytes accelerate datasets trl

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 1. Load base model in 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model_id = "meta-llama/Llama-3.1-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# 2. Apply LoRA adapters
lora_config = LoraConfig(
    r=16,                    # rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)

# 3. Training format — each example is a conversation
# System: "You are an agricultural expert..."
# User: [image description or base64 image] "Assess this crop."
# Assistant: {"crop_type": "...", "damage_pct": ..., "advisory_en": "...", "advisory_as": "..."}

# 4. Train with SFTTrainer from trl
from trl import SFTTrainer, SFTConfig

training_args = SFTConfig(
    output_dir="./afip-crop-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    args=training_args,
)

trainer.train()

# 5. Save adapter weights (NOT the full model — just the LoRA adapters)
model.save_pretrained("./afip-crop-adapters")
tokenizer.save_pretrained("./afip-crop-adapters")
```

### 1.3 Inference Server (Colab Notebook)

Create a second notebook `AFIP_Crop_Inference.ipynb` (or a second section in the same notebook):

```python
# Load base model + QLoRA adapters
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config)
model = PeftModel.from_pretrained(base_model, "./afip-crop-adapters")
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Expose via Flask
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    image_b64 = request.json.get("image")  # base64-encoded image
    
    prompt = f"""You are an agricultural expert in Assam, India.
    Analyze this flood-damaged crop image and return ONLY valid JSON:
    {{"crop_type": "...", "damage_pct": ..., "advisory_en": "...", "advisory_as": "..."}}
    """
    
    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.3)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Parse JSON from response
    try:
        result = json.loads(response)
        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Model output was not valid JSON", "raw": response}), 500

# Run Flask + ngrok
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")
public_url = ngrok.connect(5000)
print(f"🌐 Public URL: {public_url}")
app.run(port=5000)
```

**Important:** The ngrok URL changes every time the notebook restarts. Update `CROP_MODEL_URL` in `backend/.env` accordingly.

### 1.4 Prompt Engineering for Other LLM Functions

The ML person also owns the **content** of all system prompts in `services/llm.py`. These should be tuned and tested:

| Function | Prompt Constant | Test With |
|----------|----------------|-----------|
| `parse_sos_text()` | `SOS_PARSE_PROMPT` | 20 sample SOS messages (English, Hindi, Assamese mix) |
| `generate_alert_message()` | `ALERT_GEN_PROMPT` | 5 sample village risk data payloads |
| `answer_query()` | `QUERY_SYSTEM_PROMPT` | 15 predefined official queries from PRD §11 |
| `translate_to_assamese()` | `TRANSLATE_PROMPT` | 10 sample English advisory texts |

---

## Part 2: Backend Person — API Endpoints

### 2.1 Service: `backend/app/services/crop_model.py` (NEW)

```python
import os
import httpx
import base64
from app.config import settings

CROP_MODEL_URL = os.getenv("CROP_MODEL_URL")  # ngrok URL

async def assess_crop_image(image_bytes: bytes) -> dict:
    """
    Send image to Colab-hosted fine-tuned Llama 3.1 model.
    
    Fallback: If Colab endpoint is down, fall back to Gemini Vision API.
    """
    image_b64 = base64.b64encode(image_bytes).decode()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:  # 30s — model inference is slow
            response = await client.post(
                f"{CROP_MODEL_URL}/predict",
                json={"image": image_b64}
            )
            response.raise_for_status()
            return response.json()
    except (httpx.TimeoutException, httpx.ConnectError) as e:
        # FALLBACK: Use Gemini Vision API
        from app.services.llm import assess_crop_image_gemini
        return await assess_crop_image_gemini(image_bytes)
```

### 2.2 Service: `backend/app/services/llm.py` (Complete)

This file has 5 functions total:

| Function | Used By | Provider |
|----------|---------|----------|
| `generate_alert_message(village_data)` | RFC-004 (F9) | Gemini → Groq fallback |
| `parse_sos_text(raw_text)` | RFC-004 (F15, F17) | Gemini → Groq fallback |
| `answer_query(question, context)` | RFC-005 (F6) | Gemini → Groq fallback |
| `assess_crop_image_gemini(image_bytes)` | RFC-005 (F7 fallback) | Gemini Vision ONLY |
| `translate_to_assamese(text)` | RFC-004, RFC-005 (F18) | Gemini → Groq fallback |

Note: `assess_crop_image_gemini` is the **fallback** for when the Colab model is down. The primary crop assessment goes through `crop_model.py`.

### 2.3 Route: `backend/app/routes/crop.py`

```python
@router.post("/api/crop-assess")
async def crop_assess(image: UploadFile):
    contents = await image.read()
    
    # Validate
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "Image exceeds 5MB limit")
    
    # Save to uploads/
    filename = f"{uuid4()}.{image.filename.split('.')[-1]}"
    filepath = f"uploads/{filename}"
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Call fine-tuned model (with Gemini fallback)
    result = await crop_model.assess_crop_image(contents)
    
    # Store in DB (F19)
    db.execute("""
        INSERT INTO crop_assessments (image_path, crop_type, damage_pct, advisory_en, advisory_as)
        VALUES (?, ?, ?, ?, ?)
    """, (filepath, result["crop_type"], result["damage_pct"], 
          result["advisory_en"], result["advisory_as"]))
    
    return result
```

### 2.4 Route: `backend/app/routes/query.py`

```python
@router.post("/api/query")
async def query(request: QueryRequest):
    # Build context from live DB data
    villages = db.fetch_all("SELECT * FROM villages")
    sos = db.fetch_all("SELECT * FROM sos_messages WHERE status = 'active'")
    safe_zones = db.fetch_all("SELECT * FROM safe_zones")
    
    context = {"villages": villages, "sos_messages": sos, "safe_zones": safe_zones}
    
    answer = await llm.answer_query(request.question, context)
    return {"answer": answer}
```

### 2.5 Route: `backend/app/routes/villages.py`

Simple read-only endpoint returning village metadata for frontend use.

### 2.6 New `.env` Key

Add to `backend/.env.example`:
```
CROP_MODEL_URL=  # ngrok URL from Colab inference notebook
```

Update `config.py` to include `CROP_MODEL_URL` as an optional key (not required — falls back to Gemini Vision if missing).

---

## Part 3: Frontend Person — UI Components

### 3.1 Chat UI: `components/chat/QueryChat.jsx`

Collapsible chat panel on the dashboard (right side):

```
┌─────────────────────────────┐
│  🤖 Ask AFIP               │
├─────────────────────────────┤
│  [User bubble] Which        │
│  villages are at risk?      │
│                             │
│  [AI bubble] Based on       │
│  current data, 5 villages...│
├─────────────────────────────┤
│  [Type your question...]  ▶ │
└─────────────────────────────┘
```

- `'use client'` component
- Chat history in local state
- POST to `/api/query` on submit
- 3-second cooldown between queries
- Error: show "I couldn't process that query. Try rephrasing."

### 3.2 Crop Upload Page: `app/crop/page.jsx`

```
┌──────────────────────────────────┐
│  AFIP — Crop Damage Assessment   │
├──────────────────────────────────┤
│  📷 Upload a photo of your      │
│  flooded field                   │
│  [Choose File] or drag           │
│                                  │
│  ── Results ──                   │
│  🌾 Crop: Paddy (Rice)          │
│  📊 Damage: 70%                 │
│  Recovery Steps:                 │
│  1. Drain standing water         │
│  2. Apply potash fertilizer      │
│  3. Re-sow Sali rice            │
│  অসমীয়া: [Assamese version]     │
│  ⚡ Assessed by: Fine-tuned AI  │
└──────────────────────────────────┘
```

- Compress image client-side to ≤5MB before upload (R36)
- Show loading spinner (model inference takes 10–30 seconds on Colab T4)
- Display both English and Assamese advisory (R31)
- Show which model assessed (fine-tuned vs. Gemini fallback)
- Error: "We couldn't assess this image. Please retake in better lighting."

---

## Acceptance Criteria

| # | Criterion | Owner | Verifiable By |
|---|-----------|-------|---------------|
| AC1 | QLoRA fine-tuning notebook runs on Colab T4 without OOM | 🤖 ML | Run notebook end-to-end |
| AC2 | Inference notebook loads model + adapters and exposes `/predict` via ngrok | 🤖 ML | curl the ngrok URL with a test image |
| AC3 | Fine-tuned model returns valid JSON with crop_type, damage_pct, advisory_en, advisory_as | 🤖 ML | Test with 10 sample images, ≥80% return valid JSON |
| AC4 | `crop_model.py` calls Colab endpoint and returns structured response | 🔧 Backend | curl `/api/crop-assess` with test image |
| AC5 | If Colab endpoint is down, crop assessment falls back to Gemini Vision | 🔧 Backend | Stop Colab notebook, verify Gemini fallback |
| AC6 | `POST /api/query` returns relevant answer citing actual village names | 🔧 Backend | curl with test query |
| AC7 | LLM timeout → returns "I couldn't process that query" fallback | 🔧 Backend | Mock timeout |
| AC8 | Crop assessment stored in `crop_assessments` table (F19) | 🔧 Backend | SQL query after upload |
| AC9 | Chat UI shows user and AI message bubbles | 🎨 Frontend | Visual inspection |
| AC10 | Chat UI disables input for 3 seconds after query | 🎨 Frontend | Rapid click test |
| AC11 | Crop upload page compresses images to ≤5MB | 🎨 Frontend | Upload 10MB image, check network size |
| AC12 | Crop results show English + Assamese advisory | 🎨 Frontend | Visual inspection |
| AC13 | SOS parsing extracts location, people_count, needs from ≥90% of 20 test messages | 🤖 ML | Run test suite |
| AC14 | All system prompts are constants at top of `llm.py` (R27) | 🤖 ML | Code review |
| AC15 | `GET /api/villages` returns village metadata | 🔧 Backend | curl |

---

## Files Created/Modified

| File | Owner | Action | Purpose |
|------|-------|--------|---------|
| `AFIP_Crop_Model_Training.ipynb` | 🤖 ML | NEW | Colab notebook for QLoRA fine-tuning |
| `AFIP_Crop_Inference.ipynb` | 🤖 ML | NEW | Colab notebook for inference + ngrok |
| `backend/app/services/crop_model.py` | 🤖 ML + 🔧 Backend | NEW | Calls Colab endpoint with Gemini fallback |
| `backend/app/services/llm.py` | 🤖 ML (prompts) + 🔧 Backend (code) | MODIFY | Add `answer_query`, `assess_crop_image_gemini`, `translate_to_assamese` |
| `backend/app/models/query.py` | 🔧 Backend | NEW | Pydantic schemas for query |
| `backend/app/models/crop.py` | 🔧 Backend | NEW | Pydantic schemas for crop assessment |
| `backend/app/routes/query.py` | 🔧 Backend | MODIFY | Gov-GPT endpoint |
| `backend/app/routes/crop.py` | 🔧 Backend | MODIFY | Crop assessment endpoint |
| `backend/app/routes/villages.py` | 🔧 Backend | MODIFY | Village metadata endpoint |
| `frontend/src/components/chat/QueryChat.jsx` | 🎨 Frontend | NEW | Chat UI |
| `frontend/src/components/chat/chat.module.css` | 🎨 Frontend | NEW | Chat styles |
| `frontend/src/app/crop/page.jsx` | 🎨 Frontend | MODIFY | Crop upload + results page |
| `frontend/src/app/crop/crop.module.css` | 🎨 Frontend | NEW | Crop page styles |
