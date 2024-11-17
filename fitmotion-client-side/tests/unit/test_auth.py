import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "test123456",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "test123456"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_reset_password():
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": "test@example.com"
        }
    )
    assert response.status_code == 200