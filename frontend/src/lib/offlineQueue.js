// IndexedDB wrapper for Survival Mode's offline request queue (RFC-006, F8).
// Each queued record: { id, endpoint, method, body, timestamp }

const DB_NAME = 'afip_db';
const STORE_NAME = 'offline_queue';
const DB_VERSION = 1;

function isSupported() {
  return typeof window !== 'undefined' && 'indexedDB' in window;
}

export function openQueue() {
  return new Promise((resolve, reject) => {
    if (!isSupported()) {
      reject(new Error('IndexedDB not supported'));
      return;
    }
    const request = window.indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function addToQueue(entry) {
  const db = await openQueue();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const record = { ...entry, timestamp: Date.now() };
    const req = store.add(record);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function getAllQueued() {
  const db = await openQueue();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

export async function removeFromQueue(id) {
  const db = await openQueue();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.delete(id);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

export async function getQueueCount() {
  try {
    const all = await getAllQueued();
    return all.length;
  } catch {
    return 0;
  }
}
