from pydantic import BaseModel

from app.schemas.user import UserRetriveScehema


class ProductCreateSchema(BaseModel):
    name: str
    description: str
    price: int
    image_url: str | None
    stock: int
    category_id: int


class ProductRetriveSchema(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: int
    image_url: str | None
    stock: int
    rating: int
    category_id: int
    author: UserRetriveScehema | None
