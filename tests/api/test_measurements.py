import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)

def test_create_measurement():
    payload = {
        "latitude": 52.2297,
        "longitude": 21.0122,
        "signal_strength": -80,
        "download_speed": 8.5,
        "upload_speed": 3.2,
        "ping": 42,
        "timestamp": "2025-05-19T15:30:00"
    }
    response = client.post("/measurements/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["latitude"] == payload["latitude"]
    assert data["longitude"] == payload["longitude"]
    assert data["download_speed"] == payload["download_speed"]
    assert data["color"] == "red"  # download_speed < 10 = red

def test_get_measurements():
    response = client.get("/measurements/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_measurement():
    payload = {
        "latitude": 54.372,
        "longitude": 18.638,
        "signal_strength": -65,
        "download_speed": 12.5,
        "upload_speed": 6.8,
        "ping": 25,
        "timestamp": "2025-05-19T16:00:00"
    }
    create_response = client.post("/measurements/", json=payload)
    assert create_response.status_code == 201
    measurement_id = create_response.json()["id"]

    # Now get it
    response = client.get(f"/measurements/{measurement_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == measurement_id
    assert data["latitude"] == payload["latitude"]
    assert data["color"] == "green"  # download_speed >= 10 = green

def test_update_measurement():
    payload = {
        "latitude": 50.049,
        "longitude": 19.944,
        "download_speed": 15.0,
        "timestamp": "2025-05-19T16:30:00"
    }
    create_response = client.post("/measurements/", json=payload)
    assert create_response.status_code == 201
    measurement_id = create_response.json()["id"]

    # Update it
    update_payload = {
        "download_speed": 5.0,  # Change from green to red
        "ping": 60
    }
    response = client.put(f"/measurements/{measurement_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["download_speed"] == update_payload["download_speed"]
    assert data["ping"] == update_payload["ping"]
    assert data["color"] == "red"  # Should change to red

def test_delete_measurement():
    payload = {
        "latitude": 51.107,
        "longitude": 17.038,
        "download_speed": 9.5,
        "timestamp": "2025-05-19T17:00:00"
    }
    create_response = client.post("/measurements/", json=payload)
    assert create_response.status_code == 201
    measurement_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/measurements/{measurement_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Pomiar usunięty"

    # Verify it's deleted
    get_response = client.get(f"/measurements/{measurement_id}")
    assert get_response.status_code == 404

def test_color_based_on_speed():
    # Test red color
    payload_slow = {
        "latitude": 53.430,
        "longitude": 14.553,
        "download_speed": 4.5,
        "timestamp": "2025-05-19T17:30:00"
    }
    slow_response = client.post("/measurements/", json=payload_slow)
    assert slow_response.status_code == 201
    assert slow_response.json()["color"] == "red"

    # Test green color
    payload_fast = {
        "latitude": 53.430,
        "longitude": 14.553,
        "download_speed": 25.0,
        "timestamp": "2025-05-19T17:35:00"
    }
    fast_response = client.post("/measurements/", json=payload_fast)
    assert fast_response.status_code == 201
    assert fast_response.json()["color"] == "green"
