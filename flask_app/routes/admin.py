from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app_db import ROLE_CHOICES, User, db, normalize_role
from flask_app.routes.permissions import role_required

bp = Blueprint("admin", __name__)

USERNAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 150
MIN_PASSWORD_LENGTH = 8


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
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    role_raw = (request.form.get("role") or "").strip().lower()
    role = normalize_role(role_raw)

    add_modal_param = {"open": "addModal"}

    if not username:
        flash("Username is required.")
        return redirect(url_for("admin.admin", **add_modal_param))
    if len(username) > USERNAME_MAX_LENGTH:
        flash("Username is too long.")
        return redirect(url_for("admin.admin", **add_modal_param))
    if not email:
        flash("Email is required.")
        return redirect(url_for("admin.admin", **add_modal_param))
    if len(email) > EMAIL_MAX_LENGTH:
        flash("Email is too long.")
        return redirect(url_for("admin.admin", **add_modal_param))
    if len(password) < MIN_PASSWORD_LENGTH:
        flash("Password must be at least 8 characters.")
        return redirect(url_for("admin.admin", **add_modal_param))
    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash("Username or Email already exists")
        return redirect(url_for("admin.admin", **add_modal_param))

    try:
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.set_role(role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} added successfully with role '{role}'")
    except ValueError:
        flash("Invalid password.")
        return redirect(url_for("admin.admin", **add_modal_param))

    return redirect(url_for("admin.admin"))


@bp.route("/admin/edit/<int:user_id>", methods=["POST"])
@login_required
@role_required("admin", message="Access denied: Admins only.")
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    role_raw = (request.form.get("role") or "").strip().lower()
    role = normalize_role(role_raw)

    if not username:
        flash("Username is required.")
        return redirect(url_for("admin.admin"))
    if len(username) > USERNAME_MAX_LENGTH:
        flash("Username is too long.")
        return redirect(url_for("admin.admin"))
    if not email:
        flash("Email is required.")
        return redirect(url_for("admin.admin"))
    if len(email) > EMAIL_MAX_LENGTH:
        flash("Email is too long.")
        return redirect(url_for("admin.admin"))
    other_with_username = User.query.filter(User.username == username, User.id != user_id).first()
    if other_with_username:
        flash("Another user already has that username.")
        return redirect(url_for("admin.admin"))
    other_with_email = User.query.filter(User.email == email, User.id != user_id).first()
    if other_with_email:
        flash("Another user already has that email.")
        return redirect(url_for("admin.admin"))

    if len(password) > 0 and len(password) < MIN_PASSWORD_LENGTH:
        flash("Password must be at least 8 characters, or leave blank to keep current.")
        return redirect(url_for("admin.admin"))

    user.username = username
    user.email = email
    user.set_role(role)
    if password:
        try:
            user.set_password(password)
        except ValueError:
            flash("Invalid password.")
            return redirect(url_for("admin.admin"))

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
