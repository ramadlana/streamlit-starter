from sqlalchemy import create_engine

from app_db.config import build_database_uri

_sql_engine = None


def get_sql_engine():
    global _sql_engine
    if _sql_engine is None:
        _sql_engine = create_engine(
            build_database_uri(),
            future=True,
            pool_pre_ping=True,
        )
    return _sql_engine
