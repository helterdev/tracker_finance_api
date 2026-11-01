from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import authenticate_user, register_user

# Agrupa todas las rutas bajo el prefijo /auth y la etiqueta "Auth" en Swagger
router = APIRouter(prefix="/auth", tags=["Auth"])

# Alias de tipos reutilizables para inyección de dependencias
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserCreate, db: DbSession) -> User:
    """Registra un usuario nuevo y devuelve sus datos públicos (sin contraseña)."""
    return register_user(db, user_in)


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """Valida credenciales (form-data) y retorna un JWT Bearer."""
    # OAuth2 llama 'username' al campo identificador; aquí enviamos el email
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> User:
    """Retorna el perfil del usuario autenticado mediante su token JWT."""
    return current_user
