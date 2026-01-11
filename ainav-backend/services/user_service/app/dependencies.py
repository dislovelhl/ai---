"""
User service dependencies.

Re-exports shared authentication dependencies for use within the user service.
All authentication logic is now centralized in shared.auth module.
"""

from shared.auth import (
    get_db,
    get_current_user,
    get_current_user_id,
    get_current_active_user,
    get_optional_user,
    oauth2_scheme
)

# Re-export all dependencies so existing imports continue to work
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
    "get_current_active_user",
    "get_optional_user",
    "oauth2_scheme"
]
