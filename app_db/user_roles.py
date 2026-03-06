from sqlalchemy import text

from app_db.engine import get_sql_engine

ROLE_CHOICES = ("viewer", "editor", "approval1", "approval2", "admin")
ALLOWED_ROLES = set(ROLE_CHOICES)
DEFAULT_ROLE = "viewer"
ADMIN_ROLE = "admin"
EDITOR_MENU_ROLES = {"editor", "approval1", "approval2", "admin"}


def normalize_role(value: str) -> str:
    candidate = (value or "").strip().lower()
    if candidate in ALLOWED_ROLES:
        return candidate
    return DEFAULT_ROLE



def ensure_user_role_column():
    with get_sql_engine().begin() as conn:
        conn.execute(
            text(
                '''
                ALTER TABLE IF EXISTS "user"
                ADD COLUMN IF NOT EXISTS role VARCHAR(32)
                '''
            )
        )
        conn.execute(
            text(
                '''
                UPDATE "user"
                SET role = :default_role
                WHERE role IS NULL OR btrim(role) = ''
                '''
            ),
            {
                "default_role": DEFAULT_ROLE,
            },
        )
