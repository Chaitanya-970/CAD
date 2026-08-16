// API client for the AFIP FastAPI backend.
// BASE_URL points at the local FastAPI dev server (see RFC-001).

export const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const TIMEOUT_MS = 10000; // R12 — 10 second timeout on all API calls

/**
 * fetchAPI - wraps fetch with a base URL, JSON handling, and a 10s timeout.
 * Throws an Error with a `.status` (if available) on failure so callers
 * can distinguish network errors from HTTP errors.
 */
export async function fetchAPI(endpoint, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS);

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  const isFormData =
    typeof FormData !== 'undefined' && options.body instanceof FormData;

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: isFormData
        ? options.headers
        : { 'Content-Type': 'application/json', ...(options.headers || {}) },
    });

    if (!response.ok) {
      const err = new Error(`Request failed: ${response.status} ${response.statusText}`);
      err.status = response.status;
      throw err;
    }

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    if (error.name === 'AbortError') {
      const timeoutError = new Error('Request timed out');
      timeoutError.status = 408;
      throw timeoutError;
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

// --- Typed helpers for each endpoint (PRD §12) ---------------------------

export const api = {
  health: () => fetchAPI('/api/health'),
  floodZones: () => fetchAPI('/api/flood-zones'),
  safeZones: () => fetchAPI('/api/safe-zones'),
  sos: (status) => fetchAPI(`/api/sos${status ? `?status=${status}` : ''}`),
  updateSOSStatus: (id, status) =>
    fetchAPI(`/api/sos/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),
  predict: (payload) =>
    fetchAPI('/api/predict', {
      method: 'POST',
      body: JSON.stringify(payload || {}),
    }),
  alertSMS: (villageId) =>
    fetchAPI('/api/alert/sms', {
      method: 'POST',
      body: JSON.stringify({ village_id: villageId }),
    }),
  alertIVR: (villageId) =>
    fetchAPI('/api/alert/ivr', {
      method: 'POST',
      body: JSON.stringify({ village_id: villageId }),
    }),
  query: (question) =>
    fetchAPI('/api/query', {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),
  cropAssess: (formData) =>
    fetchAPI('/api/crop-assess', {
      method: 'POST',
      body: formData,
    }),
  villages: () => fetchAPI('/api/villages'),
};
