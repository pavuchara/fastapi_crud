from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from app.models.user import User
from app.routers.services.auth import decode_token_get_user


async def only_admin_permission(
    user: Annotated[User, Depends(decode_token_get_user)],
) -> User:
    if not user.is_admin:
        raise HTTPException(
            detail="Only for admin",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return user


async def only_auth_user_permission(
    user: Annotated[User, Depends(decode_token_get_user)],
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return user
