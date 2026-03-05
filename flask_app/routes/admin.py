from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app_db import ROLE_CHOICES, User, db, normalize_role
from flask_app.routes.permissions import role_required

bp = Blueprint("admin", __name__)


@bp.route("/admin")
@login_required
@role_required("admin", message="Access denied: Admins only.")
def admin():
    users = User.query.all()
    return render_template("admin.html", users=users, roles=ROLE_CHOICES)


@bp.route("/admin/add", methods=["POST"])
@login_required
@role_required("admin", message="Access denied: Admins only.")
def admin_add_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    role_raw = (request.form.get("role") or "").strip().lower()
    role = normalize_role(role_raw)

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash("Username or Email already exists")
    else:
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_role(role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} added successfully with role '{role}'")

    return redirect(url_for("admin.admin"))


@bp.route("/admin/edit/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin", message="Access denied: Admins only.")
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.username = request.form.get("username")
    user.email = request.form.get("email")
    role_raw = (request.form.get("role") or "").strip().lower()
    role = normalize_role(role_raw)
    user.set_role(role)

    password = request.form.get("password")
    if password:
        user.set_password(password)

    db.session.commit()
    flash(f"User {user.username} updated with role '{role}'")
    return redirect(url_for("admin.admin"))


@bp.route("/admin/delete/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin", message="Access denied: Admins only.")
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own admin account!")
        return redirect(url_for("admin.admin"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted")
    return redirect(url_for("admin.admin"))
