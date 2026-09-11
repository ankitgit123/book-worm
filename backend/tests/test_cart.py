"""Tests for /cart endpoints."""

from tests.conftest import (
    auth_headers,
    make_author,
    make_book,
    make_publisher,
    make_user,
)


class TestGetCart:
    def test_get_cart_initially_empty(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.get("/cart", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert float(body["subtotal"]) == 0.0

    def test_get_cart_unauthenticated(self, client):
        resp = client.get("/cart")
        assert resp.status_code == 401


class TestAddToCart:
    def test_add_item_to_cart(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 2},
            headers=headers,
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["quantity"] == 2
        assert items[0]["book"]["id"] == book.id

    def test_add_same_book_accumulates_quantity(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=20)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        client.post("/cart/items", json={"book_id": book.id, "quantity": 2}, headers=headers)
        resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 3},
            headers=headers,
        )
        assert resp.json()["items"][0]["quantity"] == 5

    def test_add_item_exceeds_stock(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=3)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 10},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_add_inactive_book_to_cart(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, is_active=False)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 1},
            headers=headers,
        )
        assert resp.status_code == 404

    def test_add_nonexistent_book(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post(
            "/cart/items",
            json={"book_id": 99999, "quantity": 1},
            headers=headers,
        )
        assert resp.status_code == 404


class TestUpdateCartItem:
    def test_update_cart_item_quantity(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=10)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        add_resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 1},
            headers=headers,
        )
        item_id = add_resp.json()["items"][0]["id"]
        resp = client.put(
            f"/cart/items/{item_id}",
            json={"quantity": 5},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["items"][0]["quantity"] == 5

    def test_update_cart_item_exceeds_stock(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=3)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        add_resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 1},
            headers=headers,
        )
        item_id = add_resp.json()["items"][0]["id"]
        resp = client.put(
            f"/cart/items/{item_id}",
            json={"quantity": 100},
            headers=headers,
        )
        assert resp.status_code == 400

    def test_update_cart_item_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.put("/cart/items/99999", json={"quantity": 1}, headers=headers)
        assert resp.status_code == 404


class TestRemoveCartItem:
    def test_remove_cart_item(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        add_resp = client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 1},
            headers=headers,
        )
        item_id = add_resp.json()["items"][0]["id"]
        resp = client.delete(f"/cart/items/{item_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_remove_cart_item_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete("/cart/items/99999", headers=headers)
        assert resp.status_code == 404


class TestClearCart:
    def test_clear_cart(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        client.post(
            "/cart/items",
            json={"book_id": book.id, "quantity": 1},
            headers=headers,
        )
        resp = client.delete("/cart", headers=headers)
        assert resp.status_code == 200
        cart = client.get("/cart", headers=headers).json()
        assert cart["items"] == []

    def test_clear_cart_when_empty_is_safe(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.delete("/cart", headers=headers)
        assert resp.status_code == 200
