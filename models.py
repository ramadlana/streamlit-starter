# Backward-compatible import shim.
# New code should import from app_db.
from app_db import User, db

__all__ = ["db", "User"]
