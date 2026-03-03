from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app_db import ensure_example_crud_table, get_sql_engine

bp = Blueprint("example_crud", __name__)


@bp.route("/example-crud")
@login_required
def example_crud():
    try:
        ensure_example_crud_table()
        with get_sql_engine().connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT id, name, description, created_at, updated_at
                    FROM app_items
                    ORDER BY id DESC
                    """
                )
            )
            items = result.mappings().all()
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"PostgreSQL error: {exc}")
        items = []
    return render_template("example_crud.html", items=items)


@bp.route("/example-crud/create", methods=["POST"])
@login_required
def example_crud_create():
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for("example_crud.example_crud"))

    try:
        ensure_example_crud_table()
        with get_sql_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO app_items (name, description)
                    VALUES (:name, :description)
                    """
                ),
                {"name": name, "description": description or None},
            )
        flash("Item created.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Create failed: {exc}")
    return redirect(url_for("example_crud.example_crud"))


@bp.route("/example-crud/edit/<int:item_id>", methods=["POST"])
@login_required
def example_crud_edit(item_id):
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for("example_crud.example_crud"))

    try:
        ensure_example_crud_table()
        with get_sql_engine().begin() as conn:
            updated = conn.execute(
                text(
                    """
                    UPDATE app_items
                    SET name = :name,
                        description = :description,
                        updated_at = NOW()
                    WHERE id = :item_id
                    """
                ),
                {
                    "name": name,
                    "description": description or None,
                    "item_id": item_id,
                },
            )
        flash("Item updated." if updated.rowcount else "Item not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Update failed: {exc}")
    return redirect(url_for("example_crud.example_crud"))


@bp.route("/example-crud/delete/<int:item_id>", methods=["POST"])
@login_required
def example_crud_delete(item_id):
    try:
        ensure_example_crud_table()
        with get_sql_engine().begin() as conn:
            deleted = conn.execute(
                text("DELETE FROM app_items WHERE id = :item_id"),
                {"item_id": item_id},
            )
        flash("Item deleted." if deleted.rowcount else "Item not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Delete failed: {exc}")
    return redirect(url_for("example_crud.example_crud"))
