"""Tests for /publishers endpoints."""

from tests.conftest import auth_headers, make_publisher, make_user


class TestCreatePublisher:
    def test_create_publisher_authenticated(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/publishers",
            json={"name": "Penguin Books"},
            headers=headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Penguin Books"
        assert "id" in body

    def test_create_publisher_unauthenticated(self, client):
        resp = client.post("/publishers", json={"name": "Penguin Books"})
        assert resp.status_code == 401

    def test_create_publisher_duplicate_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        make_publisher(db, name="Penguin Books")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/publishers",
            json={"name": "Penguin Books"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "already exists" in resp.json()["detail"].lower()

    def test_create_publisher_name_too_short(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/publishers",
            json={"name": "X"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestGetPublishers:
    def test_get_publishers_empty(self, client):
        resp = client.get("/publishers")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_publishers_returns_list(self, client, db):
        make_publisher(db, name="Publisher A")
        make_publisher(db, name="Publisher B")
        resp = client.get("/publishers")
        assert resp.status_code == 200
        names = [p["name"] for p in resp.json()]
        assert "Publisher A" in names
        assert "Publisher B" in names

    def test_get_publishers_sorted_by_name(self, client, db):
        make_publisher(db, name="Zebra Press")
        make_publisher(db, name="Acme Books")
        resp = client.get("/publishers")
        names = [p["name"] for p in resp.json()]
        assert names == sorted(names)


class TestGetPublisher:
    def test_get_publisher_by_id(self, client, db):
        publisher = make_publisher(db, name="HarperCollins")
        resp = client.get(f"/publishers/{publisher.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "HarperCollins"

    def test_get_publisher_not_found(self, client):
        resp = client.get("/publishers/99999")
        assert resp.status_code == 404
