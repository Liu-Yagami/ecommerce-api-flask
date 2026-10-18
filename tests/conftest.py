import os

# Must be set BEFORE importing app, because app.py reads them at import time.
os.environ["JWT_SECRET_KEY"] = "test-only-secret-key-0123456789-abcdef"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from app import app as flask_app
from extensions import db


@pytest.fixture
def app():
    """A fresh, empty in-memory database for every test."""
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(client):
    """Register + log in a user. Returns (user_id, auth_headers)."""
    def _make(username="user1"):
        response = client.post("/users", json={
            "first_name": "Test",
            "last_name": username.capitalize(),
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpass123",
        })
        assert response.status_code == 201, response.get_json()
        user_id = response.get_json()["user_id"]

        login = client.post("/login", json={"username": username, "password": "testpass123"})
        token = login.get_json()["access_token"]
        return user_id, {"Authorization": f"Bearer {token}"}
    return _make


@pytest.fixture
def make_product(client):
    """Create a product. Returns its id."""
    def _make(headers, name="Mouse", price=19.99):
        response = client.post("/products", json={"name": name, "price": price}, headers=headers)
        assert response.status_code == 201, response.get_json()
        return response.get_json()["product_id"]
    return _make
