from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.products import Product
from app.models.review import Review
from app.routers.services.utils import get_object_or_404
from app.models.services.products_utils import update_product_rating
from app.schemas.review import ReviewCreateSchema


async def create_review_helper(
    db: AsyncSession,
    product_id: int,
    user: User,
    review_data: ReviewCreateSchema,
):
    """Вспомогательная функция для создания отзыва в бд."""
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
