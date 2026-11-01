import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Atributos comunes compartidos entre creación y lectura de usuario."""

    email: EmailStr

    full_name: str | None = Field(default=None, max_length=150)


class UserCreate(UserBase):
    """Esquema para el registro de un nuevo usuario (POST /auth/register)."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Esquema para actualizar datos parciales del perfil (PATCH)."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=150)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserResponse(UserBase):
    """Esquema seguro de salida HTTP (lo que la API devuelve al cliente)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
