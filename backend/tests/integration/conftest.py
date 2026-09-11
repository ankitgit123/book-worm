from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import Base


TEST_DATABASE_NAME = "book_worm_test"


def build_test_database_url() -> URL:
    """
    Build the integration-test database URL from the application's
    normal DATABASE_URL.

    Development:
        book_worm

    Integration tests:
        book_worm_test
    """

    base_url = make_url(settings.DATABASE_URL)

    return base_url.set(
        database=TEST_DATABASE_NAME
    )


@pytest.fixture(scope="session")
def test_engine():
    """
    Create a SQLAlchemy engine connected to the isolated
    book_worm_test database.

    The database itself is created manually in MySQL.
    Pytest manages only the tables.
    """

    test_database_url = build_test_database_url()

    engine = create_engine(
        test_database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # Fail early with a clear message if the test database
    # cannot be reached.
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Give every integration test a clean database schema.

    Before:
        DROP all application tables
        CREATE all application tables

    After:
        DROP all application tables
    """

    Base.metadata.drop_all(bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.close()

        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    FastAPI TestClient that uses the integration-test
    database session instead of the development database.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()