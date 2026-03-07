import os
import uuid
import re
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app_db import (
    create_or_update_document,
    db,
    get_all_tags,
    get_document_by_id,
    get_document_by_slug,
    list_documents,
    normalize_role,
    User,
)
from app_db.user_roles import EDITOR_MENU_ROLES
from app_db.docs_attachments import (
    cleanup_orphaned_files,
    get_docs_attachments_dir,
    get_legacy_attachments_dir,
)
from flask_app.routes.permissions import admin_required, role_required

bp = Blueprint("docs", __name__)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
TAG_RE = re.compile(r"<[^>]+>")
DOCS_PER_PAGE_OPTIONS = (12, 24, 48, 96)
MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def _preview_text(summary, content_html, max_words=40):
    source = (summary or "").strip()
    if not source or source.lower() in {"none", "null", "n/a", "-"}:
        source = TAG_RE.sub(" ", content_html or "")
    words = [word for word in source.split() if word]
    if not words:
        return ""
    preview = " ".join(words[:max_words])
    if len(words) > max_words:
        preview += "..."
    return preview


def _decorate_docs(rows):
    docs = []
    for row in rows:
        item = dict(row)
        item["preview_text"] = _preview_text(item.get("summary"), item.get("content_html"))
        docs.append(item)
    return docs


def _can_manage_docs(user) -> bool:
    return normalize_role(getattr(user, "role", "viewer")) in EDITOR_MENU_ROLES


def _parse_positive_int(raw_value, default_value):
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return default_value
    return parsed if parsed > 0 else default_value


def _build_pagination(page, total_pages):
    if total_pages <= 1:
        return []

    pages = [1, total_pages]
    for candidate in range(page - 2, page + 3):
        if 1 < candidate < total_pages:
            pages.append(candidate)
    ordered = sorted(set(pages))

    tokens = []
    prev = None
    for item in ordered:
        if prev is not None and item - prev > 1:
            tokens.append(None)
        tokens.append(item)
        prev = item
    return tokens


