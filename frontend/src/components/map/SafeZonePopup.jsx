'use client';

import styles from './map.module.css';

const COMPONENTS = [
  { key: 'elevation_norm', label: 'Elevation', weight: '40%' },
  { key: 'road_access_score', label: 'Road Access', weight: '25%' },
  { key: 'distance_norm', label: 'Distance', weight: '20%' },
  { key: 'capacity_norm', label: 'Capacity', weight: '15%' },
];

export default function SafeZonePopup({ safeZone }) {
  const p = safeZone.properties;

  return (
    <div className={styles.popupBody}>
      <div className="popup-title">🟢 {p.name}</div>
      <div className={styles.popupRow}>
        <span>Safe Score</span>
        <span>{p.safe_score?.toFixed?.(2) ?? p.safe_score}</span>
      </div>

      {COMPONENTS.map((c) => {
        const value = p[c.key];
        if (value === undefined || value === null) return null;
        return (
          <div key={c.key} className={styles.scoreBar}>
            <span style={{ width: 90 }}>{c.label} ({c.weight})</span>
            <div className={styles.scoreBarTrack}>
              <div className={styles.scoreBarFill} style={{ width: `${Math.round(value * 100)}%` }} />
            </div>
          </div>
        );
      })}

      <div className={styles.popupRow}>
        <span>Capacity</span>
        <span>~{p.capacity_est?.toLocaleString?.() ?? p.capacity_est} people</span>
      </div>
    </div>
  );
}
