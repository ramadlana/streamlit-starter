from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app_db import get_sql_engine


bp = Blueprint("dummydata_crud", __name__)


@bp.route("/dummydata-crud")
@login_required
def dummydata_crud():
    try:
        with get_sql_engine().connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT id, name, email
                    FROM dummydata
                    ORDER BY id DESC
                    """
                )
            )
            rows = result.mappings().all()
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"PostgreSQL error: {exc}")
        rows = []
    return render_template("dummydata_crud.html", rows=rows)


@bp.route("/dummydata-crud/create", methods=["POST"])
@login_required
def dummydata_crud_create():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()

    if not name or not email:
        flash("Name and email are required.")
        return redirect(url_for("dummydata_crud.dummydata_crud"))

    try:
        with get_sql_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO dummydata (name, email)
                    VALUES (:name, :email)
                    """
                ),
                {"name": name, "email": email},
            )
        flash("Row created.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Create failed: {exc}")
    return redirect(url_for("dummydata_crud.dummydata_crud"))


@bp.route("/dummydata-crud/edit/<int:item_id>", methods=["POST"])
@login_required
def dummydata_crud_edit(item_id):
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()

    if not name or not email:
        flash("Name and email are required.")
        return redirect(url_for("dummydata_crud.dummydata_crud"))

    try:
        with get_sql_engine().begin() as conn:
            updated = conn.execute(
                text(
                    """
                    UPDATE dummydata
                    SET name = :name,
                        email = :email
                    WHERE id = :item_id
                    """
                ),
                {
                    "name": name,
                    "email": email,
                    "item_id": item_id,
                },
            )
        flash("Row updated." if updated.rowcount else "Row not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Update failed: {exc}")
    return redirect(url_for("dummydata_crud.dummydata_crud"))


@bp.route("/dummydata-crud/delete/<int:item_id>", methods=["POST"])
@login_required
def dummydata_crud_delete(item_id):
    try:
        with get_sql_engine().begin() as conn:
            deleted = conn.execute(
                text("DELETE FROM dummydata WHERE id = :item_id"),
                {"item_id": item_id},
            )
        flash("Row deleted." if deleted.rowcount else "Row not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Delete failed: {exc}")
    return redirect(url_for("dummydata_crud.dummydata_crud"))

