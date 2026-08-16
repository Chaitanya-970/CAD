'use client';

import { useState } from 'react';
import { ChevronUp, ChevronDown, Waves } from 'lucide-react';
import { api } from '@/lib/api';
import styles from './simulation.module.css';

export default function SimulationPanel({ stations, onRecalculated, open, onToggle }) {
  const [levels, setLevels] = useState(() =>
    stations.map((s) => ({
      station_name: s.station_name,
      current_level_m: s.current_level_m,
      danger_level_m: s.danger_level_m,
      forecast_rise_m: s.forecast_rise_m ?? 0,
    }))
  );
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const updateLevel = (idx, field, value) => {
    setLevels((prev) => {
      const next = [...prev];
      next[idx] = { ...next[idx], [field]: Number(value) };
      return next;
    });
  };

  const recalculate = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await api.predict({ river_levels: levels });
      setMessage(`Updated ${res.updated ?? '?'} villages${res.anomalies?.length ? ` — ${res.anomalies.length} anomalies` : ''}`);
      onRecalculated && onRecalculated(res);
    } catch (e) {
      setMessage('Recalculation failed — check backend connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.panel}>
      <button className={styles.header} onClick={onToggle}>
        <span><Waves size={16} /> Simulation</span>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {open && (
        <div className={styles.body}>
          {levels.map((s, idx) => (
            <div key={s.station_name} className={styles.station}>
              <div className={styles.stationName}>{s.station_name}</div>

              <label className={styles.sliderLabel}>
                Current Level: {s.current_level_m.toFixed(1)} m
                <input
                  type="range"
                  min={(s.danger_level_m - 5).toFixed(1)}
                  max={(s.danger_level_m + 5).toFixed(1)}
                  step="0.1"
                  value={s.current_level_m}
                  onChange={(e) => updateLevel(idx, 'current_level_m', e.target.value)}
                />
              </label>

              <label className={styles.sliderLabel}>
                Forecast Rise: {s.forecast_rise_m.toFixed(1)} m
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  value={s.forecast_rise_m}
                  onChange={(e) => updateLevel(idx, 'forecast_rise_m', e.target.value)}
                />
              </label>
            </div>
          ))}

          <button className="btn-primary" style={{ width: '100%' }} onClick={recalculate} disabled={loading}>
            {loading ? 'Recalculating…' : 'Recalculate'}
          </button>

          {message && <div className={styles.message}>{message}</div>}
        </div>
      )}
    </div>
  );
}
