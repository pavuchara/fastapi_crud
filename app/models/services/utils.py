from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product
from app.models.review import Review


async def update_product_rating(db: AsyncSession, product_id: int):
    avg_rating = await db.scalar(
        select(func.avg(Review.grade))
        .where(Review.product_id == product_id)
        .where(Review.is_active == True)
    )
    if avg_rating is not None:
        product = await db.get(Product, product_id)
        if product:
            product.rating = int(avg_rating)
            await db.commit()
