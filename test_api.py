"""CRUD API tests over SQLite (no Postgres needed). Run: pytest -q"""
import pytest
from fastapi.testclient import TestClient

from database import Base, engine
from main import app


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def client():
    return TestClient(app)


def _create(client, **overrides):
    payload = {"title": "Dune", "author": "Herbert", "status": "want_to_read", "rating": None}
    payload.update(overrides)
    resp = client.post("/books", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_health(client):
    assert client.get("/health").json()["status"] in {"ok", "healthy"}


def test_create_then_read(client):
    book = _create(client)
    got = client.get(f"/books/{book['id']}").json()
    assert got["title"] == "Dune" and got["author"] == "Herbert"


def test_read_missing_returns_404(client):
    assert client.get("/books/4242").status_code == 404


def test_filter_by_status(client):
    _create(client, title="A", status="read", rating=5)
    _create(client, title="B", status="want_to_read")
    read = client.get("/books?status=read").json()
    assert [b["title"] for b in read] == ["A"]


def test_update(client):
    book = _create(client)
    updated = client.put(f"/books/{book['id']}", json={"status": "read", "rating": 4}).json()
    assert updated["status"] == "read" and updated["rating"] == 4


def test_delete(client):
    book = _create(client)
    assert client.delete(f"/books/{book['id']}").status_code == 200
    assert client.get(f"/books/{book['id']}").status_code == 404


def test_stats(client):
    _create(client, title="A", status="read", rating=4)
    _create(client, title="B", status="read", rating=2)
    _create(client, title="C", status="want_to_read")
    stats = client.get("/books/stats").json()
    assert stats["total"] == 3
    assert stats["rated_count"] == 2
    assert stats["average_rating"] == 3.0
