import re
from typing import Optional

from sqlalchemy import text

from app_db.engine import get_sql_engine
from app_db.models import DocumentationPage


SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    normalized = (value or "").strip().lower()
    normalized = SLUG_PATTERN.sub("-", normalized)
    return normalized.strip("-") or "doc"


def normalize_tags(tags_csv: str) -> str:
    raw_items = [item.strip().lower() for item in (tags_csv or "").split(",")]
    deduped = []
    seen = set()
    for item in raw_items:
        if not item:
            continue
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return ",".join(deduped)


def _ensure_unique_slug(base_slug: str, doc_id: Optional[int] = None) -> str:
    candidate = base_slug
    suffix = 2
    while True:
        query = DocumentationPage.query.filter_by(slug=candidate)
        if doc_id is not None:
            query = query.filter(DocumentationPage.id != doc_id)
        exists = query.first()
        if not exists:
            return candidate
        candidate = f"{base_slug}-{suffix}"
        suffix += 1


def get_document_by_id(doc_id: int) -> Optional[DocumentationPage]:
    return DocumentationPage.query.get(doc_id)


def get_document_by_slug(slug: str) -> Optional[DocumentationPage]:
    return DocumentationPage.query.filter_by(slug=slug).first()


def create_or_update_document(
    *,
    doc_id: int,
    title: str,
    content_html: str,
    summary: str,
    tags_csv: str,
    created_by: int,
    slug: Optional[str] = None,
) -> DocumentationPage:
    title_clean = (title or "").strip()
    summary_clean = (summary or "").strip()
    tags_clean = normalize_tags(tags_csv)
    slug_base = slugify(slug or title_clean)

    if doc_id > 0:
        page = DocumentationPage.query.get_or_404(doc_id)
        page.title = title_clean
        page.summary = summary_clean or None
        page.content_html = content_html
        page.tags_csv = tags_clean or None
        page.slug = _ensure_unique_slug(slug_base, doc_id=page.id)
        return page

    page = DocumentationPage()
    page.title = title_clean
    page.summary = summary_clean or None
    page.content_html = content_html
    page.tags_csv = tags_clean or None
    page.created_by = created_by
    page.slug = _ensure_unique_slug(slug_base)
    return page


def list_documents(search: str = "", tag: str = "", *, page: int = 1, per_page: int = 12):
    search_term = (search or "").strip().lower()
    tag_term = (tag or "").strip().lower()
    safe_page = max(1, int(page or 1))
    safe_per_page = max(1, min(100, int(per_page or 12)))

    where_clauses = []
    params = {}
    order_by_sql = "updated_at DESC, id DESC"

    if search_term:
        where_clauses.append(
            "("
            "lower(title) LIKE :search "
            "OR lower(slug) LIKE :search "
            "OR lower(coalesce(content_html, '')) LIKE :search"
            ")"
        )
        params["search"] = f"%{search_term}%"
        order_by_sql = (
            "CASE "
            "WHEN lower(title) LIKE :search OR lower(slug) LIKE :search THEN 0 "
            "WHEN lower(coalesce(content_html, '')) LIKE :search THEN 1 "
            "ELSE 2 "
            "END, updated_at DESC, id DESC"
        )

    if tag_term:
        where_clauses.append("position(:tag_token in concat(',', coalesce(tags_csv, ''), ',')) > 0")
        params["tag_token"] = f",{tag_term},"

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    count_query = text(
        f"""
        SELECT count(*) AS total
        FROM documentation_pages
        {where_sql}
        """
    )

    data_query = text(
        f"""
        SELECT id, title, slug, summary, content_html, tags_csv, created_at, updated_at
        FROM documentation_pages
        {where_sql}
        ORDER BY {order_by_sql}
        LIMIT :limit_value
        OFFSET :offset_value
        """
    )

    with get_sql_engine().connect() as conn:
        total = conn.execute(count_query, params).scalar_one()
        total_pages = max(1, (int(total or 0) + safe_per_page - 1) // safe_per_page)
        safe_page = min(safe_page, total_pages)
        offset = (safe_page - 1) * safe_per_page
        result = conn.execute(
            data_query,
            {**params, "limit_value": safe_per_page, "offset_value": offset},
        )
        return {
            "items": result.mappings().all(),
            "total": int(total or 0),
            "page": safe_page,
            "per_page": safe_per_page,
        }
