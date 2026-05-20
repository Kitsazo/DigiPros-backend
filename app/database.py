from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .models import Base

if settings.database_url.startswith("sqlite"):
    _connect_args: dict = {"check_same_thread": False}
elif settings.database_url.startswith("postgresql"):
    # Fail fast when Postgres is unreachable instead of hanging startup.
    _connect_args = {"connect_timeout": 5}
else:
    _connect_args = {}
engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
