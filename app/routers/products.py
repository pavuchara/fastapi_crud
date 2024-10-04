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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.models.products import Product
from app.models.category import Category
from app.schemas.product import (
    ProductCreateSchema,
    ProductRetriveSchema,
)
from app.routers.services.utils import get_object_or_404
from app.models.services.exceptions import ProductValidationException
from app.models.services.products_utils import (
    create_product_helper,
    update_product_helper,
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
    """Список продуктов."""
    # TODO возможно эту логику можно перенести в фильтр/Depends
    if by_category_id is not None:
        category = await get_object_or_404(db, Category, Category.id == by_category_id)
        products = await db.scalars(
            select(Product)
            .where(Product.category_id == category.id)
            .where(Product.is_active == True)
            .options(
                selectinload(Product.author),
                selectinload(Product.category),
            )
        )
    else:
        products = await db.scalars(
            select(Product)
            .where(Product.is_active == True)
            .options(
                selectinload(Product.author),
                selectinload(Product.category),
            )
        )
    return products.all()


@router.post("/", response_model=ProductRetriveSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_data: ProductCreateSchema,
    user: Annotated[User, Depends(only_auth_user_permission)],
):
    """Создание продукта."""
    try:
        product = await create_product_helper(db, user, product_data)
        return product
    except ProductValidationException as e:
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except IntegrityError:
        # TODO по хорошему вычилять именно ошибку slug, а не все.
        raise HTTPException(
            detail="Slug already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/{product_id}", response_model=ProductRetriveSchema, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
):
    """Получение конкретного продукта."""
    product = await db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .where(Product.is_active == True)
        .options(
            selectinload(Product.author),
            selectinload(Product.category),
        )
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
    """Обновление продукта (только автор)."""
    try:
        product = await get_object_or_404(db, Product, Product.id == product_id)
        if request_user.id == product.author_id:
            product_with_related_fields = await update_product_helper(
                db,
                request_user,
                product,
                product_data,
            )
            return product_with_related_fields
        raise HTTPException(
            detail="Not product owner",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    except ProductValidationException as e:
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except IntegrityError:
        # TODO по хорошему вычилять именно ошибку slug, а не все.
        raise HTTPException(
            detail="Slug already exists",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    request_user: Annotated[User, Depends(only_auth_user_permission)],
):
    """Удаление продукта (только автор)."""
    product = await get_object_or_404(db, Product, Product.id == product_id)
    if request_user.id == product.author_id:
        await db.delete(product)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        detail="Not product owner",
        status_code=status.HTTP_403_FORBIDDEN,
    )
