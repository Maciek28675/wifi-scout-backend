from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session

client = TestClient(app)

def test_create_measurement(db: Session):
    measurement_data = {
        "user_id": 1,
        "latitude": 52.2297,
        "longitude": 21.0122,
        "signalStrength": -75,
        "downloadSpeed": 25.5,
        "uploadSpeed": 10.2,
        "ping": 45
    }
    response = client.post("/measurements/", json=measurement_data)
    assert response.status_code == 201
    assert response.json()["latitude"] == measurement_data["latitude"]
    assert response.json()["longitude"] == measurement_data["longitude"]
    assert response.json()["signalStrength"] == measurement_data["signalStrength"]
    assert response.json()["downloadSpeed"] == measurement_data["downloadSpeed"]
    assert response.json()["uploadSpeed"] == measurement_data["uploadSpeed"]
    assert response.json()["ping"] == measurement_data["ping"]
    assert response.json()["user_id"] == measurement_data["user_id"]

def test_read_measurement(db: Session):
    response = client.get("/measurements/1")
    assert response.status_code == 200
    assert "latitude" in response.json()
    assert "longitude" in response.json()
    assert "signalStrength" in response.json()
    assert "downloadSpeed" in response.json()
    assert "uploadSpeed" in response.json()
    assert "ping" in response.json()

def test_update_measurement(db: Session):
    measurement_data = {
        "latitude": 54.3520,
        "longitude": 18.6466,
        "signalStrength": -80,
        "downloadSpeed": 30.0,
        "uploadSpeed": 15.5,
        "ping": 50
    }
    response = client.put("/measurements/1", json=measurement_data)
    assert response.status_code == 200
    assert response.json()["latitude"] == measurement_data["latitude"]
    assert response.json()["longitude"] == measurement_data["longitude"]
    assert response.json()["signalStrength"] == measurement_data["signalStrength"]
    assert response.json()["downloadSpeed"] == measurement_data["downloadSpeed"]
    assert response.json()["uploadSpeed"] == measurement_data["uploadSpeed"]
    assert response.json()["ping"] == measurement_data["ping"]

def test_delete_measurement(db: Session):
    response = client.delete("/measurements/1")
    assert response.status_code == 204
    response = client.get("/measurements/1")
    assert response.status_code == 404