from sqlalchemy import (
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.db import Base


class User(Base):
    __tablename__ = "users"
    # Table fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String(256))
    first_name: Mapped[str] = mapped_column(String(256), nullable=True)
    last_name: Mapped[str] = mapped_column(String(256), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_supplier: Mapped[bool] = mapped_column(Boolean, default=False)
    is_customer: Mapped[bool] = mapped_column(Boolean, default=True)
    # Relationships:
    products = relationship("app.models.products.Product", back_populates="author", cascade="all, delete-orphan")
