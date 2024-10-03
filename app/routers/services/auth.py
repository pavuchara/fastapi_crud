from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import (
    Depends,
    status,
    HTTPException,
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.settings import SECRET_KEY, ALGORITHM
from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.services.utils import get_object_or_404


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def authenticate_user(
    email: str,
    password: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Получение `email` и `password` для аутентификации пользоваля."""
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not bcrypt_context.verify(password, user.password):
        raise HTTPException(
            detail="Invalid auth creds",
            headers={"WWW-Authenticate": "Bearer"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return user


async def create_access_token(
    user_id: int,
    email: str,
    is_admin: bool,
    is_supplier: bool,
    is_customer: bool,
    expires_delta: timedelta,
) -> str:
    """Создание access токена, время жизни зависит от `ACCESS_TOKEN_LIFETIME`."""
    encode = {
        "id": user_id,
        "sub": email,
        "is_admin": is_admin,
        "is_supplier": is_supplier,
        "is_customer": is_customer,
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def decode_token_get_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Декодирование токена, получение дынных из payload -> `User`."""
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user = await get_object_or_404(db, User, User.id == payload.get("id"))
        return user
    except JWTError:
        raise HTTPException(
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
