import os


def build_database_uri() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return database_url

    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")

    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise RuntimeError(
            "Missing PostgreSQL configuration. Set DATABASE_URL or "
            "DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME."
        )

    return (
        f"postgresql+psycopg2://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )
