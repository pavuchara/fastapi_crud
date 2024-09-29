from pydantic import BaseModel


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryRetriveSchema(BaseModel):
    id: int
    is_active: bool
    name: str
    slug: str
