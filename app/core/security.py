import uuid
from datetime import timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.models.base import utc_now

ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """Genera un hash seguro (Argon2) a partir de una contraseña en texto plano."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash almacenado."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | uuid.UUID, expires_delta: timedelta | None = None
) -> str:
    now = utc_now()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    """Decodifica y valida la firma y expiración de un token JWT."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
