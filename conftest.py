import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# override get_db to use test DB instead of real DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# create all tables before tests, drop after
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# basic client — no auth
@pytest.fixture(scope="session")
def client():
    return TestClient(app)

# register + login, return client with auth header set
@pytest.fixture(scope="session")
def auth_client(client):
    # register
    client.post("/auth/register", json={
        "email": "test@test.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpass123"
    })

    # login
    response = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "testpass123"
    })

    token = response.json()["access_token"]

    # set auth header for all subsequent requests
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client