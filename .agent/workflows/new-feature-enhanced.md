---
name: new-feature-enhanced
description: Enhanced feature development workflow with verification checkpoints
version: "2.0.0"
triggers:
  - "new feature"
  - "implement feature"
  - "add functionality"
supersedes: new-feature
---

# New Feature Development Workflow (Enhanced)

Structured workflow with reasoning checkpoints and verification gates.

## Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  DISCOVERY  │ ──▶ │   PLANNING   │ ──▶ │   DESIGN    │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
┌─────────────┐     ┌──────────────┐     ┌─────┴───────┐
│   DEPLOY    │ ◀── │    TEST      │ ◀── │  IMPLEMENT  │
└─────────────┘     └──────────────┘     └─────────────┘
```

---

## Phase 1: Discovery (发现阶段)

### Objective
Fully understand the feature request before any implementation.

### Chain-of-Thought Questions

```markdown
1. **What problem does this feature solve?**
   - User pain point being addressed
   - Business value being created

2. **Who are the users?**
   - Primary user persona
   - Usage frequency and context

3. **What are the success criteria?**
   - How do we know the feature works?
   - What metrics matter?

4. **What are the constraints?**
   - Technical limitations
   - Timeline requirements
   - Dependencies on other features
```

### Verification Gate

```yaml
gate_1_discovery:
  required:
    - [ ] Feature purpose is clearly understood
    - [ ] Success criteria are defined
    - [ ] No blockers or missing information
  action_if_blocked: "Ask user for clarification before proceeding"
```

### Output
```markdown
## Feature Discovery Summary

**Feature:** [Name]
**Problem:** [What problem this solves]
**Users:** [Who will use this]
**Success Criteria:**
1. [Criterion 1]
2. [Criterion 2]

**Questions/Assumptions:**
- [Any unclear points]
```

---

## Phase 2: Planning (规划阶段)

### Objective
Break down the feature into specific implementation tasks.

### Analysis Steps

```markdown
1. **Analyze existing code:**
   - What similar features exist?
   - What patterns should be followed?
   - What can be reused?

2. **Identify components needed:**
   - Frontend components
   - API endpoints
   - Database changes
   - Background jobs

3. **Determine implementation order:**
   - Dependencies between components
   - What can be parallelized?
   - What's the critical path?
```

### Task Breakdown Template

```markdown
## Implementation Tasks

### Backend (Priority: 1)
- [ ] Task 1.1: [Database migration if needed]
- [ ] Task 1.2: [Service layer logic]
- [ ] Task 1.3: [API endpoints]

### Frontend (Priority: 2)
- [ ] Task 2.1: [UI components]
- [ ] Task 2.2: [State management]
- [ ] Task 2.3: [API integration]

### Testing (Priority: 3)
- [ ] Task 3.1: [Unit tests]
- [ ] Task 3.2: [Integration tests]
- [ ] Task 3.3: [E2E tests if applicable]
```

### Verification Gate

```yaml
gate_2_planning:
  required:
    - [ ] All necessary tasks identified
    - [ ] Dependencies mapped
    - [ ] No unknown technical risks
  action_if_blocked: "Research unclear areas before proceeding"
```

---

## Phase 3: Design (设计阶段)

### Objective
Define the technical approach before coding.

### Design Artifacts

#### API Design (if applicable)
```yaml
endpoint: POST /v1/tools/{tool_id}/compare
request:
  body:
    compare_with: list[uuid]  # IDs of tools to compare
response:
  success:
    status: 200
    body:
      comparison: ComparisonResult
  errors:
    - 404: Tool not found
    - 400: Cannot compare fewer than 2 tools
```

#### Database Schema (if applicable)
```sql
-- Migration: add_comparison_history
CREATE TABLE comparison_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    tool_ids JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comparison_user ON comparison_history(user_id);
```

#### Component Structure (if applicable)
```
components/
└── comparison/
    ├── ComparisonTable.tsx      # Main comparison display
    ├── ComparisonSelector.tsx   # Tool selection UI
    ├── ComparisonCard.tsx       # Individual tool card
    └── useComparison.ts         # Custom hook for state
```

### Verification Gate

```yaml
gate_3_design:
  required:
    - [ ] API contract defined (if applicable)
    - [ ] Database changes documented (if applicable)
    - [ ] Component structure planned (if applicable)
    - [ ] Design follows existing patterns
  action_if_blocked: "Revise design to match project conventions"
