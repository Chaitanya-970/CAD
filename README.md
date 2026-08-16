<div align="center">
  <h3 align="center">AFIP - Assam Flood Intelligence Platform</h3>

  <p align="center">
    A comprehensive, AI-powered command center and survival dashboard built for the AFIP Hackathon. 
  </p>
</div>

---

## About The Project

AFIP (Assam Flood Intelligence Platform) is an intelligent disaster management dashboard. It calculates flood prediction mathematics, identifies safe zones in real-time, displays interactive map visualizations, and leverages Large Language Models (LLMs) to parse emergency SOS texts and assist government officials.

### Built With
* **Frontend:** Next.js, React, Leaflet
* **Backend:** FastAPI, Python
* **Database:** SQLite (Zero-config)
* **AI/LLMs:** LLaMA 3 / Gemini

---

## Getting Started (Local Development)

Follow these steps to get the project running locally. You will need **Node.js (v18+)** and **Python (3.10+)** installed.

### 1. Setup the Backend & Database

Because AFIP uses a built-in SQLite database, there is no complex database server setup required!

Open a terminal and navigate to the backend folder:
```bash
cd backend
```

Install the Python dependencies:
```bash
pip install -r requirements.txt
```

Initialize the database using the seed script. **This automatically creates the `afip.db` file right on your hard drive and populates it with 60 mock villages, 10 safe zones, and historical river data.**
```bash
python seed.py
```

Start the FastAPI backend server:
```bash
python -m uvicorn app.main:app --reload
```

### 2. Setup the Frontend

Open a *second* terminal window and navigate to the frontend folder:
```bash
cd frontend
```

Install the Node dependencies:
```bash
npm install
```

Start the Next.js development server:
```bash
npm run dev
```

Finally, open your browser and navigate to `http://localhost:3000` to view the dashboard!

---

## API Keys & Defensive AI

The AI features (Gov-GPT, SOS Parsing, Assamese Translation) rely on external LLM APIs (Gemini/Groq). 

If you do not provide real API keys in the `.env` file, **the app will not crash**. The backend uses strict defensive programming to catch API authentication exceptions and return safe default responses (e.g., *"I couldn't process that query. Try rephrasing."*). 

To test the real AI capabilities:
1. Open `backend/.env`.
2. Replace the `dummy` values with valid API keys for `GEMINI_API_KEY` and `GROQ_API_KEY`.
3. Restart the backend server.
