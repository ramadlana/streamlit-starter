from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app_db import User, db
from flask_app.extensions import login_manager

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    try:
        user_pk = int(user_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, user_pk)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username:
            flash("Invalid username or password")
        else:
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("home.index"))
            flash("Invalid username or password")

    return render_template("login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not username:
            flash("Username is required.")
        elif not email:
            flash("Email is required.")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.")
        else:
            user_exists = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            if user_exists:
                flash("Username or email already exists")
            else:
                try:
                    new_user = User()
                    new_user.username = username
                    new_user.email = email
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.commit()
                    flash("Account created! Please login.")
                    return redirect(url_for("auth.login"))
                except ValueError:
                    flash("Invalid password.")

    return render_template("signup.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/auth-check")
def auth_check():
    if current_user.is_authenticated:
        return "Authenticated", 200
    return "Unauthorized", 401
