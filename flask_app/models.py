# Backward-compatible import shim.
# New code should import from flask_app.db.models.
from flask_app.db.models import User

__all__ = ["User"]
