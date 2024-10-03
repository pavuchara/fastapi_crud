from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
    Query,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from slugify import slugify

from app.backend.db_depends import get_db
from app.routers.services.utils import get_object_or_404
from app.models.user import User
from app.models.products import Product
from app.models.category import Category
from app.schemas.product import (
    ProductCreateSchema,
    ProductRetriveSchema,
)
from app.routers.services.permissions import (
    only_auth_user_permission,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRetriveSchema], status_code=status.HTTP_200_OK)
async def get_list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
    by_category_id: Annotated[int | None, Query()] = None,
):
    if by_category_id is not None:
        category = await get_object_or_404(db, Category, Category.id == by_category_id)
        products = await db.scalars(
            select(Product)
            .where(Product.category_id == category.id)
            .options(selectinload(Product.author))
        )
    else:
        products = await db.scalars(select(Product).options(selectinload(Product.author)))
    return products.all()


@router.post("/", response_model=ProductRetriveSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_data: ProductCreateSchema,
    user: Annotated[User, Depends(only_auth_user_permission)],
):
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
    product_with_author = await db.scalar(
        select(Product)
        .where(Product.id == product.id)
        .options(selectinload(Product.author))
    )
    return product_with_author


@router.get("/{product_id}", response_model=ProductRetriveSchema, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
):
    product = await db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.author))
    )

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRetriveSchema, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    product_data: ProductCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    request_user: Annotated[User, Depends(only_auth_user_permission)],
):
    product = await get_object_or_404(db, Product, Product.id == product_id)
    if request_user.id == product.author_id:
        category = await get_object_or_404(db, Category, Category.id == product_data.category_id)

        product.name = product_data.name
        product.slug = slugify(product_data.name)
        product.description = product_data.description
        product.price = product_data.price
        product.image_url = product_data.name
        product.category_id = category.id
        await db.commit()
        await db.refresh(product)
        return product
    raise HTTPException(
        detail="Not product owner",
        status_code=status.HTTP_403_FORBIDDEN,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    request_user: Annotated[User, Depends(only_auth_user_permission)],
):
    product = await get_object_or_404(db, Product, Product.id == product_id)
    if request_user.id == product.author_id:
        await db.delete(product)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        detail="Not product owner",
        status_code=status.HTTP_403_FORBIDDEN,
    )
