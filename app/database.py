from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .models import Base, User

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


def _migrate_users_table() -> None:
    """Add columns introduced after the first SQLite schema (dev-only)."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("users")}
    table = User.__table__
    dialect = engine.dialect

    with engine.begin() as conn:
        for column in table.columns:
            if column.name in existing:
                continue
            col_type = column.type.compile(dialect=dialect)
            # SQLite cannot add NOT NULL columns without a default on populated tables.
            conn.execute(
                text(f"ALTER TABLE users ADD COLUMN {column.name} {col_type} NULL")
            )

        refreshed = {col["name"] for col in inspect(conn).get_columns("users")}

        if "name" in refreshed and "contact_name" in refreshed:
            conn.execute(
                text(
                    "UPDATE users SET contact_name = name "
                    "WHERE contact_name IS NULL AND name IS NOT NULL"
                )
            )

        if "company_name" in refreshed:
            conn.execute(
                text(
                    "UPDATE users SET company_name = substr(email, 1, instr(email, '@') - 1) "
                    "WHERE (company_name IS NULL OR trim(company_name) = '') "
                    "AND instr(email, '@') > 1"
                )
            )
            conn.execute(
                text(
                    "UPDATE users SET company_name = 'Company' "
                    "WHERE company_name IS NULL OR trim(company_name) = ''"
                )
            )


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    if settings.database_url.startswith("sqlite"):
        _migrate_users_table()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
