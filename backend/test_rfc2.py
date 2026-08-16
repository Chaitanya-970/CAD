import urllib.request
import json

def check():
    print("Testing /api/predict with empty payload (trigger DB fetch)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/predict", data=b"{}", headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    predict_data = json.loads(res.read().decode('utf-8'))
    
    assert "anomalies" in predict_data
    assert "updated" in predict_data
    
    print("\nTesting /api/flood-zones...")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/flood-zones")
    flood_data = json.loads(res.read().decode('utf-8'))
    assert flood_data['type'] == 'FeatureCollection'
    assert len(flood_data['features']) > 0
    assert 'risk_score' in flood_data['features'][0]['properties']

    print("\nTesting /api/safe-zones...")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/safe-zones")
    safe_data = json.loads(res.read().decode('utf-8'))
    assert safe_data['type'] == 'FeatureCollection'
    
    if len(safe_data['features']) > 0:
        props = safe_data['features'][0]['properties']
        assert 'safe_score' in props
        assert 'road_access_score' in props
        
        # Test sorting
        if len(safe_data['features']) > 1:
            score1 = safe_data['features'][0]['properties']['safe_score']
            score2 = safe_data['features'][1]['properties']['safe_score']
            assert score1 >= score2, "Safe zones not sorted properly!"

    # AC6 specific test: Predict with extreme river levels
    extreme_payload = {
        "river_levels": [
            {
                "station_name": "ব্ৰহ্মপুত্ৰ মাজুলী",
                "current_level_m": 120.0,
                "danger_level_m": 85.0,
                "forecast_rise_m": 1.0
            }
        ]
    }
    print("\nTesting Extreme Flood Scenario for AC6 exclusion...")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/predict", 
        data=json.dumps(extreme_payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)
    
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/safe-zones")
    extreme_safe_data = json.loads(res.read().decode('utf-8'))
    
    assert len(extreme_safe_data['features']) < len(safe_data['features']) or len(extreme_safe_data['features']) == 0, "AC6 FAIL: Safe zones not excluded under extreme flood!"
    
    print("\nAll assertions passed successfully! AC6 and anomalies verified.")

if __name__ == '__main__':
    check()
