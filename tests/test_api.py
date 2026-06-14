"""Integration tests against the FastAPI app + isolated SQLite DB."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_books_empty_initially(client):
    r = client.get("/books")
    assert r.status_code == 200
    assert r.json() == []


def test_create_book_returns_201_and_id(client):
    r = client.post(
        "/books",
        json={"title": "DDIA", "author": "Kleppmann", "status": "read", "rating": 5},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    assert body["title"] == "DDIA"
    assert body["rating"] == 5


def test_filter_books_by_status(client):
    client.post(
        "/books", json={"title": "A", "author": "x", "status": "read", "rating": 4}
    )
    client.post("/books", json={"title": "B", "author": "x", "status": "reading"})
    client.post("/books", json={"title": "C", "author": "x", "status": "want_to_read"})

    r = client.get("/books?status=read")
    assert r.status_code == 200
    titles = [b["title"] for b in r.json()]
    assert titles == ["A"]


def test_get_one_404(client):
    r = client.get("/books/9999")
    assert r.status_code == 404


def test_update_book_partial(client):
    book = client.post(
        "/books", json={"title": "Dune", "author": "Herbert", "status": "reading"}
    ).json()

    r = client.put(
        f"/books/{book['id']}", json={"status": "read", "rating": 5}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "read"
    assert body["rating"] == 5
    assert body["title"] == "Dune"  # untouched


def test_delete_book(client):
    book = client.post(
        "/books", json={"title": "x", "author": "x", "status": "want_to_read"}
    ).json()

    r = client.delete(f"/books/{book['id']}")
    assert r.status_code == 200

    r = client.get(f"/books/{book['id']}")
    assert r.status_code == 404


def test_stats_aggregates(client):
    client.post(
        "/books", json={"title": "A", "author": "x", "status": "read", "rating": 5}
    )
    client.post(
        "/books", json={"title": "B", "author": "x", "status": "read", "rating": 3}
    )
    client.post("/books", json={"title": "C", "author": "x", "status": "reading"})

    r = client.get("/books/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert body["by_status"] == {"read": 2, "reading": 1}
    assert body["rated_count"] == 2
    assert body["average_rating"] == 4.0


def test_route_order_stats_before_dynamic_id(client):
    """Confirms that /books/stats matches the literal route, not /books/{id}."""
    r = client.get("/books/stats")
    assert r.status_code == 200
    assert "total" in r.json()
