'use client';

import dynamic from 'next/dynamic';
import { useCallback, useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import ModeBanner from '@/components/survival/ModeBanner';
import QueryChat from '@/components/chat/QueryChat';
import VillageListView from '@/components/map/VillageListView';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useSurvivalMode } from '@/hooks/useSurvivalMode';
import { api } from '@/lib/api';
import { MOCK_FLOOD_ZONES, MOCK_SAFE_ZONES, MOCK_SOS, MOCK_RIVER_STATIONS } from '@/lib/mockData';
import styles from './dashboard.module.css';

const FloodMap = dynamic(() => import('@/components/map/FloodMap'), {
  ssr: false,
  loading: () => <div className={styles.mapLoading}>Loading map…</div>,
});

export default function DashboardPage() {
  const { mode, queuedCount, justRestored, queueMessage } = useSurvivalMode();

  const [floodZones, setFloodZones] = useState(null);
  const [safeZones, setSafeZones] = useState(null);
  const [sosList, setSosList] = useState([]);
  const [riverStations, setRiverStations] = useState(MOCK_RIVER_STATIONS);
  const [usingMockData, setUsingMockData] = useState(false);

  const loadCoreData = useCallback(async () => {
    try {
      const [fz, sz] = await Promise.all([api.floodZones(), api.safeZones()]);
      setFloodZones(fz);
      setSafeZones(sz);
      setUsingMockData(false);
    } catch {
      setFloodZones((prev) => prev || MOCK_FLOOD_ZONES);
      setSafeZones((prev) => prev || MOCK_SAFE_ZONES);
      setUsingMockData(true);
    }
  }, []);

  const loadSOS = useCallback(async () => {
    try {
      const data = await api.sos();
      setSosList(Array.isArray(data) ? data : []);
    } catch {
      setSosList((prev) => (prev.length ? prev : MOCK_SOS));
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial data fetch on mount
    loadCoreData();
    loadSOS();
    const interval = setInterval(loadSOS, 10000); // AC7
    return () => clearInterval(interval);
  }, [loadCoreData, loadSOS]);

  const villages = floodZones?.features || [];
  const redZones = villages.filter((v) => v.properties.risk_level === 'high').length;
  const activeSOS = sosList.filter((s) => s.status === 'active').length;

  return (
    <div className={styles.page}>
      <Header>
        <ModeBanner mode={mode} queuedCount={queuedCount} justRestored={justRestored} />
      </Header>

      <ErrorBoundary>
        <div className={styles.body}>
          <div className={styles.mapArea}>
            {mode === 'low-bandwidth' ? (
              <VillageListView villages={villages} />
            ) : (
              <FloodMap
                floodZones={floodZones}
                safeZones={safeZones}
                sosList={sosList}
                riverStations={riverStations}
                lowBandwidth={mode === 'low-bandwidth'}
                offline={mode === 'offline'}
                queueMessage={queueMessage}
                onRecalculated={loadCoreData}
                onSOSStatusChange={(id, status) =>
                  setSosList((prev) => prev.map((x) => (x.id === id ? { ...x, status } : x)))
                }
              />
            )}
          </div>

          <div className={styles.sidePanel}>
            <QueryChat />
          </div>
        </div>

        <div className={styles.statusBar}>
          <span><strong>{villages.length}</strong> villages tracked</span>
          <span><strong>{redZones}</strong> red zones</span>
          <span><strong>{activeSOS}</strong> SOS active</span>
          {usingMockData && <span className={styles.mockBadge}>Demo data — backend unreachable</span>}
        </div>
      </ErrorBoundary>
    </div>
  );
}
