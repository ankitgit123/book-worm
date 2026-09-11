"""Tests for /wishlist endpoints."""

from tests.conftest import (
    auth_headers,
    make_author,
    make_book,
    make_publisher,
    make_user,
)


class TestGetWishlist:
    def test_get_wishlist_initially_empty(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.get("/wishlist", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_wishlist_unauthenticated(self, client):
        resp = client.get("/wishlist")
        assert resp.status_code == 401


class TestAddToWishlist:
    def test_add_book_to_wishlist(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/wishlist",
            json={"book_id": book.id},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["book"]["id"] == book.id

    def test_add_same_book_returns_existing(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        first = client.post("/wishlist", json={"book_id": book.id}, headers=headers)
        second = client.post("/wishlist", json={"book_id": book.id}, headers=headers)
        assert second.status_code == 200
        # Should return the same wishlist entry (same id)
        assert first.json()["id"] == second.json()["id"]
        # Wishlist should contain only one entry
        listing = client.get("/wishlist", headers=headers).json()
        assert len(listing) == 1

    def test_add_inactive_book_to_wishlist(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, is_active=False)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post("/wishlist", json={"book_id": book.id}, headers=headers)
        assert resp.status_code == 404

    def test_add_nonexistent_book_to_wishlist(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post("/wishlist", json={"book_id": 99999}, headers=headers)
        assert resp.status_code == 404


class TestRemoveFromWishlist:
    def test_remove_book_from_wishlist(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        client.post("/wishlist", json={"book_id": book.id}, headers=headers)
        resp = client.delete(f"/wishlist/{book.id}", headers=headers)
        assert resp.status_code == 200
        listing = client.get("/wishlist", headers=headers).json()
        assert listing == []

    def test_remove_book_not_in_wishlist(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete("/wishlist/99999", headers=headers)
        assert resp.status_code == 404


class TestClearWishlist:
    def test_clear_wishlist(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book1 = make_book(db, author=author, publisher=publisher, title="Book1")
        book2 = make_book(db, author=author, publisher=publisher, title="Book2")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        client.post("/wishlist", json={"book_id": book1.id}, headers=headers)
        client.post("/wishlist", json={"book_id": book2.id}, headers=headers)
        resp = client.delete("/wishlist", headers=headers)
        assert resp.status_code == 200
        assert client.get("/wishlist", headers=headers).json() == []

    def test_clear_wishlist_when_empty(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete("/wishlist", headers=headers)
        assert resp.status_code == 200
