from fastapi import FastAPI

from app.middlewares import setup_middlewares
from app.logger import init_logging

from app.routers import (
    auth,
    admin,
    category,
    user,
    rewiew,
    products,
)


app = FastAPI()

setup_middlewares(app)
init_logging()

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(products.router)
app.include_router(category.router)
app.include_router(rewiew.router)
