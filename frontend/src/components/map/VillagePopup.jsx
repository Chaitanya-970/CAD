'use client';

import { useState } from 'react';
import styles from './map.module.css';
import { api } from '@/lib/api';

const RISK_LABEL = { high: 'HIGH', moderate: 'MODERATE', safe: 'SAFE' };

export default function VillagePopup({ village, onAlertSent, offline = false, queueMessage }) {
  const [sending, setSending] = useState(null); // 'sms' | 'ivr' | null
  const [result, setResult] = useState(null);

  const p = village.properties;

  const sendAlert = async (type) => {
    setSending(type);
    setResult(null);

    // Survival Mode (RFC-006 AC3): when offline, queue the action in
    // IndexedDB instead of attempting the network call.
    if (offline && queueMessage) {
      try {
        await queueMessage(`/api/alert/${type}`, 'POST', { village_id: p.id });
        setResult({ ok: true, text: 'Offline — queued, will send when back online' });
      } catch {
        setResult({ ok: false, text: 'Could not queue — try again' });
      } finally {
        setSending(null);
      }
      return;
    }

    try {
      const res = type === 'sms' ? await api.alertSMS(p.id) : await api.alertIVR(p.id);
      setResult({ ok: true, text: `Sent to ${res.recipients ?? '?'} recipients` });
      onAlertSent && onAlertSent(p.id, type);
    } catch (e) {
      setResult({ ok: false, text: 'Send failed — retry?' });
    } finally {
      setSending(null);
    }
  };

  return (
    <div className={styles.popupBody}>
      <div className="popup-title">
        {p.name}
        {p.name_assamese && <span className={styles.popupNameAs}>({p.name_assamese})</span>}
      </div>
      <span className={`popup-risk-badge ${p.risk_level}`}>{RISK_LABEL[p.risk_level] || p.risk_level}</span>

      <div className={styles.popupRow}><span>District</span><span>{p.district}</span></div>
      <div className={styles.popupRow}><span>Elevation</span><span>{p.elevation_m} m</span></div>
      <div className={styles.popupRow}><span>Population</span><span>~{p.population_est?.toLocaleString?.() ?? p.population_est}</span></div>
      <div className={styles.popupRow}><span>Risk Score</span><span>{p.risk_score?.toFixed?.(2) ?? p.risk_score}</span></div>

      <div className={styles.popupActions}>
        <button
          className={styles.popupActionBtn}
          disabled={sending !== null}
          onClick={() => sendAlert('sms')}
        >
          {sending === 'sms' ? 'Sending…' : 'Send SMS'}
        </button>
        <button
          className={styles.popupActionBtn}
          disabled={sending !== null}
          onClick={() => sendAlert('ivr')}
        >
          {sending === 'ivr' ? 'Calling…' : 'Send IVR'}
        </button>
      </div>
      {result && (
        <div style={{ marginTop: 6, fontSize: '0.8rem', color: result.ok ? 'var(--color-safe)' : 'var(--color-danger)' }}>
          {result.text}
        </div>
      )}
    </div>
  );
}
