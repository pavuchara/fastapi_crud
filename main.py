from fastapi import FastAPI

from app.routers import (
    auth,
    admin,
    category,
    user,
    rewiew,
    products,
)

app = FastAPI()
app_v1 = FastAPI()
app_v2 = FastAPI()


app_v1.include_router(auth.router)
app_v1.include_router(admin.router)
app_v1.include_router(user.router)
app_v1.include_router(products.router)
app_v1.include_router(category.router)
app_v1.include_router(rewiew.router)


app.mount("/v1", app_v1)
app.mount("/v2", app_v2)
