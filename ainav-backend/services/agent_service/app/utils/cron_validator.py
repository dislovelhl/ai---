"""
Cron Expression Validator and Parser.

This module provides utilities for validating cron expressions,
generating human-readable descriptions, and calculating next execution times.

Uses croniter library for accurate cron parsing and validation.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pydantic import BaseModel
import pytz
from croniter import croniter, CroniterBadCronError


class CronValidationResult(BaseModel):
    """Result of cron expression validation."""
    is_valid: bool
    description: Optional[str] = None
    error: Optional[str] = None
    next_runs: Optional[List[datetime]] = None


def validate_cron_expression(
    cron_expression: str,
    timezone_str: str = "UTC"
) -> CronValidationResult:
    """
    Validate a cron expression and return validation result with description.

    Args:
        cron_expression: Cron expression string (e.g., "0 9 * * *")
        timezone_str: Timezone for calculating next runs (e.g., "Asia/Shanghai")

    Returns:
        CronValidationResult with validation status, description, and next runs

    Examples:
        >>> result = validate_cron_expression("0 9 * * *")
        >>> print(result.is_valid)
        True
        >>> print(result.description)
        "At 09:00 every day"
    """
    if not cron_expression or not cron_expression.strip():
        return CronValidationResult(
            is_valid=False,
            error="Cron expression cannot be empty"
        )

    cron_expression = cron_expression.strip()

    # Validate format (must have 5 parts)
    parts = cron_expression.split()
    if len(parts) != 5:
        return CronValidationResult(
            is_valid=False,
            error="Cron expression must have exactly 5 parts: minute hour day month weekday"
        )

    # Validate using croniter
    try:
        # Get timezone
        try:
            tz = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            return CronValidationResult(
                is_valid=False,
                error=f"Invalid timezone: {timezone_str}"
            )

        # Test with croniter to ensure it's parseable
        now_tz = datetime.now(tz)
        cron = croniter(cron_expression, now_tz)

        # Get next 5 run times
        next_runs = []
        for _ in range(5):
            next_run = cron.get_next(datetime)
            next_runs.append(next_run.astimezone(pytz.UTC))

        # Generate human-readable description
        description = get_cron_description(cron_expression)

        return CronValidationResult(
            is_valid=True,
            description=description,
            next_runs=next_runs
        )

    except CroniterBadCronError as e:
        return CronValidationResult(
            is_valid=False,
            error=f"Invalid cron expression: {str(e)}"
        )
    except Exception as e:
        return CronValidationResult(
            is_valid=False,
            error=f"Validation error: {str(e)}"
        )


def get_cron_description(cron_expression: str) -> str:
    """
    Generate a human-readable description of a cron expression.

    Args:
        cron_expression: Cron expression string (e.g., "0 9 * * *")

    Returns:
        Human-readable description

    Examples:
        >>> get_cron_description("0 9 * * *")
        "At 09:00 every day"
        >>> get_cron_description("*/30 * * * *")
        "Every 30 minutes"
        >>> get_cron_description("0 0 * * 0")
        "At 00:00 on Sunday"
    """
    parts = cron_expression.strip().split()
    if len(parts) != 5:
        return "Invalid cron expression"

    minute, hour, day, month, weekday = parts

    # Common patterns
    if cron_expression == "* * * * *":
        return "Every minute"
    if cron_expression == "0 * * * *":
        return "Every hour"
    if cron_expression == "0 0 * * *":
        return "At midnight every day"
    if cron_expression == "0 12 * * *":
        return "At noon every day"

    # Build description parts
    description_parts = []

    # Minute and hour
    time_desc = _describe_time(minute, hour)
    if time_desc:
        description_parts.append(time_desc)

    # Day
    day_desc = _describe_day(day)
    if day_desc:
        description_parts.append(day_desc)

    # Month
    month_desc = _describe_month(month)
    if month_desc:
        description_parts.append(month_desc)

    # Weekday
    weekday_desc = _describe_weekday(weekday)
    if weekday_desc:
        description_parts.append(weekday_desc)

    if not description_parts:
        return "Custom schedule"

    return " ".join(description_parts)


def _describe_time(minute: str, hour: str) -> str:
    """Describe the time component of a cron expression."""
    # Every N minutes
    if minute.startswith("*/") and hour == "*":
        interval = minute[2:]
        return f"Every {interval} minutes"

    # Every N hours
    if minute == "0" and hour.startswith("*/"):
        interval = hour[2:]
        return f"Every {interval} hours"

    # Specific time
    if minute.isdigit() and hour.isdigit():
        hour_int = int(hour)
        minute_int = int(minute)
        return f"At {hour_int:02d}:{minute_int:02d}"

    # Multiple specific times
    if "," in hour or "," in minute:
        return "At specific times"

    # Range
    if "-" in hour or "-" in minute:
        return "During specific hours"

    if minute == "*" and hour == "*":
        return "Every minute"

    if minute != "*" and hour == "*":
        return f"At minute {minute} of every hour"

    return ""


def _describe_day(day: str) -> str:
    """Describe the day component of a cron expression."""
    if day == "*":
        return "every day"

    if day.isdigit():
        ordinal = _get_ordinal(int(day))
        return f"on the {ordinal}"

    if day.startswith("*/"):
        interval = day[2:]
        return f"every {interval} days"

    if "," in day:
        return "on specific days"

    if "-" in day:
        return "on certain days"

    return ""


def _describe_month(month: str) -> str:
    """Describe the month component of a cron expression."""
    months = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    if month == "*":
        return ""

    if month.isdigit():
        month_int = int(month)
        if 1 <= month_int <= 12:
            return f"in {months[month_int]}"

    if "," in month:
        return "in specific months"

    if "-" in month:
        return "during certain months"

    return ""


def _describe_weekday(weekday: str) -> str:
    """Describe the weekday component of a cron expression."""
    weekdays = [
        "Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday"
    ]

    if weekday == "*":
        return ""

    if weekday.isdigit():
        day_int = int(weekday)
        if 0 <= day_int <= 6:
            return f"on {weekdays[day_int]}"

    if "," in weekday:
        days = weekday.split(",")
        if all(d.isdigit() and 0 <= int(d) <= 6 for d in days):
            day_names = [weekdays[int(d)] for d in days]
            if len(day_names) == 2:
                return f"on {day_names[0]} and {day_names[1]}"
            elif len(day_names) > 2:
                return f"on {', '.join(day_names[:-1])}, and {day_names[-1]}"
            else:
                return f"on {day_names[0]}"

    if weekday == "1-5":
        return "on weekdays (Monday-Friday)"

    if weekday == "0,6" or weekday == "6,0":
        return "on weekends"

    if "-" in weekday:
        return "on certain weekdays"

    return ""


def _get_ordinal(n: int) -> str:
    """Convert a number to its ordinal string (e.g., 1 -> "1st", 2 -> "2nd")."""
    if 11 <= n <= 13:
        return f"{n}th"

    last_digit = n % 10
    if last_digit == 1:
        return f"{n}st"
    elif last_digit == 2:
        return f"{n}nd"
    elif last_digit == 3:
        return f"{n}rd"
    else:
        return f"{n}th"


def get_next_run_times(
    cron_expression: str,
    timezone_str: str = "UTC",
    count: int = 5
) -> List[datetime]:
    """
    Calculate the next N execution times for a cron expression.

    Args:
        cron_expression: Cron expression string
        timezone_str: Timezone for calculation (default: UTC)
        count: Number of next runs to calculate (default: 5)

    Returns:
        List of datetime objects (timezone-aware, in UTC)

    Raises:
        ValueError: If cron expression is invalid or timezone is unknown

    Examples:
        >>> times = get_next_run_times("0 9 * * *", "Asia/Shanghai", count=3)
        >>> len(times)
        3
    """
    if not cron_expression or not cron_expression.strip():
        raise ValueError("Cron expression cannot be empty")

    try:
        tz = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Invalid timezone: {timezone_str}")

    try:
        now_tz = datetime.now(tz)
        cron = croniter(cron_expression, now_tz)

        next_runs = []
        for _ in range(count):
            next_run = cron.get_next(datetime)
            # Convert to UTC for consistency
            next_runs.append(next_run.astimezone(pytz.UTC))

        return next_runs

    except CroniterBadCronError as e:
        raise ValueError(f"Invalid cron expression: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error calculating next run times: {str(e)}")
