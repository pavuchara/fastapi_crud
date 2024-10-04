from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserRetriveScehema


class ReviewRetriveSchema(BaseModel):
    id: int
    author: UserRetriveScehema
    product_id: int
    grade: int
    comment: str | None
    datetime_created: datetime
    is_active: bool


class ReviewCreateSchema(BaseModel):
    grade: int
    comment: str | None


class ReviewChangeStatusSchema(BaseModel):
    is_active: bool
