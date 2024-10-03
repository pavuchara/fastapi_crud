from pydantic import BaseModel


class UserRetriveScehema(BaseModel):
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_admin: bool
    is_supplier: bool
    is_customer: bool


class UserCreateSchema(BaseModel):
    email: str
    password: str
    first_name: str | None
    last_name: str | None


class UserUpdateSchema(BaseModel):
    first_name: str | None
    last_name: str | None


class UserStatusUpdate(BaseModel):
    is_admin: bool
    is_supplier: bool
    is_customer: bool
