from typing import Annotated
from slugify import slugify

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.routers.services import get_object_or_404
from app.models.category import Category
from app.schemas.category import (
    CategoryCreateSchema,
    CategoryRetriveSchema,
)


router = APIRouter(prefix="/category", tags=["category"])


@router.get("/", response_model=list[CategoryRetriveSchema], status_code=status.HTTP_200_OK)
async def get_all_categories(
    db: Annotated[Session, Depends(get_db)],
):
    all_categories = db.scalars(
        select(Category)
        .where(Category.is_active == True)
    ).all()

    return JSONResponse(
        content=jsonable_encoder(all_categories),
        status_code=status.HTTP_200_OK,
    )


@router.post("/", response_model=CategoryRetriveSchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    db: Annotated[Session, Depends(get_db)],
    category_data: CategoryCreateSchema,
):
    new_category = Category(
        name=category_data.name,
        slug=slugify(category_data.name),
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryRetriveSchema, status_code=status.HTTP_200_OK)
async def udate_category(
    category_id: int,
    category_data: CategoryCreateSchema,
    db: Annotated[Session, Depends(get_db)]
):
    category = get_object_or_404(db, Category, Category.id == category_id)
    category.name = category_data.name
    category.slug = slugify(category_data.name)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    category = get_object_or_404(db, Category, Category.id == category_id)
    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
