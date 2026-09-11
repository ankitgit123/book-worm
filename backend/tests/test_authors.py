"""Tests for /authors endpoints."""

from tests.conftest import auth_headers, make_author, make_user


class TestCreateAuthor:
    def test_create_author_authenticated(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/authors",
            json={"name": "Jane Austen", "bio": "English novelist.", "photo_url": None},
            headers=headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Jane Austen"
        assert body["bio"] == "English novelist."
        assert "id" in body

    def test_create_author_unauthenticated(self, client):
        resp = client.post("/authors", json={"name": "Jane Austen"})
        assert resp.status_code == 401

    def test_create_author_minimal(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/authors",
            json={"name": "Anon"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["bio"] is None
        assert resp.json()["photo_url"] is None

    def test_create_author_name_too_short(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/authors",
            json={"name": "X"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestGetAuthors:
    def test_get_authors_empty(self, client):
        resp = client.get("/authors")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_authors_returns_list(self, client, db):
        make_author(db, name="Author A")
        make_author(db, name="Author B")
        resp = client.get("/authors")
        assert resp.status_code == 200
        names = [a["name"] for a in resp.json()]
        assert "Author A" in names
        assert "Author B" in names

    def test_get_authors_sorted_by_name(self, client, db):
        make_author(db, name="Zara")
        make_author(db, name="Alice")
        resp = client.get("/authors")
        names = [a["name"] for a in resp.json()]
        assert names == sorted(names)


class TestGetAuthor:
    def test_get_author_by_id(self, client, db):
        author = make_author(db, name="Leo Tolstoy")
        resp = client.get(f"/authors/{author.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Leo Tolstoy"

    def test_get_author_not_found(self, client):
        resp = client.get("/authors/99999")
        assert resp.status_code == 404
