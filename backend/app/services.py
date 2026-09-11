from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


# ============================================================
# JWT CREATE
# ============================================================

def create_access_token(data: dict) -> str:
    payload = data.copy()

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    payload.update(
        {
            "iat": now,
            "exp": expire,
        }
    )

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ============================================================
# JWT DECODE
# ============================================================

def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None

    except Exception:
        return None