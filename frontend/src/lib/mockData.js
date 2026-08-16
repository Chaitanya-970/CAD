// Demo fallback data — used ONLY when the FastAPI backend (RFC-001/002) is
// unreachable, so the dashboard is still demoable while the backend is
// being brought up. Shape mirrors the real /api/flood-zones and
// /api/safe-zones GeoJSON responses (PRD §12).

export const MOCK_FLOOD_ZONES = {
  type: 'FeatureCollection',
  features: [
    { id: 1, name: 'Majuli', name_assamese: 'মাজুলী', district: 'Majuli', lat: 27.0, lng: 94.2167, elevation_m: 48.5, population_est: 1200, risk_score: 0.85 },
    { id: 2, name: 'Kamalabari', name_assamese: 'কমলাবাৰী', district: 'Majuli', lat: 26.98, lng: 94.15, elevation_m: 52.1, population_est: 900, risk_score: 0.42 },
    { id: 3, name: 'Dhubri Town', name_assamese: 'ধুবুৰী চহৰ', district: 'Dhubri', lat: 26.0189, lng: 89.9856, elevation_m: 31.2, population_est: 3400, risk_score: 0.91 },
    { id: 4, name: 'Golakganj', name_assamese: 'গোলকগঞ্জ', district: 'Dhubri', lat: 26.15, lng: 89.83, elevation_m: 36.4, population_est: 1500, risk_score: 0.28 },
    { id: 5, name: 'Silchar', name_assamese: 'শিলচৰ', district: 'Silchar', lat: 24.8333, lng: 92.7789, elevation_m: 22.5, population_est: 5200, risk_score: 0.15 },
    { id: 6, name: 'Sonai', name_assamese: 'সোণাই', district: 'Silchar', lat: 24.7167, lng: 92.9667, elevation_m: 28.9, population_est: 2100, risk_score: 0.05 },
    { id: 7, name: 'Bilasipara', name_assamese: 'বিলাসীপাৰা', district: 'Dhubri', lat: 26.2333, lng: 90.2333, elevation_m: 33.7, population_est: 1800, risk_score: 0.58 },
    { id: 8, name: 'Garamur', name_assamese: 'গৰমুৰ', district: 'Majuli', lat: 27.05, lng: 94.25, elevation_m: 44.8, population_est: 700, risk_score: 0.73 },
  ].map((v) => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [v.lng, v.lat] },
    properties: {
      id: v.id,
      name: v.name,
      name_assamese: v.name_assamese,
      district: v.district,
      elevation_m: v.elevation_m,
      population_est: v.population_est,
      risk_score: v.risk_score,
      risk_level: v.risk_score >= 0.7 ? 'high' : v.risk_score >= 0.3 ? 'moderate' : 'safe',
    },
  })),
};

export const MOCK_SAFE_ZONES = {
  type: 'FeatureCollection',
  features: [
    { id: 1, name: 'Kamalabari Hill', lat: 26.99, lng: 94.16, elevation_norm: 0.82, road_access_score: 0.7, distance_norm: 0.65, capacity_norm: 0.6, safe_score: 0.72, capacity_est: 500 },
    { id: 2, name: 'Dhubri College Ground', lat: 26.02, lng: 90.0, elevation_norm: 0.55, road_access_score: 0.85, distance_norm: 0.4, capacity_norm: 0.9, safe_score: 0.61, capacity_est: 1200 },
    { id: 3, name: 'Silchar Sports Complex', lat: 24.84, lng: 92.8, elevation_norm: 0.6, road_access_score: 0.9, distance_norm: 0.5, capacity_norm: 0.75, safe_score: 0.66, capacity_est: 800 },
  ].map((z) => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [z.lng, z.lat] },
    properties: { ...z },
  })),
};

export const MOCK_SOS = [
  {
    id: 1,
    from_number: '+91XXXXX00001',
    raw_text: 'Pani ghor bhitor ahise, 4 jon ase',
    parsed_location: 'Majuli',
    parsed_needs: 'rescue, water',
    parsed_people_count: 4,
    latitude: 27.0,
    longitude: 94.2167,
    status: 'active',
    received_at: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    from_number: '+91XXXXX00002',
    raw_text: 'Need medical help near Dhubri town, elderly person injured',
    parsed_location: 'Dhubri Town',
    parsed_needs: 'medical',
    parsed_people_count: 1,
    latitude: 26.0189,
    longitude: 89.9856,
    status: 'active',
    received_at: new Date(Date.now() - 40 * 60 * 1000).toISOString(),
  },
];

export const MOCK_RIVER_STATIONS = [
  { station_name: 'Majuli Station', current_level_m: 45.5, danger_level_m: 47.0, forecast_rise_m: 1.5 },
  { station_name: 'Dhubri Station', current_level_m: 28.0, danger_level_m: 30.0, forecast_rise_m: 2.0 },
  { station_name: 'Silchar Station', current_level_m: 18.0, danger_level_m: 24.0, forecast_rise_m: 1.0 },
];
