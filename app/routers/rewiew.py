from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.models.products import Product
from app.models.review import Review
from app.routers.services.utils import get_object_or_404
from app.routers.services.permissions import only_auth_user_permission
from app.models.services.exceptions import ReviewValidationException
from app.models.services.utils import update_product_rating
from app.schemas.review import (
    ReviewCreateSchema,
    ReviewRetriveSchema,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_self_review(
    review_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(only_auth_user_permission)],
):
    """Удалить собственный отзыв (только для автора)."""
    review = await get_object_or_404(db, Review, Review.id == review_id)
    if review.author_id == user.id:
        product_id: int = review.product_id
        await db.delete(review)
        await db.commit()
        await update_product_rating(db, product_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        detail="Not author",
        status_code=status.HTTP_403_FORBIDDEN,
    )


@router.get(
    "/{product_id}/reviews",
    response_model=list[ReviewRetriveSchema],
    status_code=status.HTTP_200_OK,
)
async def get_product_rewiews(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
):
    """Получить все отзывы товара."""
    product = await get_object_or_404(db, Product, Product.id == product_id)
    rewiews = await db.scalars(
        select(Review)
        .where(Review.product_id == product.id)
        .where(Review.is_active == True)
        .options(
            selectinload(Review.author),
        )
    )
    return rewiews.all()


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewRetriveSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review_data: ReviewCreateSchema,
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(only_auth_user_permission)],
):
    """Написать отзыв на товар."""
    try:
        product = await get_object_or_404(db, Product, Product.id == product_id)
        review = Review(
            author_id=user.id,
            product_id=product.id,
            grade=review_data.grade,
            comment=review_data.comment,
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        await update_product_rating(db, product_id)
        new_review = await db.scalar(
            select(Review)
            .where(Review.id == review.id)
            .options(
                selectinload(Review.author),
            )
        )
        return new_review
    except ReviewValidationException as e:
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except IntegrityError:
        # TODO по хорошему вычилять именно ошибку дубля, а не все.
        raise HTTPException(
            detail="User already rewiew this product",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
