from app_db.base import db
from app_db.config import build_database_uri
from app_db.docs import (
    create_or_update_document,
    get_document_by_id,
    get_document_by_slug,
    list_documents,
)
from app_db.engine import get_sql_engine
from app_db.example_crud import ensure_example_crud_table
from app_db.models import DocumentationPage, User
from app_db.user_roles import (
    ALLOWED_ROLES,
    EDITOR_MENU_ROLES,
    ROLE_CHOICES,
    ensure_user_role_column,
    normalize_role
)

__all__ = [
    "db",
    "User",
    "DocumentationPage",
    "build_database_uri",
    "get_sql_engine",
    "ensure_example_crud_table",
    "get_document_by_id",
    "get_document_by_slug",
    "list_documents",
    "create_or_update_document",
    "ALLOWED_ROLES",
    "EDITOR_MENU_ROLES",
    "ROLE_CHOICES",
    "normalize_role",
    "ensure_user_role_column",
]