```

---

## Phase 4: Implementation (实现阶段)

### Objective
Implement the feature following the design.

### Implementation Protocol

For each task:

```markdown
### Before Starting
1. Read related existing code
2. Identify patterns to follow
3. Check for reusable utilities

### During Implementation
1. Write code incrementally
2. Test each piece as you go
3. Follow code quality gates

### After Completing
1. Self-review the code
2. Verify against requirements
3. Check for edge cases
```

### Code Quality Checkpoints

After each implementation unit:

```yaml
checkpoint_backend:
  - [ ] Type hints on all functions
  - [ ] Docstrings with Chinese + English
  - [ ] Error handling for edge cases
  - [ ] No hardcoded values
  - [ ] Async patterns correct

checkpoint_frontend:
  - [ ] TypeScript types defined
  - [ ] Props interfaces documented
  - [ ] Loading/error states handled
  - [ ] Accessibility attributes added
  - [ ] Chinese text included
```

### Verification Gate

```yaml
gate_4_implementation:
  required:
    - [ ] All planned tasks completed
    - [ ] Code follows project patterns
    - [ ] No obvious bugs or issues
  action_if_blocked: "Fix issues before proceeding to testing"
```

---

## Phase 5: Testing (测试阶段)

### Objective
Verify the feature works correctly.

### Test Coverage Requirements

```yaml
backend_tests:
  unit:
    - Service methods have test coverage
    - Edge cases are tested
    - Error paths are tested
  integration:
    - API endpoints return correct responses
    - Database operations work correctly

frontend_tests:
  unit:
    - Components render correctly
    - User interactions work
  integration:
    - API calls succeed
    - State updates correctly
```

### Manual Testing Checklist

```markdown
## Manual Test Cases

### Happy Path
- [ ] [Primary use case works end-to-end]
- [ ] [Expected data is displayed correctly]
- [ ] [User feedback is appropriate]

### Edge Cases
- [ ] [Empty state handled]
- [ ] [Error state handled]
- [ ] [Loading state shown]

### Cross-Browser (if applicable)
- [ ] Chrome
- [ ] Firefox
- [ ] Safari (if accessible)

### Responsive (if applicable)
- [ ] Desktop (1920px)
- [ ] Tablet (768px)
- [ ] Mobile (375px)
```

### Verification Gate

```yaml
gate_5_testing:
  required:
    - [ ] All unit tests pass
    - [ ] Integration tests pass
    - [ ] Manual test cases verified
    - [ ] No regressions in existing features
  action_if_blocked: "Fix failing tests before deployment"
```

---

## Phase 6: Deploy (部署阶段)

### Objective
Deploy the feature safely.

### Pre-Deployment Checklist

```yaml
pre_deploy:
  code:
    - [ ] All tests pass
    - [ ] No linting errors
    - [ ] Code reviewed (if team context)
  database:
    - [ ] Migration tested locally
    - [ ] Rollback migration exists
    - [ ] Data migration plan if needed
  config:
    - [ ] Environment variables documented
    - [ ] Feature flags configured (if applicable)
```

### Deployment Steps

```markdown
1. **Staging Deployment**
   - Deploy to staging environment
   - Run smoke tests
   - Verify feature works

2. **Production Deployment**
   - Deploy database migrations first
   - Deploy backend services
   - Deploy frontend
   - Verify in production

3. **Post-Deployment**
   - Monitor error rates
   - Check performance metrics
   - Be ready to rollback if needed
```

### Verification Gate

```yaml
gate_6_deploy:
  required:
    - [ ] Staging tests pass
    - [ ] No errors in production logs
    - [ ] Feature works in production
  action_if_issues: "Execute rollback plan"
```

---

## Rollback Plan

In case of issues:

```markdown
### Database Rollback
```bash
alembic downgrade -1
```

### Code Rollback
```bash
git revert HEAD
git push origin main
```

### Feature Flag Disable (if applicable)
```bash
# Disable feature without code change
curl -X POST /admin/features/disable -d "feature=comparison"
```
```

---

## Workflow Summary

```
Phase          Gate                         Output
────────────────────────────────────────────────────────────
Discovery   → Requirements clear?        → Feature summary
Planning    → Tasks identified?          → Task breakdown
Design      → Approach validated?        → Technical design
Implement   → Code quality met?          → Working code
Testing     → All tests pass?            → Verified feature
Deploy      → Production stable?         → Live feature
```

Each gate must pass before proceeding. If blocked, resolve issues before continuing.
