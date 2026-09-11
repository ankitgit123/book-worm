from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import settings


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)


# ============================================================
# SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# FASTAPI DATABASE DEPENDENCY
# ============================================================

def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()