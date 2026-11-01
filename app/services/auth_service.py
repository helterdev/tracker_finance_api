from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    """Busca un usuario por email usando sintaxis SQLAlchemy 2.0."""
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)  # Retorna la entidad User o None


def register_user(db: Session, user_in: UserCreate) -> User:
    """Registra un nuevo usuario validando que el email no esté en uso."""
    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )

    # Nunca guardamos user_in.password; guardamos su hash Argon2
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verifica credenciales y estado activo del usuario para el login."""
    user = get_user_by_email(db, email)

    # Mismo mensaje de error si falla email o password para evitar enumeración de usuarios
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    return user
