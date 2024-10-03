from fastapi import FastAPI

from app.routers import (
    auth,
    admin,
    category,
    products,
    user,
)

app = FastAPI()


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(products.router)
app.include_router(category.router)
