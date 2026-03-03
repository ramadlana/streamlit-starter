# Backward-compatible import shim.
# New code should import from app_db.models.
from app_db.models import User

__all__ = ["User"]
