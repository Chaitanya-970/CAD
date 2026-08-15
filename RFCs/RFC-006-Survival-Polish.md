# RFC-006: Survival Mode & Polish

> **Features:** F8 (Survival Mode), F21 (Request Logging & Diagnostics)
> **Predecessors:** RFC-003 (needs the map dashboard to exist for downgrading)
> **Successors:** None (final RFC)
> **Complexity:** Medium
> **Primary Track:** Frontend + Backend
> **Applicable Rules:** R6, R17, R18, R19, R21, R24, R26, R35, R45, R47

---

## Summary

This is the final RFC. It adds Survival Mode (bandwidth detection, UI downgrading, and offline message queuing) and request logging middleware. It also covers final polish: responsive layout adjustments, loading states, and error boundaries.

---

## Technical Specification

### 1. Frontend: `hooks/useSurvivalMode.js` (R24)

A custom React hook that detects network quality and manages offline message queuing.

```javascript
'use client';

export function useSurvivalMode() {
  // Returns: { mode, queuedCount, queueMessage, flushQueue }
  // mode: 'full' | 'low-bandwidth' | 'offline'
  
  // DETECTION LOGIC:
  // 1. Check navigator.connection (Chromium only — R45)
  //    - effectiveType === '4g' → 'full'
  //    - effectiveType === '3g' → 'full'
  //    - effectiveType === '2g' or 'slow-2g' → 'low-bandwidth'
  // 2. Fallback: navigator.onLine (R18 for F8)
  //    - true → 'full'
  //    - false → 'offline'
  // 3. Listen for 'online'/'offline' events and connection 'change' events
  
  // QUEUE LOGIC:
  // - queueMessage(endpoint, method, body): stores request in IndexedDB
  // - flushQueue(): replays all queued requests via fetchAPI, removes on success
  // - Auto-flush: setInterval checks navigator.onLine every 10 seconds
  //   On transition from offline → online: trigger flushQueue()
  
  // PERSISTENCE:
  // - IndexedDB store name: 'afip_offline_queue'
  // - Each record: { id, endpoint, method, body, timestamp }
  // - Queue survives browser refresh
}
```

### 2. Frontend: `components/survival/ModeBanner.jsx`

A sticky banner at the top of the dashboard:

| Mode | Banner Color | Text |
|------|-------------|------|
| `full` | Hidden (no banner) | — |
| `low-bandwidth` | Yellow (#f59e0b) | "⚡ Low-Bandwidth Mode — Map tiles disabled" |
| `offline` | Red (#ef4444) | "📡 Offline — {N} Messages Queued" |

On transition from offline to online, briefly show green banner: "✅ Back online — {N} queued messages sent"

### 3. Frontend: Dashboard Integration

When `mode === 'low-bandwidth'`:
- Disable OpenStreetMap tile layer (show a plain gray background)
- Switch map to a text-only fallback: a list/table of villages with their risk level, sorted by risk score descending

When `mode === 'offline'`:
- All `fetchAPI` calls that would fail are intercepted and queued via `queueMessage`
- Show queued count in the banner and status bar

### 4. Frontend: IndexedDB Wrapper (`lib/offlineQueue.js`)

```javascript
const DB_NAME = 'afip_db';
const STORE_NAME = 'offline_queue';
const DB_VERSION = 1;

export function openQueue() { ... }       // Open/create IndexedDB
export function addToQueue(request) { ... } // Add a request to the queue
export function getAllQueued() { ... }      // Get all queued requests
export function removeFromQueue(id) { ... } // Remove a processed request
export function getQueueCount() { ... }    // Get count for banner display
```

### 5. Backend: Request Logging Middleware (F21)

Add logging middleware to FastAPI `main.py`:

```python
import logging
import time
from fastapi import Request

logger = logging.getLogger("afip")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration_ms:.0f}ms)")
    return response
```

Additionally, add logging to each external API call in services (Twilio, Gemini, Groq, Bhashini):
```python
logger.info(f"[Twilio] SMS to {phone} — {status} ({duration_ms}ms)")
logger.info(f"[Gemini] query — {status} ({duration_ms}ms)")
logger.error(f"[Bhashini] TTS failed — {error}")
```

### 6. Frontend: Error Boundary

Wrap the dashboard in a React Error Boundary that catches render errors and shows a friendly message instead of a blank screen (R19):

```jsx
// components/ErrorBoundary.jsx
'use client';
export class ErrorBoundary extends React.Component {
  state = { hasError: false };
  static getDerivedStateFromError(error) { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return <div className="error-fallback">Something went wrong. Please refresh the page.</div>;
    }
    return this.props.children;
  }
}
```

### 7. Final Polish Checklist

Items that must be verified before demo:
- [ ] All loading states show a spinner or skeleton, not a blank space
- [ ] All API errors show user-friendly messages, not raw errors (R19)
- [ ] Map occupies full viewport on 1366x768 screen
- [ ] Page title is "AFIP — Flood Intelligence" (not "localhost:3000")
- [ ] Favicon is set (can be a simple water-drop emoji as a PNG)
- [ ] No console errors in Chrome DevTools
- [ ] Demo data uses real Assamese place names (R47)

---

## Acceptance Criteria

| # | Criterion | Verifiable By |
|---|-----------|---------------|
| AC1 | `useSurvivalMode` hook returns `{ mode: 'full' }` on a normal connection | Console log in Chrome |
| AC2 | Disabling Wi-Fi changes mode to `'offline'` and shows red banner | Toggle Wi-Fi off, observe banner |
| AC3 | In offline mode, submitting an action (e.g., "Send Alert") queues the request in IndexedDB | Open DevTools → Application → IndexedDB → verify record |
| AC4 | Re-enabling Wi-Fi triggers auto-flush — queued requests are sent and banner shows green confirmation | Toggle Wi-Fi on, observe network requests |
| AC5 | Queued messages persist across browser refresh | Queue a message, refresh page, verify count in banner |
| AC6 | In low-bandwidth mode, map tiles are disabled and a text-only village list is shown | Throttle to 2G in DevTools Network tab |
| AC7 | Backend logs every API request with method, path, status code, and duration | Observe terminal output during API calls |
| AC8 | Backend logs every external API call (Twilio, Gemini, Bhashini) with service name and duration | Trigger an alert, observe log lines |
| AC9 | Error boundary catches render errors and shows "Something went wrong" message | Intentionally break a component, verify fallback |
| AC10 | No console errors on a clean page load in Chrome | Open DevTools Console |
| AC11 | Dashboard renders correctly on 1366x768 viewport | Resize browser window |

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `frontend/src/hooks/useSurvivalMode.js` | NEW | Bandwidth detection + mode management |
| `frontend/src/lib/offlineQueue.js` | NEW | IndexedDB wrapper for offline queuing |
| `frontend/src/components/survival/ModeBanner.jsx` | NEW | Survival mode status banner |
| `frontend/src/components/survival/survival.module.css` | NEW | Banner styles |
| `frontend/src/components/ErrorBoundary.jsx` | NEW | React error boundary |
| `frontend/src/app/dashboard/page.jsx` | MODIFY | Integrate survival mode hook and banner |
| `backend/app/main.py` | MODIFY | Add request logging middleware |
| `backend/app/services/twilio_sms.py` | MODIFY | Add per-call logging |
| `backend/app/services/twilio_voice.py` | MODIFY | Add per-call logging |
| `backend/app/services/llm.py` | MODIFY | Add per-call logging |
| `backend/app/services/bhashini.py` | MODIFY | Add per-call logging |
