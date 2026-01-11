"""
Admin activity logging decorator.

Provides a decorator to automatically log admin actions to the AdminActivityLog table.
"""
from functools import wraps
from typing import Callable, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models import AdminActivityLog, User
import inspect


def log_admin_action(action_type: str, resource_type: str):
    """
    Decorator to log admin actions to AdminActivityLog.

    Args:
        action_type: Type of action ('create', 'update', 'delete', 'approve', 'reject')
        resource_type: Type of resource ('tool', 'category', 'scenario', 'workflow')

    Usage:
        @router.post("/tools")
        @log_admin_action("create", "tool")
        async def create_tool(...)

    The decorator expects the endpoint to have:
        - admin_user: User parameter (from require_admin dependency)
        - db: AsyncSession parameter (from get_db dependency)
        - Optional: request: Request parameter for IP/user-agent tracking

    For updates/deletes, it will attempt to capture old values.
    For creates/updates, it will capture new values from the response.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract dependencies from function parameters
            admin_user: Optional[User] = None
            db: Optional[AsyncSession] = None
            request: Optional[Request] = None
            resource_id = None
            old_value = None

            # Get function signature to extract parameters
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()

            # Extract admin_user, db, and request from parameters
            for param_name, param_value in bound_args.arguments.items():
                if isinstance(param_value, User):
                    admin_user = param_value
                elif isinstance(param_value, AsyncSession):
                    db = param_value
                elif isinstance(param_value, Request):
                    request = param_value
                elif param_name in ["tool_id", "category_id", "scenario_id", "workflow_id"]:
                    resource_id = param_value

            # For update/delete actions, fetch old value before operation
            if action_type in ["update", "delete"] and db and resource_id:
                old_value = await _fetch_resource_state(db, resource_type, resource_id)

            # Execute the original endpoint function
            result = await func(*args, **kwargs)

            # Extract new value and resource_id from result
            new_value = None
            if action_type in ["create", "update"]:
                if hasattr(result, "model_dump"):
                    # Pydantic model response
                    new_value = result.model_dump(mode="json")
                    if not resource_id and hasattr(result, "id"):
                        resource_id = result.id
                elif isinstance(result, dict) and "id" in result:
                    # Dict response (from delete endpoints)
                    if not resource_id:
                        resource_id = result.get("id")

            # Log the activity
            if admin_user and db:
                await _create_activity_log(
                    db=db,
                    admin_id=admin_user.id,
                    action_type=action_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    old_value=old_value,
                    new_value=new_value,
                    ip_address=_get_client_ip(request) if request else None,
                    user_agent=_get_user_agent(request) if request else None
                )

            return result

        return wrapper
    return decorator


async def _fetch_resource_state(db: AsyncSession, resource_type: str, resource_id) -> Optional[dict]:
    """
    Fetch the current state of a resource before modification.

    Args:
        db: Database session
        resource_type: Type of resource ('tool', 'category', 'scenario')
        resource_id: UUID of the resource

    Returns:
        Dict representation of the resource or None
    """
    from .repository import ToolRepository, CategoryRepository, ScenarioRepository

    try:
        if resource_type == "tool":
            repo = ToolRepository(db)
            resource = await repo.get_by_id_with_relations(resource_id)
        elif resource_type == "category":
            repo = CategoryRepository(db)
            resource = await repo.get_by_id(resource_id)
        elif resource_type == "scenario":
            repo = ScenarioRepository(db)
            resource = await repo.get_by_id(resource_id)
        else:
            return None

        if resource:
            # Convert SQLAlchemy model to dict
            from sqlalchemy.inspection import inspect as sa_inspect
            mapper = sa_inspect(resource.__class__)
            result = {}
            for column in mapper.columns:
                value = getattr(resource, column.name)
                # Convert UUID and datetime to string for JSON serialization
                if hasattr(value, 'isoformat'):
                    result[column.name] = value.isoformat()
                elif hasattr(value, 'hex'):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
            return result

        return None
    except Exception:
        # If we can't fetch the old state, just return None
        return None


async def _create_activity_log(
    db: AsyncSession,
    admin_id,
    action_type: str,
    resource_type: str,
    resource_id,
    old_value: Optional[dict],
    new_value: Optional[dict],
    ip_address: Optional[str],
    user_agent: Optional[str]
):
    """
    Create an activity log entry.

    Args:
        db: Database session
        admin_id: UUID of the admin user
        action_type: Type of action performed
        resource_type: Type of resource affected
        resource_id: UUID of the resource
        old_value: Previous state (for updates/deletes)
        new_value: New state (for creates/updates)
        ip_address: Client IP address
        user_agent: Client user agent string
    """
    try:
        log_entry = AdminActivityLog(
            admin_id=admin_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(log_entry)
        await db.commit()
    except Exception as e:
        # Don't fail the request if logging fails, just rollback the log entry
        await db.rollback()
        # In production, you might want to log this error to a monitoring service
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create activity log: {str(e)}")


def _get_client_ip(request: Request) -> Optional[str]:
    """
    Extract client IP address from request.

    Checks X-Forwarded-For header first (for proxied requests),
    then falls back to direct client IP.

    Args:
        request: FastAPI Request object

    Returns:
        IP address string or None
    """
    if not request:
        return None

    # Check X-Forwarded-For header (common in proxied setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()

    # Fall back to direct client IP
    if request.client:
        return request.client.host

    return None


def _get_user_agent(request: Request) -> Optional[str]:
    """
    Extract user agent string from request.

    Args:
        request: FastAPI Request object

    Returns:
        User agent string or None
    """
    if not request:
        return None

    user_agent = request.headers.get("User-Agent")
    # Truncate to fit in database column (max 255 chars)
    if user_agent and len(user_agent) > 255:
        return user_agent[:255]

    return user_agent
