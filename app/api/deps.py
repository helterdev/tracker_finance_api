import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Dependencias preinstanciadas a nivel de módulo
DB_DEPENDENCY = Depends(get_db)
TOKEN_DEPENDENCY = Depends(oauth2_scheme)


def get_current_user(
    db: Session = DB_DEPENDENCY,
    token: str = TOKEN_DEPENDENCY,
) -> User:
    """Valida el JWT Bearer y retorna el usuario autenticado."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        token_data = TokenPayload.model_validate(payload)
    except jwt.InvalidTokenError, ValidationError:
        raise credentials_exception

    user = db.get(User, token_data.sub)
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    return user
