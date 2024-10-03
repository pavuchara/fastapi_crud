from pydantic import BaseModel

from app.schemas.user import UserRetriveScehema
from app.schemas.category import CategoryRetriveSchema


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
    category: CategoryRetriveSchema
    author: UserRetriveScehema | None
