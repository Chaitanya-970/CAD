'use client';

import { useState } from 'react';
import styles from './map.module.css';
import { api } from '@/lib/api';

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  return `${hrs}h ago`;
}

const STATUS_CLASS = {
  active: styles.statusActive,
  acknowledged: styles.statusAcknowledged,
  resolved: styles.statusResolved,
};

export default function SOSPin({ sos, onStatusChange, offline = false, queueMessage }) {
  const [updating, setUpdating] = useState(false);
  const [status, setStatus] = useState(sos.status);
  const [queued, setQueued] = useState(false);

  const update = async (next) => {
    setUpdating(true);

    // Survival Mode (RFC-006 AC3): queue status updates while offline.
    if (offline && queueMessage) {
      try {
        await queueMessage(`/api/sos/${sos.id}`, 'PATCH', { status: next });
        setStatus(next);
        setQueued(true);
        onStatusChange && onStatusChange(sos.id, next);
      } catch {
        // leave status as-is; dashboard can retry
      } finally {
        setUpdating(false);
      }
      return;
    }

    try {
      await api.updateSOSStatus(sos.id, next);
      setStatus(next);
      onStatusChange && onStatusChange(sos.id, next);
    } catch {
      // leave status as-is; dashboard can retry
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className={styles.popupBody}>
      <div className="popup-title">🆘 SOS</div>
      <span className={`${styles.statusBadge} ${STATUS_CLASS[status] || ''}`}>{status}</span>

      <div style={{ margin: '8px 0', fontSize: '0.875rem' }}>{sos.raw_text}</div>

      {sos.parsed_needs && (
        <div className={styles.popupRow}><span>Needs</span><span>{sos.parsed_needs}</span></div>
      )}
      {sos.parsed_people_count != null && (
        <div className={styles.popupRow}><span>People</span><span>{sos.parsed_people_count}</span></div>
      )}
      <div className={styles.popupRow}><span>Received</span><span>{timeAgo(sos.received_at)}</span></div>
      {queued && (
        <div style={{ marginTop: 4, fontSize: '0.8rem', color: 'var(--color-warning)' }}>
          Offline — queued, will sync when back online
        </div>
      )}

      <div className={styles.popupActions}>
        {status !== 'acknowledged' && (
          <button className={styles.popupActionBtn} disabled={updating} onClick={() => update('acknowledged')}>
            Acknowledge
          </button>
        )}
        {status !== 'resolved' && (
          <button className={styles.popupActionBtn} disabled={updating} onClick={() => update('resolved')}>
            Resolve
          </button>
        )}
      </div>
    </div>
  );
}
