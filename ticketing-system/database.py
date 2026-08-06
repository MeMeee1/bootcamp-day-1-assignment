import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_database_url() -> str:
    """Reads database URL from environment."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return db_url


DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
