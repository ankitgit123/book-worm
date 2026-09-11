"""
Shared pytest fixtures for the Book Worm backend test suite.

Uses an in-memory SQLite database so no external database is required.
"""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import (
    Address,
    Author,
    Base,
    Book,
    Category,
    BookCategory,
    Publisher,
    User,
)
from app.services import hash_password


# ============================================================
# IN-MEMORY DATABASE SETUP
# ============================================================

# StaticPool keeps a single connection open for the lifetime of the engine so
# that every session (including those opened by the FastAPI app inside the test
# client) sees the same in-memory database.
SQLITE_URL = "sqlite://"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(setup_db):
    """Yield a fresh database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    """Return a TestClient that uses the test database session."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ============================================================
# FACTORY HELPERS
# ============================================================

def make_user(
    db,
    *,
    name: str = "Test User",
    email: str = "test@example.com",
    password: str = "password123",
    gift_points_balance: int = 0,
) -> User:
    user = User(
        name=name,
        email=email.lower(),
        password_hash=hash_password(password),
        gift_points_balance=gift_points_balance,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_author(
    db,
    *,
    name: str = "Test Author",
) -> Author:
    author = Author(name=name)
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


def make_publisher(
    db,
    *,
    name: str = "Test Publisher",
) -> Publisher:
    publisher = Publisher(name=name)
    db.add(publisher)
    db.commit()
    db.refresh(publisher)
    return publisher


def make_category(
    db,
    *,
    name: str = "Fiction",
    slug: str = "fiction",
) -> Category:
    category = Category(name=name, slug=slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def make_book(
    db,
    *,
    author: Author,
    publisher: Publisher,
    title: str = "Test Book",
    price: Decimal = Decimal("199.99"),
    stock_quantity: int = 10,
    is_active: bool = True,
    categories: list[Category] | None = None,
) -> Book:
    book = Book(
        title=title,
        author_id=author.id,
        publisher_id=publisher.id,
        format="Paperback",
        language="English",
        price=price,
        stock_quantity=stock_quantity,
        sales_count=0,
        average_rating=Decimal("0.00"),
        is_active=is_active,
    )
    db.add(book)
    db.flush()

    for cat in (categories or []):
        db.add(BookCategory(book_id=book.id, category_id=cat.id))

    db.commit()
    db.refresh(book)
    return book


def auth_headers(client, *, email: str, password: str) -> dict:
    """Return Authorization headers for the given credentials."""
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
