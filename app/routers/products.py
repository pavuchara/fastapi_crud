from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from slugify import slugify

from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.category import Category
from app.schemas.product import (
    ProductCreateSchema,
    ProductRetriveSchema,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRetriveSchema], status_code=status.HTTP_200_OK)
async def get_list_products(
    db: Annotated[Session, Depends(get_db)]
):
    products = db.scalars(select(Product))
    return products


@router.post("/", response_model=ProductRetriveSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    db: Annotated[Session, Depends(get_db)],
    product_data: ProductCreateSchema,
):
    category = db.scalar(
        select(Category)
        .where(Category.id == product_data.category_id)
    )
    if not category:
        raise HTTPException(
            detail={"error": "Category does not exist"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    product = Product(
        name=product_data.name,
        slug=slugify(product_data.name),
        description=product_data.description,
        price=product_data.price,
        image_url=product_data.image_url,
        stock=product_data.stock,
        category_id=product_data.category_id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductRetriveSchema, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
    )
    if not product:
        raise HTTPException(
            detail={"error": "Product does not exists"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return product


@router.put("/{product_id}", response_model=ProductRetriveSchema, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    product_data: ProductCreateSchema,
    db: Annotated[Session, Depends(get_db)],
):
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
    )
    if not product:
        return HTTPException(
            detail={"error": "Product does not exists"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    category = db.scalar(
        select(Category)
        .where(Category.id == product_data.category_id)
    )
    if not category:
        return HTTPException(
            detail={"error": "Category does not exists"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    product.name = product_data.name
    product.slug = slugify(product_data.name)
    product.description = product_data.description
    product.price = product_data.price
    product.image_url = product_data.name
    product.category_id = product_data.category_id
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
    )
    if not product:
        raise HTTPException(
            detail={"error": "Product does not exists"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    db.delete(product)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/category/{category_id}",
    response_model=list[ProductRetriveSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_list_by_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    category = db.scalar(
        select(Category)
        .where(Category.id == category_id)
    )
    if not category:
        raise HTTPException(
            detail={"error": "Category does not exists"},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    products = db.scalars(
        select(Product)
        .where(Product.category_id == category_id)
    )
    return products
