from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_LIFETIME
from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.services import get_object_or_404
from app.schemas.user import (
    UserCreateSchema,
    UserRetriveScehema,
)


router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


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


@router.post("/token", status_code=status.HTTP_200_OK)
async def get_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """Получение токена для аутентифицированного пользователя."""
    user = await authenticate_user(form_data.username, form_data.password, db)
    acess_token = await create_access_token(
        user_id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        is_supplier=user.is_supplier,
        is_customer=user.is_customer,
        expires_delta=ACCESS_TOKEN_LIFETIME,
    )
    return {
        "access_token": acess_token,
        "token_type": "bearer"
    }


@router.post(
    "/registeration",
    response_model=UserRetriveScehema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: UserCreateSchema,
):
    """Регистрация пользователя."""
    try:
        user = User(
            email=user_data.email,
            password=bcrypt_context.hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as e:
        await db.rollback()
        if "unique" in str(e.orig):
            raise HTTPException(
                detail="Email already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        raise HTTPException(
            detail="An error occurred while creating the user",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
