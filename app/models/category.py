import uuid
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import UUIDTimestampMixin


class CategoryType(StrEnum):
    """Tipos válidos de categoría financiera."""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Category(UUIDTimestampMixin, Base):
    """Categoría para clasificar ingresos o gastos de un usuario."""

    __tablename__ = "categories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, name="category_type_enum"),
        nullable=False,
    )
