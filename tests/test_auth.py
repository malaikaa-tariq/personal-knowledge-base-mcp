import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["ok"] is True
    assert data["status"] == "healthy"

def test_signup_success():
    response = client.post("/auth/signup", json={
        "email": "pytestuser@example.com",
        "password": "strongpassword123",
        "full_name": "Pytest User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "pytestuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_signup_duplicate_email():
    response = client.post("/auth/signup", json={
        "email": "pytestuser@example.com",
        "password": "anotherpassword",
        "full_name": "Duplicate User"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success():
    response = client.post("/auth/login", json={
        "email": "pytestuser@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email": "pytestuser@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_user():
    response = client.post("/auth/login", json={
        "email": "doesnotexist@example.com",
        "password": "whatever123"
    })
    assert response.status_code == 401

def test_me_without_token():
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_me_with_valid_token():
    login_response = client.post("/auth/login", json={
        "email": "pytestuser@example.com",
        "password": "strongpassword123"
    })
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "pytestuser@example.com"

def test_me_with_invalid_token():
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401
