from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Boolean,
    TIMESTAMP,
    Integer,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates

from app.backend.db import Base
from app.models.services.exceptions import ReviewValidationException


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("author_id", "product_id", name="unique_review_user"),)

    # Table fields:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        index=True,
        nullable=False,
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    datetime_created: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(ZoneInfo("Europe/Moscow")),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Relationships:
    product = relationship("app.models.products.Product", back_populates="reviews")
    author = relationship("app.models.user.User", back_populates="reviews")

    @validates("grade")
    def validete_grade(self, key, value):
        if not 0 <= value <= 10:
            raise ReviewValidationException("Rating value must be between 0 and 10")
        return value
