# Backward-compatible import shim.
# New code should import from flask_app.db.
from flask_app.db import User, db

__all__ = ["db", "User"]
