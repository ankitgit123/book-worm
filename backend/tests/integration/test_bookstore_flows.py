from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Author,
    Book,
    BookCategory,
    Category,
    Order,
    OrderItem,
    Payment,
    Publisher,
    User,
)


TEST_PASSWORD = "TestPassword123!"

ADDRESS_DATA = {
    "full_name": "Book Worm Test User",
    "phone": "9876543210",
    "address_line1": "100 Test Street",
    "address_line2": "Test Apartment",
    "city": "Gurugram",
    "state": "Haryana",
    "postal_code": "122001",
    "country": "India",
    "is_default": True,
}


def register_and_login(client, email: str) -> dict:
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Book Worm Integration User",
            "email": email,
            "password": TEST_PASSWORD,
        },
    )

    assert register_response.status_code in (200, 201), (
        f"Registration failed: "
        f"{register_response.status_code} "
        f"{register_response.text}"
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
        },
    )

    assert login_response.status_code == 200, (
        f"Login failed: "
        f"{login_response.status_code} "
        f"{login_response.text}"
    )

    login_data = login_response.json()

    assert "access_token" in login_data, (
        f"Login response does not contain access_token: {login_data}"
    )

    return {
        "Authorization": f"Bearer {login_data['access_token']}"
    }


def create_catalogue_data(db_session: Session) -> Book:
    author = Author(
        name="Integration Test Author",
        bio="Author used only for automated integration tests.",
        photo_url=None,
    )

    publisher = Publisher(
        name="Integration Test Publisher",
    )

    category = Category(
        name="Integration Testing",
        slug="integration-testing",
    )

    db_session.add_all(
        [
            author,
            publisher,
            category,
        ]
    )

    db_session.flush()

    book = Book(
        title="Integration Testing Book",
        description="Book used for Book Worm integration testing.",
        author_id=author.id,
        publisher_id=publisher.id,
        format="Paperback",
        language="English",
        price=Decimal("500.00"),
        cover_image_url=None,
        delivery_date=date.today() + timedelta(days=3),
        stock_quantity=10,
        sales_count=0,
        average_rating=Decimal("0.00"),
        is_active=True,
    )

    db_session.add(book)
    db_session.flush()

    book_category = BookCategory(
        book_id=book.id,
        category_id=category.id,
    )

    db_session.add(book_category)
    db_session.commit()

    db_session.refresh(book)

    return book


def create_address(client, headers: dict) -> int:
    response = client.post(
        "/addresses",
        json=ADDRESS_DATA,
        headers=headers,
    )

    assert response.status_code in (200, 201), (
        f"Address creation failed: "
        f"{response.status_code} "
        f"{response.text}"
    )

    data = response.json()

    address_id = data.get("id")

    assert address_id is not None, (
        f"Address response does not contain id: {data}"
    )

    return address_id


def add_to_cart(
    client,
    headers: dict,
    book_id: int,
    quantity: int,
):
    response = client.post(
        "/cart/items",
        json={
            "book_id": book_id,
            "quantity": quantity,
        },
        headers=headers,
    )

    assert response.status_code in (200, 201), (
        f"Add to cart failed: "
        f"{response.status_code} "
        f"{response.text}"
    )

    return response


def create_order(
    client,
    headers: dict,
    address_id: int,
    gift_points_used: int = 0,
):
    response = client.post(
        "/orders",
        json={
            "address_id": address_id,
            "gift_points_used": gift_points_used,
        },
        headers=headers,
    )

    assert response.status_code in (200, 201), (
        f"Order creation failed: "
        f"{response.status_code} "
        f"{response.text}"
    )

    data = response.json()

    order_id = (
        data.get("id")
        or data.get("order_id")
        or data.get("order", {}).get("id")
    )

    assert order_id is not None, (
        f"Order response does not contain an order ID: {data}"
    )

    return order_id, data


