from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates

from app.backend.db import Base
from app.models.services.exceptions import ProductValidationException


class Product(Base):
    """Модель продуктов."""
    __tablename__ = "products"
    # Table fields:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    slug: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(5000))
    price: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(256), nullable=True)
    stock: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), index=True)
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=True
    )
    # Relationships:
    category = relationship("app.models.category.Category", back_populates="products")
    author = relationship("app.models.user.User", back_populates="products")
    reviews = relationship(
        "app.models.review.Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    @validates("price")
    def validate_price(self, key, value):
        if value <= 0:
            raise ProductValidationException("Price cannot be <= 0!")
        return value

    @validates("stock")
    def validate_stock(self, key, value):
        if value < 0:
            raise ProductValidationException("Stock cannot be < 0!")
        return value
