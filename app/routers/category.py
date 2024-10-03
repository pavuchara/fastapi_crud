from typing import Annotated
from slugify import slugify

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.routers.services.utils import get_object_or_404
from app.routers.services.permissions import (
    only_admin_permission,
    only_auth_user_permission,
)
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryCreateSchema,
    CategoryRetriveSchema,
)


router = APIRouter(prefix="/category", tags=["category"])


@router.get("/", response_model=list[CategoryRetriveSchema], status_code=status.HTTP_200_OK)
async def get_all_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_auth_user_permission)],
):
    categories = await db.scalars(
        select(Category)
        .where(Category.is_active == True)
    )
    return categories.all()


@router.post("/", response_model=CategoryRetriveSchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_data: CategoryCreateSchema,
    _: Annotated[User, Depends(only_admin_permission)],
):
    new_category = Category(
        name=category_data.name,
        slug=slugify(category_data.name),
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryRetriveSchema, status_code=status.HTTP_200_OK)
async def udate_category(
    category_id: int,
    category_data: CategoryCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_admin_permission)],
):
    category = await get_object_or_404(db, Category, Category.id == category_id)
    category.name = category_data.name
    category.slug = slugify(category_data.name)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(only_admin_permission)],
):
    category = await get_object_or_404(db, Category, Category.id == category_id)
    await db.delete(category)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