def _pagination_context(page_data):
    total = page_data["total"]
    per_page = page_data["per_page"]
    page = page_data["page"]
    total_pages = max(1, (total + per_page - 1) // per_page)
    safe_page = min(max(1, page), total_pages)
    return {
        "page": safe_page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": safe_page > 1,
        "has_next": safe_page < total_pages,
        "pages": _build_pagination(safe_page, total_pages),
    }



def _attachments_dir() -> Path:
    return get_docs_attachments_dir()


@bp.route("/docs")
@login_required
def docs_index():
    search = (request.args.get("q") or "").strip()
    tags = request.args.getlist("tags")
    page = _parse_positive_int(request.args.get("page"), 1)
    per_page_raw = _parse_positive_int(request.args.get("per_page"), DOCS_PER_PAGE_OPTIONS[0])
    per_page = per_page_raw if per_page_raw in DOCS_PER_PAGE_OPTIONS else DOCS_PER_PAGE_OPTIONS[0]
    page_data = list_documents(search=search, tags=tags, page=page, per_page=per_page)
    return render_template(
        "docs_index.html",
        docs=_decorate_docs(page_data["items"]),
        query=search,
        active_tags=tags,
        available_tags=get_all_tags(),
        can_manage_docs=_can_manage_docs(current_user),
        per_page_options=DOCS_PER_PAGE_OPTIONS,
        pagination=_pagination_context(page_data),
        pagination_endpoint="docs.docs_index",
        pagination_kwargs={},
    )


@bp.route("/docs/tag/<string:tag>")
@login_required
def docs_by_tag(tag: str):
    safe_tag = (tag or "").strip().lower()
    if not safe_tag:
        return redirect(url_for("docs.docs_index"))
    kwargs = {"tags": [safe_tag]}
    if request.args.get("q"):
        kwargs["q"] = request.args.get("q")
    if request.args.get("per_page"):
        kwargs["per_page"] = request.args.get("per_page")
    if request.args.get("page"):
        kwargs["page"] = request.args.get("page")
    return redirect(url_for("docs.docs_index", **kwargs))


@bp.route("/docs/<string:slug>")
@login_required
def docs_view(slug: str):
    doc = get_document_by_slug(slug)
    if not doc:
        abort(404)
    tags = [tag for tag in (doc.tags_csv or "").split(",") if tag]
    creator = db.session.get(User, doc.created_by)
    return render_template(
        "docs_view.html",
        doc=doc,
        tags=tags,
        creator_name=creator.username if creator else "Unknown",
        can_manage_docs=_can_manage_docs(current_user),
    )


@bp.route("/docs/editor/<int:doc_id>", methods=["GET", "POST"])
@login_required
@role_required(
    "editor",
    "approval1",
    "approval2",
    "admin",
    message="Access denied: You only have view permission for docs.",
)
def docs_editor(doc_id: int):
    if doc_id < 0:
        abort(404)
    doc = None
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        slug = (request.form.get("slug") or "").strip()
        summary = (request.form.get("summary") or "").strip()
        tags_csv = (request.form.get("tags") or "").strip()
        content_html = (request.form.get("content_html") or "").strip()

        if not title:
            flash("Title is required.")
            return redirect(url_for("docs.docs_editor", doc_id=doc_id))

        if not content_html:
            flash("Content is required.")
            return redirect(url_for("docs.docs_editor", doc_id=doc_id))

        saved = create_or_update_document(
            doc_id=doc_id,
            title=title,
            slug=slug,
            summary=summary,
            tags_csv=tags_csv,
            content_html=content_html,
            created_by=current_user.id,
        )
        # New docs: create_or_update_document returns an unsaved instance; add to session.
        if doc_id <= 0:
            db.session.add(saved)
        db.session.commit()
        flash("Document saved.")
        return redirect(url_for("docs.docs_view", slug=saved.slug))

    if doc_id > 0:
        doc = get_document_by_id(doc_id)
        if not doc:
            abort(404)

    return render_template(
        "docs_editor.html",
        doc=doc,
        available_tags=get_all_tags(),
    )


@bp.route("/docs/upload-image", methods=["POST"])
@login_required
def docs_upload_image():
    if not _can_manage_docs(current_user):
        return jsonify({"error": "Forbidden"}), 403

    if request.content_length is None:
        return jsonify({"error": "Content-Length required."}), 400
    if request.content_length > MAX_IMAGE_UPLOAD_BYTES:
        return jsonify({"error": "Image too large. Maximum size is 10 MB."}), 413

    image = request.files.get("image")
    if image is None or not image.filename:
        return jsonify({"error": "No image uploaded."}), 400

    original_name = secure_filename(image.filename)
    extension = Path(original_name).suffix.lower()
    mime_type = (image.mimetype or "").lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS and not mime_type.startswith("image/"):
        return jsonify({"error": "Unsupported image format."}), 400

    # Keep storage names collision-safe and extension-preserving.
    ext = extension if extension else ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    destination = _attachments_dir() / filename
    image.save(destination)

    image_url = url_for("docs.docs_attachment", filename=filename)
    return jsonify({"url": image_url})


@bp.route("/docs/attachments/<path:filename>")
@login_required
def docs_attachment(filename: str):
    safe_name = os.path.basename(filename)
    if not safe_name:
        abort(404)
    docs_dir = _attachments_dir()
    docs_candidate = docs_dir / safe_name
    if docs_candidate.exists():
        return send_from_directory(docs_dir, safe_name)

    legacy_dir = get_legacy_attachments_dir()
    legacy_candidate = legacy_dir / safe_name
    if legacy_candidate.exists():
        return send_from_directory(legacy_dir, safe_name)
    abort(404)


@bp.route("/docs/admin/attachments-housekeeping", methods=["POST"])
@login_required
@admin_required()
def docs_admin_attachments_housekeeping():
    mode = (request.form.get("mode") or "dry-run").strip().lower()
    apply_changes = mode == "apply"
    delete_permanently = (request.form.get("delete_permanently") or "").strip() == "1"
    include_legacy = (request.form.get("include_legacy") or "").strip() == "1"
    min_age_minutes_raw = (request.form.get("min_age_minutes") or "0").strip()
    try:
        min_age_minutes = max(0, int(min_age_minutes_raw))
    except ValueError:
        min_age_minutes = 0

    result = cleanup_orphaned_files(
        apply_changes=apply_changes,
        delete_permanently=delete_permanently,
        include_legacy=include_legacy,
        min_age_minutes=min_age_minutes,
    )

    if apply_changes:
        if delete_permanently:
            flash(
                f"Housekeeping done. Deleted {len(result['deleted'])} orphan files. "
                f"Skipped recent: {len(result['skipped_recent'])}."
            )
        else:
            flash(
                f"Housekeeping done. Moved {len(result['moved'])} orphan files to trash. "
                f"Skipped recent: {len(result['skipped_recent'])}. "
                f"(min_age_minutes={result['min_age_minutes']})"
            )
    else:
        flash(
            f"Dry-run: found {result['orphaned_count']} orphan files. "
            f"Skipped recent: {len(result['skipped_recent'])}. "
            f"(min_age_minutes={result['min_age_minutes']})"
        )
    return redirect(url_for("docs.docs_index"))


@bp.route("/docs/admin/delete/<int:doc_id>", methods=["POST"])
@login_required
@role_required(
    "editor",
    "approval1",
    "approval2",
    "admin",
    message="Access denied: You only have view permission for docs.",
)
def docs_admin_delete_document(doc_id: int):
    doc = get_document_by_id(doc_id)
    if not doc:
        flash("Document not found.")
        return redirect(url_for("docs.docs_index"))

    db.session.delete(doc)
    db.session.commit()
    flash(f"Document '{doc.title}' deleted.")
    return redirect(url_for("docs.docs_index"))
