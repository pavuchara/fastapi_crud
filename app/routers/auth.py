from typing import Annotated

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

from passlib.context import CryptContext

from app.backend.db_depends import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreateSchema,
    UserRetriveScehema,
)


router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post(
    "/registeration",
    response_model=UserRetriveScehema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: UserCreateSchema,
):
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


async def authenticate_user(
    email: str,
    password: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.scalar(select(User).where(User.email == email))
    if not user or not bcrypt_context.verify(password, user.password):
        raise HTTPException(
            detail="Invalid auth creds",
            headers={"WWW-Authenticate": "Bearer"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return user


@router.post("/token", status_code=status.HTTP_200_OK)
async def get_token(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    return {
        "access_token": user.email,
        "token_type": "bearer"
    }