def get_cart(client, headers: dict):
    response = client.get(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 200, (
        f"Get cart failed: "
        f"{response.status_code} "
        f"{response.text}"
    )

    return response.json()


def get_order(client, headers: dict, order_id: int):
    response = client.get(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert response.status_code == 200, (
        f"Get order failed: "
        f"{response.status_code} "
        f"{response.text}"
    )

    return response.json()


def get_cart_item_book_id(cart_item: dict) -> int:
    """
    Extract the book ID from the actual cart-item response.

    The application may represent the relationship as:
        book_id
        bookId
        book.id
    """

    if cart_item.get("book_id") is not None:
        return cart_item["book_id"]

    if cart_item.get("bookId") is not None:
        return cart_item["bookId"]

    book = cart_item.get("book")

    if isinstance(book, dict) and book.get("id") is not None:
        return book["id"]

    raise AssertionError(
        "Cart item does not expose a book ID in a supported format. "
        f"Actual cart item response: {cart_item}"
    )


def get_cart_item_quantity(cart_item: dict) -> int:
    """
    Extract quantity from the cart-item response.
    """

    quantity = cart_item.get("quantity")

    assert quantity is not None, (
        f"Cart item does not contain quantity: {cart_item}"
    )

    return quantity


def test_complete_purchase_flow(
    client,
    db_session: Session,
):
    """
    Complete customer purchase flow:

    Register
      ↓
    Login
      ↓
    Create address
      ↓
    Add book to cart
      ↓
    Verify cart
      ↓
    Create order
      ↓
    Verify payment
      ↓
    Verify stock
      ↓
    Verify sales count
      ↓
    Verify cart is empty
    """

    book = create_catalogue_data(db_session)

    headers = register_and_login(
        client,
        "integration.purchase@example.com",
    )

    address_id = create_address(
        client,
        headers,
    )

    add_to_cart(
        client,
        headers,
        book.id,
        quantity=2,
    )

    cart_before_purchase = get_cart(
        client,
        headers,
    )

    assert "items" in cart_before_purchase, (
        f"Cart response does not contain items: {cart_before_purchase}"
    )

    assert len(cart_before_purchase["items"]) == 1

    cart_item = cart_before_purchase["items"][0]

    assert get_cart_item_book_id(cart_item) == book.id
    assert get_cart_item_quantity(cart_item) == 2

    order_id, _ = create_order(
        client,
        headers,
        address_id,
        gift_points_used=0,
    )

    assert order_id > 0

    order = get_order(
        client,
        headers,
        order_id,
    )

    assert order["id"] == order_id
    assert order["status"] == "CONFIRMED"

    assert Decimal(str(order["subtotal"])) == Decimal("1000.00")
    assert Decimal(str(order["tax"])) == Decimal("180.00")
    assert Decimal(str(order["delivery_charge"])) == Decimal("0.00")
    assert Decimal(str(order["discount"])) == Decimal("0.00")
    assert Decimal(str(order["total_amount"])) == Decimal("1180.00")

    db_session.expire_all()

    database_book = db_session.execute(
        select(Book).where(Book.id == book.id)
    ).scalar_one()

    assert database_book.stock_quantity == 8
    assert database_book.sales_count == 2

    database_order = db_session.execute(
        select(Order).where(Order.id == order_id)
    ).scalar_one()

    assert database_order.status == "CONFIRMED"

    order_items = db_session.execute(
        select(OrderItem).where(
            OrderItem.order_id == order_id
        )
    ).scalars().all()

    assert len(order_items) == 1

    assert order_items[0].book_id == book.id
    assert order_items[0].quantity == 2
    assert order_items[0].unit_price == Decimal("500.00")
    assert order_items[0].total_price == Decimal("1000.00")

    payment = db_session.execute(
        select(Payment).where(
            Payment.order_id == order_id
        )
    ).scalar_one()

    assert payment.method == "MOCK"
    assert payment.status == "COMPLETED"
    assert payment.amount == Decimal("1180.00")
    assert payment.transaction_reference == f"MOCK-TXN-{order_id}"
    assert payment.paid_at is not None

    cart_after_purchase = get_cart(
        client,
        headers,
    )

    assert cart_after_purchase["items"] == []


def test_buy_again_flow(
    client,
    db_session: Session,
):
    """
    Purchase a book, then use Buy Again.
    """

    book = create_catalogue_data(db_session)

    headers = register_and_login(
        client,
        "integration.buyagain@example.com",
    )

    address_id = create_address(
        client,
        headers,
    )

    add_to_cart(
        client,
        headers,
        book.id,
        quantity=1,
    )

    order_id, _ = create_order(
        client,
        headers,
        address_id,
        gift_points_used=0,
    )

    buy_again_response = client.post(
        f"/orders/{order_id}/buy-again",
        headers=headers,
    )

    assert buy_again_response.status_code in (200, 201), (
        f"Buy Again failed: "
        f"{buy_again_response.status_code} "
        f"{buy_again_response.text}"
    )

    cart = get_cart(
        client,
        headers,
    )

    assert len(cart["items"]) == 1

    cart_item = cart["items"][0]

    assert get_cart_item_book_id(cart_item) == book.id
    assert get_cart_item_quantity(cart_item) == 1


def test_cancel_order_restores_stock_and_gift_points(
    client,
    db_session: Session,
):
    """
    Purchase with gift points and then cancel.

    Verify:

    - order becomes CANCELLED
    - stock is restored
    - gift points are restored
    - payment becomes REFUND_PENDING
    """

    book = create_catalogue_data(db_session)

    headers = register_and_login(
        client,
        "integration.cancel@example.com",
    )

    current_user_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert current_user_response.status_code == 200

    current_user = current_user_response.json()

    user_id = current_user["id"]

    user = db_session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one()

    user.gift_points_balance = 100

    db_session.commit()

    address_id = create_address(
        client,
        headers,
    )

    add_to_cart(
        client,
        headers,
        book.id,
        quantity=1,
    )

    order_id, _ = create_order(
        client,
        headers,
        address_id,
        gift_points_used=100,
    )

    db_session.expire_all()

    database_book_after_purchase = db_session.execute(
        select(Book).where(Book.id == book.id)
    ).scalar_one()

    assert database_book_after_purchase.stock_quantity == 9

    database_user_after_purchase = db_session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one()

    assert database_user_after_purchase.gift_points_balance == 0

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers,
    )

    assert cancel_response.status_code in (200, 201), (
        f"Order cancellation failed: "
        f"{cancel_response.status_code} "
        f"{cancel_response.text}"
    )

    cancelled_order = get_order(
        client,
        headers,
        order_id,
    )

    assert cancelled_order["status"] == "CANCELLED"

    db_session.expire_all()

    database_book_after_cancel = db_session.execute(
        select(Book).where(Book.id == book.id)
    ).scalar_one()

    assert database_book_after_cancel.stock_quantity == 10

    database_user_after_cancel = db_session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one()

    assert database_user_after_cancel.gift_points_balance == 100

    payment = db_session.execute(
        select(Payment).where(
            Payment.order_id == order_id
        )
    ).scalar_one()

    assert payment.status == "REFUND_PENDING"


def test_review_after_purchase(
    client,
    db_session: Session,
):
    """
    Purchase a book and submit a review.
    """

    book = create_catalogue_data(db_session)

    headers = register_and_login(
        client,
        "integration.review@example.com",
    )

    address_id = create_address(
        client,
        headers,
    )

    add_to_cart(
        client,
        headers,
        book.id,
        quantity=1,
    )

    order_id, _ = create_order(
        client,
        headers,
        address_id,
        gift_points_used=0,
    )

    assert order_id > 0

    review_response = client.post(
        f"/books/{book.id}/reviews",
        json={
            "rating": 5,
            "comment": (
                "Excellent book. "
                "This review was created by an integration test."
            ),
        },
        headers=headers,
    )

    assert review_response.status_code in (200, 201), (
        f"Review creation failed: "
        f"{review_response.status_code} "
        f"{review_response.text}"
    )

    review = review_response.json()

    assert review["book_id"] == book.id
    assert review["rating"] == 5

    reviews_response = client.get(
        f"/books/{book.id}/reviews",
        headers=headers,
    )

    assert reviews_response.status_code == 200, (
        f"Get reviews failed: "
        f"{reviews_response.status_code} "
        f"{reviews_response.text}"
    )

    reviews = reviews_response.json()

    if isinstance(reviews, dict):
        review_items = reviews.get(
            "items",
            reviews.get("reviews", []),
        )
    else:
        review_items = reviews

    assert len(review_items) >= 1

    matching_review = next(
        (
            item
            for item in review_items
            if item.get("rating") == 5
        ),
        None,
    )

    assert matching_review is not None


def test_cart_to_order_to_order_history_flow(
    client,
    db_session: Session,
):
    """
    Cart → Order → Order History → Order Details.
    """

    book = create_catalogue_data(db_session)

    headers = register_and_login(
        client,
        "integration.history@example.com",
    )

    address_id = create_address(
        client,
        headers,
    )

    add_to_cart(
        client,
        headers,
        book.id,
        quantity=1,
    )

    order_id, _ = create_order(
        client,
        headers,
        address_id,
        gift_points_used=0,
    )

    orders_response = client.get(
        "/orders",
        headers=headers,
    )

    assert orders_response.status_code == 200, (
        f"Order history failed: "
        f"{orders_response.status_code} "
        f"{orders_response.text}"
    )

    orders = orders_response.json()

    if isinstance(orders, dict):
        order_items = orders.get(
            "items",
            orders.get("orders", []),
        )
    else:
        order_items = orders

    matching_order = next(
        (
            order
            for order in order_items
            if order.get("id") == order_id
        ),
        None,
    )

    assert matching_order is not None

    order_details = get_order(
        client,
        headers,
        order_id,
    )

    assert order_details["id"] == order_id
    assert order_details["status"] == "CONFIRMED"