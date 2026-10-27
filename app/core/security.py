
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


# ============================================================
# ACCESS TOKEN
# ============================================================

def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "access":
            logger.warning(
                "JWT rejected: expected access token"
            )
            return None

        if not payload.get("sub"):
            logger.warning(
                "JWT rejected: missing subject"
            )
            return None

        return payload

    except JWTError as exc:
        # Never log the token or SECRET_KEY.
        logger.warning(
            "Access-token validation failed: %s",
            type(exc).__name__,
        )
        return None


# ============================================================
# REFRESH TOKEN
# ============================================================

def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": subject,
        "iat": now,
        "exp": expires_at,
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_refresh_token(
    token: str,
) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            logger.warning(
                "JWT rejected: expected refresh token"
            )
            return None

        if not payload.get("sub"):
            logger.warning(
                "JWT rejected: refresh token missing subject"
            )
            return None

        return payload

    except JWTError as exc:
        # Never log the token or SECRET_KEY.
        logger.warning(
            "Refresh-token validation failed: %s",
            type(exc).__name__,
        )
        return None
