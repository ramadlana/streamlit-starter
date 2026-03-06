"""Simple key-value app settings (e.g. allow_signup). Admin-only writes."""

from sqlalchemy import text

from app_db.engine import get_sql_engine

KEY_ALLOW_SIGNUP = "allow_signup"


def ensure_app_settings_table():
    """Create app_settings table and default row if missing."""
    with get_sql_engine().begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key VARCHAR(64) PRIMARY KEY,
                    value VARCHAR(256) NOT NULL
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO app_settings (key, value)
                VALUES (:key, 'true')
                ON CONFLICT (key) DO NOTHING
                """
            ),
            {"key": KEY_ALLOW_SIGNUP},
        )


def get_allow_signup() -> bool:
    """Return True if new sign ups are allowed, else False. Default True."""
    with get_sql_engine().connect() as conn:
        row = conn.execute(
            text("SELECT value FROM app_settings WHERE key = :key"),
            {"key": KEY_ALLOW_SIGNUP},
        ).fetchone()
    if not row:
        return True
    return (row[0] or "").strip().lower() in ("1", "true", "yes")


def set_allow_signup(allowed: bool) -> None:
    """Set whether new sign ups are allowed. Admin-only."""
    value = "true" if allowed else "false"
    with get_sql_engine().begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO app_settings (key, value)
                VALUES (:key, :value)
                ON CONFLICT (key) DO UPDATE SET value = :value
                """
            ),
            {"key": KEY_ALLOW_SIGNUP, "value": value},
        )
