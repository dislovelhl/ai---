"""
Pydantic schemas for Workflow Schedules.
Supports cron-based scheduling with timezone awareness.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


# =============================================================================
# TIMEZONE ENUM
# =============================================================================

class TimezoneEnum(str, Enum):
    """
    Common timezones for workflow scheduling.
    Users can select from these predefined options.
    """
    # UTC
    UTC = "UTC"

    # Asia
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_HONG_KONG = "Asia/Hong_Kong"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_SINGAPORE = "Asia/Singapore"
    ASIA_SEOUL = "Asia/Seoul"
    ASIA_DUBAI = "Asia/Dubai"
    ASIA_KOLKATA = "Asia/Kolkata"

    # Europe
    EUROPE_LONDON = "Europe/London"
    EUROPE_PARIS = "Europe/Paris"
    EUROPE_BERLIN = "Europe/Berlin"
    EUROPE_MOSCOW = "Europe/Moscow"
    EUROPE_AMSTERDAM = "Europe/Amsterdam"

    # Americas
    AMERICA_NEW_YORK = "America/New_York"
    AMERICA_CHICAGO = "America/Chicago"
    AMERICA_DENVER = "America/Denver"
    AMERICA_LOS_ANGELES = "America/Los_Angeles"
    AMERICA_TORONTO = "America/Toronto"
    AMERICA_SAO_PAULO = "America/Sao_Paulo"
    AMERICA_MEXICO_CITY = "America/Mexico_City"

    # Pacific
    AUSTRALIA_SYDNEY = "Australia/Sydney"
    AUSTRALIA_MELBOURNE = "Australia/Melbourne"
    PACIFIC_AUCKLAND = "Pacific/Auckland"


# =============================================================================
# SCHEDULE SCHEMAS
# =============================================================================

class ScheduleBase(BaseModel):
    """Base schema for workflow schedule with common fields."""
    cron_expression: str = Field(
        ...,
        max_length=100,
        description="Cron expression (e.g., '0 9 * * *' for daily at 9am)",
        examples=["0 9 * * *", "*/30 * * * *", "0 0 * * 0"]
    )
    timezone: TimezoneEnum = Field(
        default=TimezoneEnum.UTC,
        description="Timezone for schedule execution"
    )
    enabled: bool = Field(
        default=True,
        description="Whether the schedule is active"
    )

    @validator('cron_expression')
    def validate_cron_expression(cls, v):
        """Basic validation of cron expression format."""
        if not v or not v.strip():
            raise ValueError('Cron expression cannot be empty')

        parts = v.strip().split()
        if len(parts) != 5:
            raise ValueError(
                'Cron expression must have 5 parts: minute hour day month weekday'
            )

        return v.strip()


class ScheduleCreate(ScheduleBase):
    """Schema for creating a new workflow schedule."""
    workflow_id: UUID = Field(
        ...,
        description="ID of the workflow to schedule"
    )


class ScheduleUpdate(BaseModel):
    """Schema for updating an existing workflow schedule."""
    cron_expression: Optional[str] = Field(
        None,
        max_length=100,
        description="Cron expression (e.g., '0 9 * * *' for daily at 9am)"
    )
    timezone: Optional[TimezoneEnum] = Field(
        None,
        description="Timezone for schedule execution"
    )
    enabled: Optional[bool] = Field(
        None,
        description="Whether the schedule is active"
    )

    @validator('cron_expression')
    def validate_cron_expression(cls, v):
        """Basic validation of cron expression format."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Cron expression cannot be empty')

            parts = v.strip().split()
            if len(parts) != 5:
                raise ValueError(
                    'Cron expression must have 5 parts: minute hour day month weekday'
                )

            return v.strip()
        return v


class ScheduleResponse(ScheduleBase):
    """Schema for workflow schedule response with all fields."""
    id: UUID
    workflow_id: UUID
    created_by_user_id: UUID
    next_run_at: Optional[datetime] = Field(
        None,
        description="Next scheduled execution time (timezone-aware)"
    )
    last_run_at: Optional[datetime] = Field(
        None,
        description="Last successful execution time (timezone-aware)"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleSummary(BaseModel):
    """Lightweight schedule for listings."""
    id: UUID
    workflow_id: UUID
    cron_expression: str
    timezone: str
    enabled: bool
    next_run_at: Optional[datetime]
    last_run_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# PAGINATED RESPONSES
# =============================================================================

class PaginatedSchedulesResponse(BaseModel):
    """Paginated list of schedules."""
    items: list[ScheduleSummary]
    total: int
    page: int
    page_size: int
    pages: int
