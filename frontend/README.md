# AFIP Frontend — Assam Flood Intelligence Platform

Next.js (App Router) dashboard for AFIP — built per `RFC-001`, `RFC-003`,
the frontend portions of `RFC-005`, and `RFC-006`.

## Stack

- **Next.js 16** (App Router, JS, CSS Modules — no Tailwind)
- **Leaflet.js + react-leaflet** for the map (dynamically imported, `ssr: false`)
- **lucide-react** for icons
- Design tokens (colors/fonts/spacing) lifted directly from `DESIGN.md`

## Getting started

```bash
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_URL if backend isn't on :8000
npm run dev
```

Open http://localhost:3000. The FastAPI backend (RFC-001/002/004/005) is expected
at `http://localhost:8000` by default.

**No backend yet?** The dashboard still works — `src/lib/mockData.js` provides
demo villages, safe zones, and SOS pins so the map renders and is fully
interactive even before the backend is running. A small "Demo data" badge
appears in the status bar whenever it's serving mock data instead of live data.

## Structure

```
src/
  app/
    page.js                landing page
    dashboard/page.js       main map dashboard (F1, F11, F12, F20, F6, F8)
    crop/page.js             crop damage upload + results (F7)
  components/
    map/                    FloodMap, popups, SOS pins, text-only list
    alerts/                 SimulationPanel (river-level sliders → /api/predict)
    chat/                   QueryChat (Gov-GPT)
    survival/               ModeBanner (Survival Mode UI)
    layout/                 Header/nav
    ErrorBoundary.jsx
  hooks/
    useSurvivalMode.js       bandwidth detection + offline queueing (F8)
  lib/
    api.js                   fetchAPI client (10s timeout, typed endpoint helpers)
    offlineQueue.js          IndexedDB wrapper for queued offline requests
    mockData.js              demo fallback data
```

## Notes

- Chrome is required for full Survival Mode fidelity (`navigator.connection`
  is Chromium-only); other browsers fall back to the `navigator.onLine`
  boolean check, per PRD §6.1 / R45.
- Map center defaults to the Brahmaputra valley (~26.2°N, 92.9°E), zoom 8.
- All external API calls go through `fetchAPI`, which enforces a 10-second
  timeout and surfaces failures to the UI rather than hanging silently.
