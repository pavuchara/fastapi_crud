from sqlalchemy import (
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from email_validator import validate_email, EmailNotValidError

from app.backend.db import Base
from app.models.services.exceptions import UserValidationException


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
    products = relationship(
        "app.models.products.Product",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    reviews = relationship(
        "app.models.review.Review",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    @validates("email")
    def validate_email(self, key, value):
        try:
            emailinfo = validate_email(value, check_deliverability=False)
            return emailinfo.normalized
        except EmailNotValidError as e:
            raise UserValidationException(str(e))
