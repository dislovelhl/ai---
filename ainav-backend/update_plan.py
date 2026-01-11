import json

# Read the plan
with open('./.auto-claude/specs/020-workflow-scheduling-and-triggers/implementation_plan.json', 'r') as f:
    plan = json.load(f)

# Find and update subtask 2.3
for phase in plan['phases']:
    if phase['phase_id'] == 'phase-2':
        for subtask in phase['subtasks']:
            if subtask['subtask_id'] == '2.3':
                subtask['status'] = 'completed'
                subtask['notes'] = (
                    "Implemented Celery task in workflow_scheduler.py. "
                    "Task runs every minute via Celery Beat, finds due schedules, "
                    "executes workflows asynchronously, calculates next_run_at with "
                    "timezone-aware cron parsing using croniter and pytz. "
                    "Handles errors and prepared for email notifications."
                )
                break

# Write back
with open('./.auto-claude/specs/020-workflow-scheduling-and-triggers/implementation_plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

print("✓ Updated subtask 2.3 to completed")
