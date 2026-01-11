# Agent Service Utilities

## Cron Validator

The `cron_validator` module provides utilities for validating cron expressions, generating human-readable descriptions, and calculating next execution times.

### Usage

```python
from services.agent_service.app.utils.cron_validator import (
    validate_cron_expression,
    get_cron_description,
    get_next_run_times,
)

# Validate a cron expression
result = validate_cron_expression("0 9 * * *", "Asia/Shanghai")
if result.is_valid:
    print(f"Description: {result.description}")
    print(f"Next runs: {result.next_runs}")
else:
    print(f"Error: {result.error}")

# Get human-readable description
description = get_cron_description("*/30 * * * *")
# Returns: "Every 30 minutes"

# Calculate next run times
next_runs = get_next_run_times("0 9 * * *", "Asia/Shanghai", count=5)
# Returns: List of 5 datetime objects in UTC
```

### Features

- **Validation**: Validates cron expressions using croniter library
- **Human-readable descriptions**: Converts cron syntax to plain English
- **Timezone support**: Calculates next runs in any timezone
- **Error handling**: Comprehensive error messages for invalid expressions

### Supported Cron Format

Standard 5-field cron format:
```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Weekday (0-6, Sunday=0)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

### Common Examples

- `* * * * *` - Every minute
- `0 * * * *` - Every hour
- `0 9 * * *` - Daily at 9:00 AM
- `*/30 * * * *` - Every 30 minutes
- `0 9 * * 1-5` - Weekdays at 9:00 AM
- `0 0 1 * *` - First day of every month at midnight
- `0 0 * * 0` - Every Sunday at midnight

### Integration with Schemas

You can use the validator in Pydantic schemas:

```python
from pydantic import validator
from services.agent_service.app.utils.cron_validator import validate_cron_expression

class ScheduleCreate(BaseModel):
    cron_expression: str
    timezone: str

    @validator('cron_expression')
    def validate_cron(cls, v, values):
        timezone = values.get('timezone', 'UTC')
        result = validate_cron_expression(v, timezone)
        if not result.is_valid:
            raise ValueError(result.error)
        return v
```
