'use client';

import 'leaflet/dist/leaflet.css';
import { useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import VillagePopup from './VillagePopup';
import SafeZonePopup from './SafeZonePopup';
import SOSPin from './SOSPin';
import SimulationPanel from '../alerts/SimulationPanel';
import styles from './map.module.css';

const ASSAM_CENTER = [26.2, 92.9];
const DEFAULT_ZOOM = 8;

const RISK_COLOR = { high: '#D64545', moderate: '#E8A838', safe: '#2D8B5E' };

function radiusFromPopulation(pop) {
  if (!pop) return 6;
  return Math.max(6, Math.min(22, Math.sqrt(pop) / 4));
}

function sosIcon(status) {
  return L.divIcon({
    className: '',
    html: `<div class="${styles.sosDivIcon} ${status !== 'active' ? styles.sosDivIconAck : ''}"></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
}

const safeZoneIcon = L.divIcon({
  className: '',
  html: `<div class="${styles.safeZoneDivIcon}"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 14],
});

/** Keeps the map's tile layer in sync with survival mode without remounting the map */
function TileLayerToggle({ enabled }) {
  const map = useMap();
  useEffect(() => {
    // Leaflet needs a resize nudge after the container/layout changes
    setTimeout(() => map.invalidateSize(), 200);
  }, [enabled, map]);
  return enabled ? (
    <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    />
  ) : null;
}

export default function FloodMap({
  floodZones,
  safeZones,
  sosList = [],
  riverStations = [],
  lowBandwidth = false,
  offline = false,
  queueMessage,
  onRecalculated,
  onSOSStatusChange,
}) {
  const [showFlood, setShowFlood] = useState(true);
  const [showSafe, setShowSafe] = useState(true);
  const [showSOS, setShowSOS] = useState(true);
  const [simOpen, setSimOpen] = useState(false);

  const villageMarkers = useMemo(() => {
    const villages = floodZones?.features || [];
    return villages.map((v) => {
      const [lng, lat] = v.geometry.coordinates;
      const p = v.properties;
      return (
        <CircleMarker
          key={`v-${p.id}`}
          center={[lat, lng]}
          radius={radiusFromPopulation(p.population_est)}
          pathOptions={{
            color: RISK_COLOR[p.risk_level] || '#999',
            fillColor: RISK_COLOR[p.risk_level] || '#999',
            fillOpacity: 0.7,
            weight: 1.5,
          }}
        >
          <Popup>
            <VillagePopup village={v} offline={offline} queueMessage={queueMessage} />
          </Popup>
        </CircleMarker>
      );
    });
  }, [floodZones, offline, queueMessage]);

  const safeZoneMarkers = useMemo(() => {
    const safeZoneFeatures = safeZones?.features || [];
    return safeZoneFeatures.map((z) => {
      const [lng, lat] = z.geometry.coordinates;
      return (
        <Marker key={`sz-${z.properties.id}`} position={[lat, lng]} icon={safeZoneIcon}>
          <Popup>
            <SafeZonePopup safeZone={z} />
          </Popup>
        </Marker>
      );
    });
  }, [safeZones]);

  const sosMarkers = useMemo(
    () =>
      sosList.map((s) => (
        <Marker key={`sos-${s.id}`} position={[s.latitude, s.longitude]} icon={sosIcon(s.status)}>
          <Popup>
            <SOSPin sos={s} offline={offline} queueMessage={queueMessage} onStatusChange={onSOSStatusChange} />
          </Popup>
        </Marker>
      )),
    [sosList, offline, queueMessage, onSOSStatusChange]
  );

  return (
    <div className={styles.mapWrapper}>
      <MapContainer center={ASSAM_CENTER} zoom={DEFAULT_ZOOM} className={styles.mapContainer} preferCanvas>
        <TileLayerToggle enabled={!lowBandwidth && !offline} />
        {showFlood && villageMarkers}
        {showSafe && safeZoneMarkers}
        {showSOS && sosMarkers}
      </MapContainer>

      <div className={styles.layerControl}>
        <label>
          <input type="checkbox" checked={showFlood} onChange={(e) => setShowFlood(e.target.checked)} />
          Flood Zones
        </label>
        <label>
          <input type="checkbox" checked={showSafe} onChange={(e) => setShowSafe(e.target.checked)} />
          Safe Zones
        </label>
        <label>
          <input type="checkbox" checked={showSOS} onChange={(e) => setShowSOS(e.target.checked)} />
          SOS Pins
        </label>
      </div>

      <SimulationPanel
        stations={riverStations}
        open={simOpen}
        onToggle={() => setSimOpen((o) => !o)}
        onRecalculated={onRecalculated}
      />
    </div>
  );
}
