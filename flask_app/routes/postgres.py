import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint("postgres", __name__)
_pg_engine = None


def get_postgres_engine():
    global _pg_engine
    if _pg_engine is not None:
        return _pg_engine

    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")

    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise RuntimeError(
            "Missing PostgreSQL env vars. Required: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME."
        )

    uri = (
        f"postgresql+psycopg2://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )
    _pg_engine = create_engine(uri, future=True, pool_pre_ping=True)
    return _pg_engine


def ensure_pg_items_table():
    with get_postgres_engine().begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app_items (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )


@bp.route("/pg-items")
@login_required
def pg_items():
    try:
        ensure_pg_items_table()
        with get_postgres_engine().connect() as conn:
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
    return render_template("postgres_crud.html", items=items)


@bp.route("/pg-items/create", methods=["POST"])
@login_required
def pg_items_create():
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for("postgres.pg_items"))

    try:
        ensure_pg_items_table()
        with get_postgres_engine().begin() as conn:
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
    return redirect(url_for("postgres.pg_items"))


@bp.route("/pg-items/edit/<int:item_id>", methods=["POST"])
@login_required
def pg_items_edit(item_id):
    name = (request.form.get("name") or "").strip()
    description = (request.form.get("description") or "").strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for("postgres.pg_items"))

    try:
        ensure_pg_items_table()
        with get_postgres_engine().begin() as conn:
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
    return redirect(url_for("postgres.pg_items"))


@bp.route("/pg-items/delete/<int:item_id>", methods=["POST"])
@login_required
def pg_items_delete(item_id):
    try:
        ensure_pg_items_table()
        with get_postgres_engine().begin() as conn:
            deleted = conn.execute(
                text("DELETE FROM app_items WHERE id = :item_id"),
                {"item_id": item_id},
            )
        flash("Item deleted." if deleted.rowcount else "Item not found.")
    except (RuntimeError, SQLAlchemyError) as exc:
        flash(f"Delete failed: {exc}")
    return redirect(url_for("postgres.pg_items"))
