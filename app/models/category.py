from sqlalchemy import (
    Boolean,
    Integer,
    String,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.backend.db import Base


class Category(Base):
    __tablename__ = "categories"
    # Table fields:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Relationships:
    products = relationship("app.models.products.Product", back_populates="category")
