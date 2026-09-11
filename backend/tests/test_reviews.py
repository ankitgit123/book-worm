"""Tests for /books/{book_id}/reviews and /reviews endpoints."""

from tests.conftest import (
    auth_headers,
    make_author,
    make_book,
    make_publisher,
    make_user,
)


def _setup_purchase(client, db, book_id, headers):
    """Helper: create an address, add the book to cart, and place an order."""
    from tests.conftest import make_user  # noqa – already imported above

    addr_resp = client.post(
        "/addresses",
        json={
            "full_name": "John Doe",
            "address_line1": "123 St",
            "city": "City",
            "state": "ST",
            "postal_code": "00000",
            "country": "US",
        },
        headers=headers,
    )
    addr_id = addr_resp.json()["id"]
    client.post("/cart/items", json={"book_id": book_id, "quantity": 1}, headers=headers)
    client.post("/orders", json={"address_id": addr_id, "gift_points_used": 0}, headers=headers)


class TestCreateReview:
    def test_create_review_after_purchase(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, headers)
        resp = client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 5, "comment": "Great book!"},
            headers=headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["rating"] == 5
        assert body["comment"] == "Great book!"
        assert body["book_id"] == book.id

    def test_create_review_without_purchase_forbidden(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 4},
            headers=headers,
        )
        assert resp.status_code == 403

    def test_create_review_duplicate_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, headers)
        client.post(f"/books/{book.id}/reviews", json={"rating": 5}, headers=headers)
        resp = client.post(
            f"/books/{book.id}/reviews", json={"rating": 3}, headers=headers
        )
        assert resp.status_code == 400

    def test_create_review_invalid_rating(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 6},
            headers=headers,
        )
        assert resp.status_code == 422

    def test_create_review_book_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/books/99999/reviews",
            json={"rating": 5},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_create_review_updates_book_rating(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, headers)
        client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 4, "comment": "Good"},
            headers=headers,
        )
        book_resp = client.get(f"/books/{book.id}").json()
        assert float(book_resp["average_rating"]) == 4.0


class TestGetBookReviews:
    def test_get_reviews_empty(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        resp = client.get(f"/books/{book.id}/reviews")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_reviews_returns_reviews(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, headers)
        client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 5, "comment": "Excellent"},
            headers=headers,
        )
        resp = client.get(f"/books/{book.id}/reviews")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["comment"] == "Excellent"

    def test_get_reviews_book_not_found(self, client):
        resp = client.get("/books/99999/reviews")
        assert resp.status_code == 404


class TestUpdateReview:
    def test_update_review(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, headers)
        review_id = client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 3, "comment": "Okay"},
            headers=headers,
        ).json()["id"]
        resp = client.put(
            f"/reviews/{review_id}",
            json={"rating": 5, "comment": "Changed my mind, great!"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["rating"] == 5
        assert resp.json()["comment"] == "Changed my mind, great!"

    def test_update_review_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.put(
            "/reviews/99999",
            json={"rating": 5, "comment": "X"},
            headers=headers,
        )
        assert resp.status_code == 404


class TestDeleteReview:
    def test_delete_review(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, headers)
        review_id = client.post(
            f"/books/{book.id}/reviews",
            json={"rating": 5},
            headers=headers,
        ).json()["id"]
        resp = client.delete(f"/reviews/{review_id}", headers=headers)
        assert resp.status_code == 200
        assert client.get(f"/books/{book.id}/reviews").json() == []

    def test_delete_review_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete("/reviews/99999", headers=headers)
        assert resp.status_code == 404

    def test_cannot_delete_another_users_review(self, client, db):
        make_user(db, email="user1@example.com", password="pass1234")
        make_user(db, email="user2@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        h1 = auth_headers(client, email="user1@example.com", password="pass1234")
        h2 = auth_headers(client, email="user2@example.com", password="pass1234")
        _setup_purchase(client, db, book.id, h1)
        review_id = client.post(
            f"/books/{book.id}/reviews", json={"rating": 5}, headers=h1
        ).json()["id"]
        resp = client.delete(f"/reviews/{review_id}", headers=h2)
        assert resp.status_code == 404
