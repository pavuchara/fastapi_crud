from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import ACCESS_TOKEN_LIFETIME
from app.backend.db_depends import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreateSchema,
    UserRetriveScehema,
)
from app.routers.services.auth import (
    authenticate_user,
    create_access_token,
    bcrypt_context,
)


router = APIRouter(prefix="/auth", tags=["auth"])


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
