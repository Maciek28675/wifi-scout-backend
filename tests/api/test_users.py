from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user import UserRegisterSchema, UserLoginSchema

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/user/register",
        json={"email": "testuser@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}

def test_login_user():
    client.post(
        "/user/register",
        json={"email": "testuser@example.com", "password": "testpassword"},
    )
    response = client.post(
        "/user/login",
        json={"email": "testuser@example.com", "password": "testpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_not_found():
    response = client.post(
        "/user/login",
        json={"email": "nonexistent@example.com", "password": "testpassword"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_login_user_incorrect_password():
    client.post(
        "/user/register",
        json={"email": "testuser@example.com", "password": "testpassword"},
    )
    response = client.post(
        "/user/login",
        json={"email": "testuser@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}