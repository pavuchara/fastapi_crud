from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from loguru import logger

from app.settings import ALLOW_ORIGINS, ALLOWED_HOSTS


def setup_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

    @app.middleware("http")
    async def exception_handling_middleware(request: Request, call_next):
        try:
            logger.info(f"{request.method} {request.url}")
            return await call_next(request)
        except Exception as e:
            logger.error(f"{e} http_path={request.url}")
            return JSONResponse(
                content="Something went wrong",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
