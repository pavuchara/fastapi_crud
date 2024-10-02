from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.auth import oauth2_scheme
from app.routers.services import get_object_or_404
from app.schemas.user import (
    UserRetriveScehema,
    UserUpdateSchema,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRetriveScehema], status_code=status.HTTP_200_OK)
async def get_list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    users = await db.scalars(select(User))
    return users.all()


@router.get("/current")
async def get_current_user(user: User = Depends(oauth2_scheme)):
    return user


@router.get("/{user_id}", response_model=UserRetriveScehema, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await get_object_or_404(db, User, User.id == user_id)
    return user


@router.put("/{user_id}", response_model=UserRetriveScehema, status_code=status.HTTP_200_OK)
async def change_profile(
    user_id: int,
    user_data: UserUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await get_object_or_404(db, User, User.id == user_id)
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    await db.commit()
    await db.refresh(user)
    return user
