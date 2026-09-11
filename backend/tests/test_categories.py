"""Tests for /categories endpoints."""

from tests.conftest import auth_headers, make_category, make_user


class TestCreateCategory:
    def test_create_category_authenticated(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/categories",
            json={"name": "Science Fiction", "slug": "science-fiction"},
            headers=headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Science Fiction"
        assert body["slug"] == "science-fiction"
        assert "id" in body

    def test_create_category_unauthenticated(self, client):
        resp = client.post(
            "/categories",
            json={"name": "Fantasy", "slug": "fantasy"},
        )
        assert resp.status_code == 401

    def test_create_category_duplicate_name_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        make_category(db, name="Fantasy", slug="fantasy")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/categories",
            json={"name": "Fantasy", "slug": "fantasy-2"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_category_duplicate_slug_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        make_category(db, name="Fantasy", slug="fantasy")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/categories",
            json={"name": "Fantasy 2", "slug": "fantasy"},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_create_category_name_too_short(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/categories",
            json={"name": "A", "slug": "a"},
            headers=headers,
        )
        assert resp.status_code == 422


class TestGetCategories:
    def test_get_categories_empty(self, client):
        resp = client.get("/categories")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_categories_returns_list(self, client, db):
        make_category(db, name="Horror", slug="horror")
        make_category(db, name="Romance", slug="romance")
        resp = client.get("/categories")
        assert resp.status_code == 200
        names = [c["name"] for c in resp.json()]
        assert "Horror" in names
        assert "Romance" in names

    def test_get_categories_sorted_by_name(self, client, db):
        make_category(db, name="Thriller", slug="thriller")
        make_category(db, name="Biography", slug="biography")
        resp = client.get("/categories")
        names = [c["name"] for c in resp.json()]
        assert names == sorted(names)


class TestGetCategory:
    def test_get_category_by_id(self, client, db):
        cat = make_category(db, name="Mystery", slug="mystery")
        resp = client.get(f"/categories/{cat.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Mystery"
        assert resp.json()["slug"] == "mystery"

    def test_get_category_not_found(self, client):
        resp = client.get("/categories/99999")
        assert resp.status_code == 404
