from pydantic import BaseModel


class UserRetriveScehema(BaseModel):
    id: int
    email: int
    first_name: str | None
    last_name: str | None
    is_admin: bool
    is_supplier: bool
    is_customer: bool


class UserCreateSchema(BaseModel):
    email: int
    password: int
    first_name: str | None
    last_name: str | None
