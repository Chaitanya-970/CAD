# RFC-003: Map Dashboard & Visualization

> **Features:** F1 (Interactive Flood-Risk Map), F11 (Bilingual Map Labels), F12 (SOS Pin Display), F20 (River Level Simulation Controls)
> **Predecessors:** RFC-002 (needs `/api/flood-zones` and `/api/safe-zones` returning real data)
> **Successors:** RFC-006
> **Complexity:** Medium
> **Primary Track:** Frontend
> **Applicable Rules:** R6, R20, R21, R22, R23, R24, R35, R45, R47

---

## Summary

This RFC builds the primary user-facing dashboard — the Leaflet.js map with flood-zone overlays, safe-zone markers, SOS pin display, bilingual labels, and a simulation control panel for the demo operator to adjust river levels in real-time.

---

## Technical Specification

### 1. Dynamic Import of Leaflet (R22)

Leaflet cannot run during SSR. The map must be loaded with `next/dynamic`:

```jsx
// app/dashboard/page.jsx
'use client';
import dynamic from 'next/dynamic';

const FloodMap = dynamic(() => import('@/components/map/FloodMap'), {
  ssr: false,
  loading: () => <div className="map-loading">Loading map...</div>,
});
```

### 2. Component: `components/map/FloodMap.jsx`

The main map component. Uses `react-leaflet` `MapContainer`, `TileLayer`, and custom layers.

**Initial view:** Centered on the Brahmaputra valley in Assam (~26.2°N, 92.9°E), zoom level 8.

**Layers (toggleable via layer control):**
1. **Flood Zone Layer** — Circle markers for each village, colored by risk level:
   - `risk_level: "high"` → red (#ef4444)
   - `risk_level: "moderate"` → yellow (#f59e0b)
   - `risk_level: "safe"` → green (#22c55e)
   - Circle radius proportional to population
2. **Safe Zone Layer** — Green diamond markers for safe zones with score labels
3. **SOS Pins Layer** — Red pulsing markers for active SOS messages (data from `GET /api/sos`)

**Data fetching:** On mount, fetch from:
- `GET /api/flood-zones` → render flood zone layer
- `GET /api/safe-zones` → render safe zone layer
- `GET /api/sos` → render SOS pins (poll every 10 seconds)

### 3. Component: `components/map/VillagePopup.jsx`

Popup shown when clicking a village marker:
```
┌─────────────────────────────┐
│ Majuli (মাজুলী)            │  ← bilingual name (F11)
│ District: Majuli            │
│ Elevation: 48.5m            │
│ Population: ~1,200          │
│ Risk Score: 0.85 (HIGH)     │
│ [Send Alert]                │  ← triggers SMS (placeholder until RFC-004)
└─────────────────────────────┘
```

### 4. Component: `components/map/SafeZonePopup.jsx`

```
┌─────────────────────────────┐
│ 🟢 Kamalabari Hill          │
│ Safe Score: 0.82            │
│ ├ Elevation: 40%            │
│ ├ Road Access: 25%          │
│ ├ Distance: 20%             │
│ └ Capacity: 15%             │
│ Capacity: ~500 people       │
└─────────────────────────────┘
```

### 5. Component: `components/map/SOSPin.jsx`

Red pulsing marker for SOS messages. Popup shows:
- Raw SOS text
- Parsed needs (if available)
- People count
- Timestamp
- Status badge (Active / Acknowledged / Resolved)

CSS animation for pulsing:
```css
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}
```

### 6. Component: `components/alerts/SimulationPanel.jsx` (F20)

A collapsible side panel for the demo operator:
- Slider for each river station: "Current Level" (range: station.danger_level ± 5m)
- Slider for "Forecast Rise" (range: 0–5m)
- "Recalculate" button that `POST`s to `/api/predict` with the slider values
- On response, the map automatically re-fetches and re-renders flood zones

### 7. Dashboard Layout: `app/dashboard/page.jsx`

```
┌──────────────────────────────────────────────┐
│  AFIP — Flood Intelligence    [Simulation ▼] │  ← header with collapsible panel toggle
├──────────────────────────────────────────────┤
│                                              │
│            FloodMap (full viewport)          │
│                                              │
│  [Layer toggles]     [Zoom controls]         │
│                                              │
├──────────────────────────────────────────────┤
│  Status bar: "52 villages tracked | 3 red    │
│  zones | 2 SOS active"                       │
└──────────────────────────────────────────────┘
```

### 8. API Client Integration

All data fetching uses `fetchAPI` from `src/lib/api.js` (created in RFC-001). SOS pin polling uses `setInterval` every 10 seconds, cleaned up on component unmount.

---

## Acceptance Criteria

| # | Criterion | Verifiable By |
|---|-----------|---------------|
| AC1 | Dashboard page loads at `http://localhost:3000/dashboard` and shows a Leaflet map centered on Assam | Visual inspection |
| AC2 | Flood zone markers appear on the map colored red/yellow/green based on risk level | Visual: compare colors against API data |
| AC3 | Safe zone markers appear as green distinct markers with score labels | Visual inspection |
| AC4 | Clicking a village marker shows a popup with name (English + Assamese), elevation, population, risk score | Visual: verify bilingual text |
| AC5 | Clicking a safe zone marker shows score breakdown (4 components) | Visual inspection |
| AC6 | SOS pins appear as visually distinct pulsing red markers | Visual: verify animation |
| AC7 | SOS pins refresh every 10 seconds without full page reload | Observe network tab: periodic `/api/sos` calls |
| AC8 | Layer toggle allows showing/hiding flood zones, safe zones, and SOS pins independently | Click each toggle, verify layers appear/disappear |
| AC9 | Simulation panel sliders allow adjusting river levels and triggering recalculation | Adjust slider, click Recalculate, observe map colors change |
| AC10 | Map loads within 3 seconds (R35) | Measure with browser DevTools |
| AC11 | Status bar shows correct counts of villages, red zones, and active SOS | Compare against API data |
| AC12 | Map renders correctly in Chrome (R45) | Visual inspection in Chrome |

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `frontend/src/components/map/FloodMap.jsx` | NEW | Main Leaflet map with all layers |
| `frontend/src/components/map/VillagePopup.jsx` | NEW | Village click popup with bilingual labels |
| `frontend/src/components/map/SafeZonePopup.jsx` | NEW | Safe zone click popup with score breakdown |
| `frontend/src/components/map/SOSPin.jsx` | NEW | Pulsing SOS marker component |
| `frontend/src/components/alerts/SimulationPanel.jsx` | NEW | River level simulation controls |
| `frontend/src/app/dashboard/page.jsx` | MODIFY | Add map, layout, status bar |
| `frontend/src/app/dashboard/dashboard.module.css` | NEW | Dashboard styles |
| `frontend/src/components/map/map.module.css` | NEW | Map and marker styles |
