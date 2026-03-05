from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app_db.base import db
from app_db.user_roles import normalize_role


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="viewer")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_role(self, role: str):
        normalized = normalize_role(role)
        self.role = normalized


class DocumentationPage(db.Model):
    __tablename__ = "documentation_pages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    summary = db.Column(db.String(320), nullable=True)
    content_html = db.Column(db.Text, nullable=False)
    tags_csv = db.Column(db.String(500), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
        index=True,
    )
