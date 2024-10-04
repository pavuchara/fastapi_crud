from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from slugify import slugify

from app.models.category import Category
from app.models.user import User
from app.models.products import Product
from app.models.review import Review
from app.schemas.product import ProductCreateSchema
from app.routers.services.utils import get_object_or_404


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


async def create_product_helper(db: AsyncSession, user: User, product_data: ProductCreateSchema):
    """Вспомогательная функция для создания продукта в бд."""
    category = await get_object_or_404(db, Category, Category.id == product_data.category_id)
    product = Product(
        name=product_data.name,
        slug=slugify(product_data.name),
        description=product_data.description,
        price=product_data.price,
        image_url=product_data.image_url,
        stock=product_data.stock,
        category_id=category.id,
        author_id=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    new_product = await db.scalar(
        select(Product)
        .where(Product.id == product.id)
        .options(
            selectinload(Product.author),
            selectinload(Product.category),
        )
    )
    return new_product


async def update_product_helper(
    db: AsyncSession,
    user: User,
    product: Product,
    product_data: ProductCreateSchema,
):
    """Вспомогательная функция для обновления продукта в бд."""
    category = await get_object_or_404(
        db, Category, Category.id == product_data.category_id
    )
    product.name = product_data.name
    product.slug = slugify(product_data.name)
    product.description = product_data.description
    product.price = product_data.price
    product.image_url = product_data.name
    product.category_id = category.id
    await db.commit()
    await db.refresh(product)

    product_with_related_fields = await db.scalar(
        select(Product)
        .where(Product.id == product.id)
        .options(
            selectinload(Product.author),
            selectinload(Product.category),
        )
    )
    return product_with_related_fields
