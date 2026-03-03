import secrets
from pathlib import Path

from flask import Flask

from flask_app.extensions import db, login_manager
from flask_app.routes.admin import bp as admin_bp
from flask_app.routes.auth import bp as auth_bp
from flask_app.routes.home import bp as home_bp
from flask_app.routes.postgres import bp as postgres_bp


def create_app():
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    setattr(login_manager, "login_view", "auth.login")
    login_manager.init_app(app)

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(postgres_bp)

    with app.app_context():
        db.create_all()

    return app
