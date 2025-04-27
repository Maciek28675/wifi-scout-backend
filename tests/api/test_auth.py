from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.schemas.user import UserRegisterSchema, UserLoginSchema
import pytest

client = TestClient(app)

@pytest.fixture
def create_user():
    user_data = UserRegisterSchema(email="testuser@example.com", password="testpassword")
    response = client.post("/user/register", json=user_data.dict())
    assert response.status_code == 200
    return user_data

def test_login_user(create_user):
    login_data = UserLoginSchema(email=create_user.email, password=create_user.password)
    response = client.post("/user/login", json=login_data.dict())
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_not_found():
    login_data = UserLoginSchema(email="nonexistent@example.com", password="testpassword")
    response = client.post("/user/login", json=login_data.dict())
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_login_user_incorrect_password(create_user):
    login_data = UserLoginSchema(email=create_user.email, password="wrongpassword")
    response = client.post("/user/login", json=login_data.dict())
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"