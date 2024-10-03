import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Default -> Random key.
SECRET_KEY = os.getenv("SECRET_KEY", "a21679097c1ba42e9bd06eea239cdc5bf19b249e87698625cba5e3572f005544")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_LIFETIME = timedelta(minutes=10)

# DB settings:
POSTGRES_DB = os.getenv("POSTGRES_DB", "FastAPI")
POSTGRES_USER = os.getenv("POSTGRES_USER", "FastAPI")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "FastAPI")
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
