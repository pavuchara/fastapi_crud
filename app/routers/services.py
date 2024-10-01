from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session


def get_object_or_404(db_session: Session, model, expression):
    instance = db_session.scalar(
        select(model)
        .where(expression)
    )
    if not instance:
        raise HTTPException(detail="Not found", status_code=status.HTTP_404_NOT_FOUND)
    return instance
