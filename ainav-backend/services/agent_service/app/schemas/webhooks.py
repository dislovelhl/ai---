"""
Pydantic schemas for Workflow Webhooks.
Supports external webhook triggers with security features.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import secrets


# =============================================================================
# WEBHOOK SCHEMAS
# =============================================================================

class WebhookBase(BaseModel):
    """Base schema for workflow webhook with common fields."""
    enabled: bool = Field(
        default=True,
        description="Whether the webhook is active"
    )
    allowed_ips: Optional[List[str]] = Field(
        default=None,
        description="IP whitelist for webhook requests (null = allow all)",
        examples=[["192.168.1.1", "10.0.0.0/8"]]
    )
    max_requests_per_hour: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum requests allowed per hour for rate limiting"
    )

    @validator('allowed_ips')
    def validate_allowed_ips(cls, v):
        """Basic validation of IP addresses/CIDR notation."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('allowed_ips must be a list')

            # Validate non-empty list
            if len(v) == 0:
                raise ValueError('allowed_ips cannot be an empty list (use null to allow all)')

            # Basic IP format validation
            for ip in v:
                if not ip or not ip.strip():
                    raise ValueError('IP address cannot be empty')

                # Check for basic IP format (simple check, CIDR notation allowed)
                parts = ip.strip().split('/')
                if len(parts) > 2:
                    raise ValueError(f'Invalid IP/CIDR format: {ip}')

                # Validate first part is IP-like
                ip_part = parts[0]
                octets = ip_part.split('.')
                if len(octets) != 4:
                    raise ValueError(f'Invalid IP address format: {ip_part}')

                # Validate each octet is a number 0-255
                for octet in octets:
                    try:
                        num = int(octet)
                        if num < 0 or num > 255:
                            raise ValueError(f'Invalid IP octet: {octet} (must be 0-255)')
                    except ValueError:
                        raise ValueError(f'Invalid IP octet: {octet} (must be a number)')

                # Validate CIDR mask if present
                if len(parts) == 2:
                    try:
                        mask = int(parts[1])
                        if mask < 0 or mask > 32:
                            raise ValueError(f'Invalid CIDR mask: {parts[1]} (must be 0-32)')
                    except ValueError:
                        raise ValueError(f'Invalid CIDR mask: {parts[1]} (must be a number)')

        return v


class WebhookCreate(WebhookBase):
    """Schema for creating a new workflow webhook."""
    workflow_id: UUID = Field(
        ...,
        description="ID of the workflow to trigger via webhook"
    )


class WebhookUpdate(BaseModel):
    """Schema for updating an existing workflow webhook."""
    enabled: Optional[bool] = Field(
        None,
        description="Whether the webhook is active"
    )
    allowed_ips: Optional[List[str]] = Field(
        None,
        description="IP whitelist for webhook requests (null = allow all)"
    )
    max_requests_per_hour: Optional[int] = Field(
        None,
        ge=1,
        le=10000,
        description="Maximum requests allowed per hour for rate limiting"
    )

    @validator('allowed_ips')
    def validate_allowed_ips(cls, v):
        """Basic validation of IP addresses/CIDR notation."""
        if v is not None:
            if not isinstance(v, list):
                raise ValueError('allowed_ips must be a list')

            # Validate non-empty list
            if len(v) == 0:
                raise ValueError('allowed_ips cannot be an empty list (use null to allow all)')

            # Basic IP format validation
            for ip in v:
                if not ip or not ip.strip():
                    raise ValueError('IP address cannot be empty')

                # Check for basic IP format (simple check, CIDR notation allowed)
                parts = ip.strip().split('/')
                if len(parts) > 2:
                    raise ValueError(f'Invalid IP/CIDR format: {ip}')

                # Validate first part is IP-like
                ip_part = parts[0]
                octets = ip_part.split('.')
                if len(octets) != 4:
                    raise ValueError(f'Invalid IP address format: {ip_part}')

                # Validate each octet is a number 0-255
                for octet in octets:
                    try:
                        num = int(octet)
                        if num < 0 or num > 255:
                            raise ValueError(f'Invalid IP octet: {octet} (must be 0-255)')
                    except ValueError:
                        raise ValueError(f'Invalid IP octet: {octet} (must be a number)')

                # Validate CIDR mask if present
                if len(parts) == 2:
                    try:
                        mask = int(parts[1])
                        if mask < 0 or mask > 32:
                            raise ValueError(f'Invalid CIDR mask: {parts[1]} (must be 0-32)')
                    except ValueError:
                        raise ValueError(f'Invalid CIDR mask: {parts[1]} (must be a number)')

        return v


class WebhookResponse(WebhookBase):
    """Schema for webhook response with all fields."""
    id: UUID
    workflow_id: UUID
    created_by_user_id: UUID
    webhook_url_path: str = Field(
        ...,
        description="Generated unique webhook path (append to base URL)"
    )
    webhook_secret: str = Field(
        ...,
        description="Secret token for HMAC signature validation"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookSummary(BaseModel):
    """Lightweight webhook schema for listings (excludes secret)."""
    id: UUID
    workflow_id: UUID
    webhook_url_path: str
    enabled: bool
    max_requests_per_hour: int
    allowed_ips: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PAGINATED RESPONSES
# =============================================================================

class PaginatedWebhooksResponse(BaseModel):
    """Paginated list of webhooks."""
    items: List[WebhookSummary]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# WEBHOOK TRIGGER SCHEMAS
# =============================================================================

class WebhookTriggerRequest(BaseModel):
    """Schema for incoming webhook trigger requests."""
    payload: dict = Field(
        default_factory=dict,
        description="Arbitrary JSON payload to pass to workflow execution"
    )
    signature: Optional[str] = Field(
        None,
        description="HMAC-SHA256 signature of payload (hex format)"
    )


class WebhookTriggerResponse(BaseModel):
    """Schema for webhook trigger response."""
    success: bool
    execution_id: Optional[UUID] = Field(
        None,
        description="ID of the created workflow execution"
    )
    message: str


# =============================================================================
# WEBHOOK SECRET REGENERATION
# =============================================================================

class WebhookRegenerateSecretResponse(BaseModel):
    """Schema for webhook secret regeneration response."""
    webhook_id: UUID
    new_secret: str = Field(
        ...,
        description="Newly generated webhook secret"
    )
    message: str = Field(
        default="Webhook secret regenerated successfully. Update your webhook clients with the new secret."
    )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def generate_webhook_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure webhook secret.

    Args:
        length: Length of the secret in bytes (default: 32)

    Returns:
        Hex-encoded secret string

    Example:
        >>> secret = generate_webhook_secret()
        >>> len(secret)
        64  # 32 bytes = 64 hex characters
    """
    return secrets.token_hex(length)


def generate_webhook_url_path() -> str:
    """
    Generate a unique webhook URL path.

    Returns:
        URL-safe random path string

    Example:
        >>> path = generate_webhook_url_path()
        >>> path
        'wh_a1b2c3d4e5f6g7h8'
    """
    return f"wh_{secrets.token_urlsafe(16)}"
