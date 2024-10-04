from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.models.review import Review
from app.routers.services.permissions import only_admin_permission
from app.routers.services.utils import get_object_or_404
from app.models.services.products_utils import update_product_rating
from app.schemas.review import ReviewRetriveSchema, ReviewChangeStatusSchema
from app.schemas.user import (
    UserRetriveScehema,
    UserStatusUpdate,
)


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(only_admin_permission)],
)


@router.put(
    "/user_status/{user_id}",
    response_model=UserRetriveScehema,
    status_code=status.HTTP_200_OK,
)
async def change_user_status_by_admin(
    user_id: int,
    user_data: UserStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Роут чисто для админа (`is_admin == True`), редактирование статусов пользователей."""
    target_user = await get_object_or_404(db, User, User.id == user_id)
    target_user.is_admin = user_data.is_admin
    target_user.is_supplier = user_data.is_supplier
    target_user.is_customer = user_data.is_customer
    await db.commit()
    await db.refresh(target_user)
    return target_user


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Роут чисто для админа (`is_admin == True`), удаление пользовтелей."""
    target_user = get_object_or_404(db, User, User.id == user_id)
    await db.delete(target_user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/change_review_status/{review_id}",
    response_model=ReviewRetriveSchema,
    status_code=status.HTTP_200_OK,
)
async def change_review_status(
    review_id: int,
    review_status: ReviewChangeStatusSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_admin_permission)],
):
    """Роут чисто для админа (`is_admin == True`), скрыть отзыв."""
    review = await get_object_or_404(db, Review, Review.id == review_id)
    review.is_active = review_status.is_active
    await db.commit()
    await db.refresh(review)
    await update_product_rating(db, review.product_id)
    return review
