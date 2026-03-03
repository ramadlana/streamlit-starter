from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app_db import User, db

bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(
            current_user, "is_admin", False
        ):
            flash("Access denied: Admins only.")
            return redirect(url_for("home.index"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/admin")
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template("admin.html", users=users)


@bp.route("/admin/add", methods=["POST"])
@login_required
@admin_required
def admin_add_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    is_admin = True if request.form.get("is_admin") else False

    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash("Username or Email already exists")
    else:
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.is_admin = is_admin
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User {username} added successfully")

    return redirect(url_for("admin.admin"))


@bp.route("/admin/edit/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.username = request.form.get("username")
    user.email = request.form.get("email")
    user.is_admin = True if request.form.get("is_admin") else False

    password = request.form.get("password")
    if password:
        user.set_password(password)

    db.session.commit()
    flash(f"User {user.username} updated")
    return redirect(url_for("admin.admin"))


@bp.route("/admin/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own admin account!")
        return redirect(url_for("admin.admin"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted")
    return redirect(url_for("admin.admin"))
