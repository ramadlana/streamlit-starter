import os
from pathlib import Path

from flask import Flask, flash, redirect, request, url_for
from flask_wtf.csrf import CSRFError, generate_csrf

from app_db import build_database_uri, db, ensure_user_role_column
from flask_app.extensions import csrf, login_manager
from flask_app.routes.admin import bp as admin_bp
from flask_app.routes.auth import bp as auth_bp
from flask_app.routes.example_crud import bp as example_crud_bp
from flask_app.routes.home import bp as home_bp
from flask_app.routes.dummydata_crud import bp as dummydata_crud_bp
from flask_app.routes.docs import bp as docs_bp
from flask_app.routes.iframe_app_streamlit import bp as iframe_app_streamlit_bp

def create_app():
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    is_debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key and not is_debug:
        raise RuntimeError(
            "Missing SECRET_KEY in production mode. "
            "Set SECRET_KEY environment variable."
        )
    app.config["SECRET_KEY"] = secret_key or "dev-only-change-this-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = build_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    csrf.init_app(app)
    setattr(login_manager, "login_view", "auth.login")
    login_manager.init_app(app)

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf}

    @app.errorhandler(CSRFError)
    def handle_csrf_error(_):
        flash("Your session expired. Please try again.")
        return redirect(request.referrer or url_for("auth.login"))

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(example_crud_bp)
    app.register_blueprint(dummydata_crud_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(iframe_app_streamlit_bp)
    with app.app_context():
        db.create_all()
        ensure_user_role_column()

    return app
