from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from app_db import normalize_role


def role_required(*allowed_roles, message="Access denied."):
    allowed = {normalize_role(role) for role in allowed_roles if role}

    def outer(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            role = normalize_role(getattr(current_user, "role", "viewer"))
            if role in allowed:
                return fn(*args, **kwargs)
            flash(message)
            return redirect(url_for("home.index"))

        return inner

    return outer


def admin_required(message="Access denied: Admins only."):
    return role_required("admin", message=message)
