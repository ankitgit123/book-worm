"""Tests for /orders endpoints (create, list, get, cancel, buy-again)."""

from decimal import Decimal

from tests.conftest import (
    auth_headers,
    make_author,
    make_book,
    make_publisher,
    make_user,
)


def _address_payload(**overrides) -> dict:
    base = {
        "full_name": "John Doe",
        "address_line1": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "postal_code": "62701",
        "country": "US",
        "is_default": False,
    }
    base.update(overrides)
    return base


def _create_address(client, headers):
    return client.post("/addresses", json=_address_payload(), headers=headers).json()


def _add_to_cart(client, headers, book_id, quantity=1):
    client.post(
        "/cart/items",
        json={"book_id": book_id, "quantity": quantity},
        headers=headers,
    )


def _place_order(client, headers, address_id, gift_points_used=0):
    return client.post(
        "/orders",
        json={"address_id": address_id, "gift_points_used": gift_points_used},
        headers=headers,
    )


class TestCreateOrder:
    def test_create_order_success(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(
            db, author=author, publisher=publisher,
            price=Decimal("200.00"), stock_quantity=5,
        )
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id, quantity=2)
        resp = _place_order(client, headers, addr_id)
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "CONFIRMED"
        assert len(body["items"]) == 1
        assert body["items"][0]["quantity"] == 2
        assert body["payment"] is not None
        assert body["payment"]["status"] == "COMPLETED"

    def test_create_order_calculates_totals(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(
            db, author=author, publisher=publisher,
            price=Decimal("100.00"), stock_quantity=5,
        )
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id, quantity=1)
        resp = _place_order(client, headers, addr_id)
        body = resp.json()
        # subtotal=100, tax=18, delivery=40 (under 500), total=158
        assert float(body["subtotal"]) == 100.00
        assert float(body["tax"]) == 18.00
        assert float(body["delivery_charge"]) == 40.00
        assert float(body["total_amount"]) == 158.00

    def test_create_order_free_delivery_above_500(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(
            db, author=author, publisher=publisher,
            price=Decimal("600.00"), stock_quantity=5,
        )
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id)
        resp = _place_order(client, headers, addr_id)
        assert float(resp.json()["delivery_charge"]) == 0.00

    def test_create_order_empty_cart_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        resp = _place_order(client, headers, addr_id)
        assert resp.status_code == 400

    def test_create_order_invalid_address_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        _add_to_cart(client, headers, book.id)
        resp = _place_order(client, headers, 99999)
        assert resp.status_code == 404

    def test_create_order_insufficient_gift_points_rejected(self, client, db):
        make_user(db, email="user@example.com", password="pass1234", gift_points_balance=10)
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id)
        resp = _place_order(client, headers, addr_id, gift_points_used=100)
        assert resp.status_code == 400

    def test_create_order_clears_cart(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id)
        _place_order(client, headers, addr_id)
        cart = client.get("/cart", headers=headers).json()
        assert cart["items"] == []

    def test_create_order_decrements_stock(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(
            db, author=author, publisher=publisher, stock_quantity=10
        )
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id, quantity=3)
        _place_order(client, headers, addr_id)
        updated_book = client.get(f"/books/{book.id}").json()
        assert updated_book["stock_quantity"] == 7

    def test_create_order_unauthenticated(self, client):
        resp = client.post("/orders", json={"address_id": 1})
        assert resp.status_code == 401


class TestGetOrders:
    def test_get_orders_empty(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.get("/orders", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_orders_returns_own_only(self, client, db):
        make_user(db, email="user1@example.com", password="pass1234")
        make_user(db, email="user2@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        h1 = auth_headers(client, email="user1@example.com", password="pass1234")
        h2 = auth_headers(client, email="user2@example.com", password="pass1234")
        addr_id = _create_address(client, h1)["id"]
        _add_to_cart(client, h1, book.id)
        _place_order(client, h1, addr_id)
        resp = client.get("/orders", headers=h2)
        assert resp.json() == []


class TestGetOrder:
    def test_get_order_by_id(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id)
        order_id = _place_order(client, headers, addr_id).json()["id"]
        resp = client.get(f"/orders/{order_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id

    def test_get_order_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.get("/orders/99999", headers=headers)
        assert resp.status_code == 404

    def test_cannot_get_another_users_order(self, client, db):
        make_user(db, email="user1@example.com", password="pass1234")
        make_user(db, email="user2@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        h1 = auth_headers(client, email="user1@example.com", password="pass1234")
        h2 = auth_headers(client, email="user2@example.com", password="pass1234")
        addr_id = _create_address(client, h1)["id"]
        _add_to_cart(client, h1, book.id)
        order_id = _place_order(client, h1, addr_id).json()["id"]
        resp = client.get(f"/orders/{order_id}", headers=h2)
        assert resp.status_code == 404


class TestCancelOrder:
    def test_cancel_confirmed_order(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id)
        order_id = _place_order(client, headers, addr_id).json()["id"]
        resp = client.post(f"/orders/{order_id}/cancel", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "CANCELLED"

    def test_cancel_order_restores_stock(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=10)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id, quantity=3)
        order_id = _place_order(client, headers, addr_id).json()["id"]
        client.post(f"/orders/{order_id}/cancel", headers=headers)
        updated_book = client.get(f"/books/{book.id}").json()
        assert updated_book["stock_quantity"] == 10

    def test_cancel_already_cancelled_order(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=5)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id)
        order_id = _place_order(client, headers, addr_id).json()["id"]
        client.post(f"/orders/{order_id}/cancel", headers=headers)
        resp = client.post(f"/orders/{order_id}/cancel", headers=headers)
        assert resp.status_code == 400

    def test_cancel_order_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post("/orders/99999/cancel", headers=headers)
        assert resp.status_code == 404


class TestBuyAgain:
    def test_buy_again_adds_items_to_cart(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        author = make_author(db)
        publisher = make_publisher(db)
        book = make_book(db, author=author, publisher=publisher, stock_quantity=20)
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        addr_id = _create_address(client, headers)["id"]
        _add_to_cart(client, headers, book.id, quantity=2)
        order_id = _place_order(client, headers, addr_id).json()["id"]
        resp = client.post(f"/orders/{order_id}/buy-again", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        assert any(i["book"]["id"] == book.id for i in items)

    def test_buy_again_order_not_found(self, client, db):
        make_user(db, email="user@example.com", password="pass1234")
        headers = auth_headers(client, email="user@example.com", password="pass1234")
        resp = client.post("/orders/99999/buy-again", headers=headers)
        assert resp.status_code == 404
