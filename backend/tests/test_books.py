"""Tests for /books endpoints."""

from decimal import Decimal

from tests.conftest import (
    auth_headers,
    make_author,
    make_book,
    make_category,
    make_publisher,
    make_user,
)


def _book_payload(author_id: int, publisher_id: int, **overrides) -> dict:
    base = {
        "title": "Test Book",
        "description": "A test book.",
        "author_id": author_id,
        "publisher_id": publisher_id,
        "format": "Paperback",
        "language": "English",
        "price": "199.99",
        "stock_quantity": 10,
        "category_ids": [],
    }
    base.update(overrides)
    return base


class TestCreateBook:
    def test_create_book_authenticated(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/books",
            json=_book_payload(author.id, publisher.id),
            headers=headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Test Book"
        assert body["author"]["id"] == author.id
        assert body["publisher"]["id"] == publisher.id
        assert body["stock_quantity"] == 10

    def test_create_book_unauthenticated(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        resp = client.post(
            "/books",
            json=_book_payload(author.id, publisher.id),
        )
        assert resp.status_code == 401

    def test_create_book_with_categories(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        cat = make_category(db, name="Fiction", slug="fiction")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/books",
            json=_book_payload(author.id, publisher.id, category_ids=[cat.id]),
            headers=headers,
        )
        assert resp.status_code == 201
        categories = resp.json()["categories"]
        assert any(c["id"] == cat.id for c in categories)

    def test_create_book_invalid_author(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        publisher = make_publisher(db)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/books",
            json=_book_payload(99999, publisher.id),
            headers=headers,
        )
        assert resp.status_code == 404

    def test_create_book_invalid_publisher(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/books",
            json=_book_payload(author.id, 99999),
            headers=headers,
        )
        assert resp.status_code == 404

    def test_create_book_invalid_category(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/books",
            json=_book_payload(author.id, publisher.id, category_ids=[99999]),
            headers=headers,
        )
        assert resp.status_code == 400


class TestGetBooks:
    def test_get_books_empty(self, client):
        resp = client.get("/books")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_books_returns_active_only(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        make_book(db, author=author, publisher=publisher, title="Active", is_active=True)
        make_book(db, author=author, publisher=publisher, title="Inactive", is_active=False)
        resp = client.get("/books")
        titles = [b["title"] for b in resp.json()]
        assert "Active" in titles
        assert "Inactive" not in titles

    def test_filter_by_author(self, client, db):
        author1 = make_author(db, name="Author One")
        author2 = make_author(db, name="Author Two")
        publisher = make_publisher(db)
        make_book(db, author=author1, publisher=publisher, title="Book by One")
        make_book(db, author=author2, publisher=publisher, title="Book by Two")
        resp = client.get(f"/books?author_id={author1.id}")
        titles = [b["title"] for b in resp.json()]
        assert "Book by One" in titles
        assert "Book by Two" not in titles

    def test_filter_by_publisher(self, client, db):
        author = make_author(db)
        pub1 = make_publisher(db, name="Publisher One")
        pub2 = make_publisher(db, name="Publisher Two")
        make_book(db, author=author, publisher=pub1, title="Book Pub1")
        make_book(db, author=author, publisher=pub2, title="Book Pub2")
        resp = client.get(f"/books?publisher_id={pub1.id}")
        titles = [b["title"] for b in resp.json()]
        assert "Book Pub1" in titles
        assert "Book Pub2" not in titles

    def test_filter_by_min_price(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        make_book(db, author=author, publisher=publisher, title="Cheap", price=Decimal("50.00"))
        make_book(db, author=author, publisher=publisher, title="Expensive", price=Decimal("500.00"))
        resp = client.get("/books?min_price=100")
        titles = [b["title"] for b in resp.json()]
        assert "Expensive" in titles
        assert "Cheap" not in titles

    def test_filter_by_max_price(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        make_book(db, author=author, publisher=publisher, title="Cheap", price=Decimal("50.00"))
        make_book(db, author=author, publisher=publisher, title="Expensive", price=Decimal("500.00"))
        resp = client.get("/books?max_price=100")
        titles = [b["title"] for b in resp.json()]
        assert "Cheap" in titles
        assert "Expensive" not in titles

    def test_search_by_title(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        make_book(db, author=author, publisher=publisher, title="Python Programming")
        make_book(db, author=author, publisher=publisher, title="Java Guide")
        resp = client.get("/books?search=python")
        titles = [b["title"] for b in resp.json()]
        assert "Python Programming" in titles
        assert "Java Guide" not in titles


class TestGetBook:
    def test_get_book_by_id(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, title="Some Book")
        resp = client.get(f"/books/{book.id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Some Book"

    def test_get_book_not_found(self, client):
        resp = client.get("/books/99999")
        assert resp.status_code == 404


class TestUpdateBook:
    def test_update_book_authenticated(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, title="Old Title")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.put(
            f"/books/{book.id}",
            json={"title": "New Title"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "New Title"

    def test_update_book_unauthenticated(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        resp = client.put(f"/books/{book.id}", json={"title": "Hacked"})
        assert resp.status_code == 401

    def test_update_book_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.put("/books/99999", json={"title": "X"}, headers=headers)
        assert resp.status_code == 404


class TestDeleteBook:
    def test_delete_book_soft_deletes(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete(f"/books/{book.id}", headers=headers)
        assert resp.status_code == 200
        # Book should no longer appear in the active listing
        listing = client.get("/books").json()
        ids = [b["id"] for b in listing]
        assert book.id not in ids

    def test_delete_book_unauthenticated(self, client, db):
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        resp = client.delete(f"/books/{book.id}")
        assert resp.status_code == 401
