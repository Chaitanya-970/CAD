'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchAPI } from '@/lib/api';
import { addToQueue, getAllQueued, getQueueCount, removeFromQueue } from '@/lib/offlineQueue';

/**
 * useSurvivalMode — detects network quality and manages offline message
 * queuing, per RFC-006 / PRD F8.
 *
 * mode: 'full' | 'low-bandwidth' | 'offline'
 *
 * Detection:
 *  1. navigator.connection (Chromium-only, R45) — effectiveType 4g/3g -> full,
 *     2g/slow-2g -> low-bandwidth.
 *  2. Fallback: navigator.onLine — true -> full, false -> offline.
 */
export function useSurvivalMode() {
  const [mode, setMode] = useState(() =>
    typeof navigator === 'undefined' ? 'full' : navigator.onLine ? 'full' : 'offline'
  );
  const [queuedCount, setQueuedCount] = useState(0);
  const [justRestored, setJustRestored] = useState(false);
  const wasOffline = useRef(false);

  const computeMode = useCallback(() => {
    if (typeof navigator === 'undefined') return 'full';

    if (!navigator.onLine) return 'offline';

    const conn =
      navigator.connection || navigator.mozConnection || navigator.webkitConnection;

    if (conn && conn.effectiveType) {
      if (conn.effectiveType === '2g' || conn.effectiveType === 'slow-2g') {
        return 'low-bandwidth';
      }
      return 'full';
    }

    // Fallback: navigator.onLine only, no 2G/3G/4G granularity (R18)
    return 'full';
  }, []);

  const refreshQueueCount = useCallback(async () => {
    const count = await getQueueCount();
    setQueuedCount(count);
  }, []);

  const queueMessage = useCallback(
    async (endpoint, method, body) => {
      await addToQueue({ endpoint, method, body });
      await refreshQueueCount();
    },
    [refreshQueueCount]
  );

  const flushQueue = useCallback(async () => {
    let items = [];
    try {
      items = await getAllQueued();
    } catch {
      return;
    }
    if (items.length === 0) return;

    let sentCount = 0;
    for (const item of items) {
      try {
        await fetchAPI(item.endpoint, {
          method: item.method,
          body: item.body ? JSON.stringify(item.body) : undefined,
        });
        await removeFromQueue(item.id);
        sentCount += 1;
      } catch {
        // Leave it queued — will retry on next flush
      }
    }
    await refreshQueueCount();
    if (sentCount > 0) {
      setJustRestored(true);
      setTimeout(() => setJustRestored(false), 5000);
    }
  }, [refreshQueueCount]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- syncing with browser network APIs on mount
    setMode(computeMode());
    refreshQueueCount();

    const handleChange = () => {
      const next = computeMode();
      setMode((prev) => {
        if (prev === 'offline' && next !== 'offline') {
          wasOffline.current = true;
          flushQueue();
        }
        return next;
      });
    };

    window.addEventListener('online', handleChange);
    window.addEventListener('offline', handleChange);

    const conn =
      navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (conn) {
      conn.addEventListener('change', handleChange);
    }

    // Poll navigator.onLine every 10s as a belt-and-braces auto-flush trigger
    const interval = setInterval(() => {
      if (navigator.onLine) {
        flushQueue();
      }
    }, 10000);

    return () => {
      window.removeEventListener('online', handleChange);
      window.removeEventListener('offline', handleChange);
      if (conn) conn.removeEventListener('change', handleChange);
      clearInterval(interval);
    };
  }, [computeMode, flushQueue, refreshQueueCount]);

  return { mode, queuedCount, justRestored, queueMessage, flushQueue };
}
