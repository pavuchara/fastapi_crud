from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.services.utils import get_object_or_404
from app.schemas.user import (
    UserRetriveScehema,
    UserUpdateSchema,
)
from app.routers.services.permissions import (
    only_auth_user_permission,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRetriveScehema], status_code=status.HTTP_200_OK)
async def get_list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
):
    users = await db.scalars(select(User))
    return users.all()


@router.get("/current", response_model=UserRetriveScehema, status_code=status.HTTP_200_OK)
async def get_current_user(
    request_user: Annotated[User, Depends(only_auth_user_permission)],
):
    return request_user


@router.get("/{user_id}", response_model=UserRetriveScehema, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
):
    user = await get_object_or_404(db, User, User.id == user_id)
    return user


@router.put("/{user_id}", response_model=UserRetriveScehema, status_code=status.HTTP_200_OK)
async def change_profile(
    user_id: int,
    user_data: UserUpdateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    request_user: Annotated[User, Depends(only_auth_user_permission)],
):
    if request_user.id == user_id:
        user = await get_object_or_404(db, User, User.id == user_id)
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
        await db.commit()
        await db.refresh(user)
        return user
    raise HTTPException(
        detail="Not profile owner",
        status_code=status.HTTP_403_FORBIDDEN,
    )
