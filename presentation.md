---
marp: true
theme: default
size: 16:9
style: |
  section {
    background-color: #E9DED1;
    color: #2a1e13;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  section.hero {
    background-color: #8B1E2D;
    color: #E9DED1;
  }
  h1 {
    font-size: 80px;
    margin-bottom: 20px;
    color: #E9DED1 !important;
  }
  h2 {
    font-size: 50px;
    color: #8B1E2D;
    border-bottom: 3px solid #8B1E2D;
    padding-bottom: 10px;
  }
  section.hero h2 {
    color: #E9DED1;
    border-bottom: 3px solid #E9DED1;
  }
  p, li {
    font-size: 32px;
    line-height: 1.5;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 30px;
  }
  .card {
    background-color: #ffffff;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    border-left: 8px solid #8B1E2D;
  }
  .card h3 {
    margin: 0 0 10px 0;
    color: #8B1E2D;
    font-size: 36px;
  }
---

<!-- _class: hero -->
# Assam Flood Intelligence Platform
## AI-Powered Command Center for Disaster Survival

**Team CAD**
Chaitanya Bhardwaj · Anshika Jain · Divya Sharma

github.com/Chaitanya-970/CAD

---

## The Problem
During the Assam floods, emergency response is hindered by a severe lack of real-time data, communication blackouts, and unpredictable water levels. 

- **4.2 Million** people affected annually in Assam alone.
- **8-12 Hour Delay** in standard relief resource allocation.
- **Zero Connectivity** leaves victims stranded without SOS capabilities.

---

## The Solution
AFIP is an intelligent disaster management dashboard. We specialize in real-time flood prediction, dynamic safe zone identification, and AI-powered SOS parsing.

<div class="grid-3" style="margin-top: 20px;">
  <div class="card">
    <h3>Predictive Mapping</h3>
    <p>Visualizing risk levels across 60+ villages in real-time.</p>
  </div>
  <div class="card">
    <h3>AI-Powered SOS</h3>
    <p>Parsing raw emergency texts into actionable rescue missions.</p>
  </div>
  <div class="card">
    <h3>Offline Survival</h3>
    <p>Falling back to edge mock data during complete communication blackouts.</p>
  </div>
</div>

---

## Tech Stack

<div class="grid">
  <div class="card">
    <h3>Frontend</h3>
    <p>Next.js, React, Leaflet</p>
  </div>
  <div class="card">
    <h3>Backend</h3>
    <p>FastAPI, Python</p>
  </div>
  <div class="card">
    <h3>Database</h3>
    <p>SQLite (Zero-Config)</p>
  </div>
  <div class="card">
    <h3>AI / ML</h3>
    <p>Groq, LLaMA, Gemini</p>
  </div>
</div>

---

## System Architecture
AFIP is built on a highly resilient, modern architecture that ensures data flows seamlessly even in disaster zones.

<div class="grid" style="margin-top: 40px;">
  <div class="card" style="text-align: center;">
    <h3>1. Data Ingestion</h3>
    <p>Telemetry & Weather APIs</p>
  </div>
  <div class="card" style="text-align: center;">
    <h3>2. Math Engine</h3>
    <p>Real-time Risk Prediction</p>
  </div>
  <div class="card" style="text-align: center;">
    <h3>3. NLP & Vision</h3>
    <p>Automated SOS Parsing</p>
  </div>
  <div class="card" style="text-align: center;">
    <h3>4. Edge Dashboard</h3>
    <p>Offline Synchronization</p>
  </div>
</div>

---

## The AI Pipeline (Qwen2-VL)
Our multi-agent pipeline powers the backend logic for disaster relief, connecting **Vision → RAG → Weather → Cost** estimation.

<div style="text-align: center; margin-top: 20px;">
  <img src="image.png" alt="AI Pipeline Architecture" style="max-height: 400px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" />
</div>
   
<p style="font-style: italic; font-size: 24px; margin-top: 20px; text-align: center;">
  "We fine-tuned Qwen2-VL on 300 samples for 1 epoch due to time constraints — the pipeline is fully functional, and accuracy would improve with a longer training run on the full dataset."
</p>

---

## Key Features

- **Interactive Bilingual Map**: Visualizes risk levels and dynamic safe zones in English and Assamese.
- **Gov-GPT Dashboard**: Natural language query interface for officials to instantly analyze flood data.
- **AI-Powered SOS Parser**: Converts unstructured SMS cries for help into actionable rescue missions.
- **Automated SMS & IVR Alerts**: Sends localized SMS warnings and Bhashini-translated voice calls.
- **Survival Mode (Offline Edge)**: Ensures zero-downtime by falling back to local mock data during total blackouts.

---

## Post-Flood Crop Assessment
Post-disaster agricultural recovery is critical for Assam's economy.

<div class="grid" style="margin-top: 20px;">
  <div class="card">
    <h3>Vision Analysis</h3>
    <p>Farmers upload photos of flooded fields for instant crop identification and damage estimation.</p>
  </div>
  <div class="card">
    <h3>Actionable Recovery</h3>
    <p>Generates 3 immediate recovery steps in both English and Assamese via Bhashini translation.</p>
  </div>
</div>

---

<!-- _class: hero -->
# THANK YOU
## Ready to deploy and save lives.

**Team CAD**
Chaitanya Bhardwaj · Anshika Jain · Divya Sharma

github.com/Chaitanya-970/CAD
