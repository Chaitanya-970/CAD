'use client';

import styles from '../../app/dashboard/dashboard.module.css';

const RISK_LABEL = { high: 'HIGH', moderate: 'MODERATE', safe: 'SAFE' };

export default function VillageListView({ villages }) {
  const sorted = [...villages].sort((a, b) => b.properties.risk_score - a.properties.risk_score);

  return (
    <div className={styles.textOnlyList}>
      <h3>Villages by Risk (text-only view)</h3>
      <table className={styles.villageTable}>
        <thead>
          <tr>
            <th>Village</th>
            <th>District</th>
            <th>Risk</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((v) => (
            <tr key={v.properties.id}>
              <td>
                {v.properties.name}
                {v.properties.name_assamese ? ` (${v.properties.name_assamese})` : ''}
              </td>
              <td>{v.properties.district}</td>
              <td>
                <span className={`popup-risk-badge ${v.properties.risk_level}`}>
                  {RISK_LABEL[v.properties.risk_level] || v.properties.risk_level}
                </span>
              </td>
              <td>{v.properties.risk_score?.toFixed?.(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
