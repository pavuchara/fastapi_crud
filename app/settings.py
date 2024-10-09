import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Default -> Random key.
SECRET_KEY = os.getenv("SECRET_KEY", "a21679097c1ba42e9bd06eea239cdc5bf19b249e87698625cba5e3572f005544")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)

# DB settings:
POSTGRES_DB = os.getenv("POSTGRES_DB", "FastAPI")
POSTGRES_USER = os.getenv("POSTGRES_USER", "FastAPI")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "FastAPI")
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"

# CORS:
ALLOW_ORIGINS = ["*"]  # TODO Fix me later
ALLOWED_HOSTS = ["*"]  # TODO Fix me later

# Loguru
LOGURU_CONF = {
    "rotation": "10 MB",
    "retention": "1 week",
    "compression": "zip",
}
