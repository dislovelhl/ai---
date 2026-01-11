---
name: version-control
description: Agent version control and deployment strategy
version: "1.0.0"
---

# Agent Version Control Strategy (版本控制策略)

Systematic versioning, staged rollout, and rollback procedures.

## 1. Version Naming

### Semantic Versioning

```
Format: v[MAJOR].[MINOR].[PATCH]
Example: v2.1.3

MAJOR: Breaking changes or significant capability redesign
  - New workflow paradigms
  - Removed features
  - Constitutional principle changes

MINOR: New capabilities or substantial improvements
  - New skills added
  - Enhanced chain-of-thought
  - New few-shot examples
  - Performance optimizations

PATCH: Bug fixes and minor adjustments
  - Typo corrections
  - Template fixes
  - Documentation updates
  - Minor prompt tweaks
```

### Version Examples

```yaml
versions:
  v1.0.0: "Initial agent configuration"
  v1.1.0: "Added SEO optimization skill"
  v1.1.1: "Fixed template typo in API route"
  v2.0.0: "Constitutional principles + chain-of-thought"
  v2.1.0: "Added evaluation framework"
```

---

## 2. Change Documentation

### Changelog Format

```markdown
# Changelog

## [v2.0.0] - 2025-01-15

### Added
- Constitutional principles for self-verification
- Chain-of-thought reasoning protocols
- Few-shot examples in backend-dev skill
- Testing and evaluation framework

### Changed
- Enhanced workflow with verification gates
- Improved error handling patterns

### Deprecated
- Old backend-dev.md (superseded by backend-dev-enhanced.md)

### Removed
- None

### Fixed
- datetime.utcnow() usage replaced with timezone-aware

### Security
- Added input validation requirements
- SQL injection prevention patterns
```

### Change Request Template

```markdown
## Change Request

**Title:** [Brief description]
**Type:** Feature | Improvement | Fix | Security
**Priority:** High | Medium | Low
**Version Target:** v[X.Y.Z]

### Description
[Detailed explanation of the change]

### Motivation
[Why this change is needed]

### Testing Plan
[How the change will be validated]

### Rollback Plan
[How to revert if issues arise]

### Checklist
- [ ] Constitutional principles reviewed
- [ ] Existing tests pass
- [ ] New tests added (if applicable)
- [ ] Documentation updated
```

---

## 3. Staged Rollout

### Rollout Phases

```
Phase     Traffic   Duration   Success Criteria
───────────────────────────────────────────────
Alpha       5%      1 day      No critical errors
Beta       20%      3 days     Success rate >= 85%
Canary     50%      3 days     Success rate >= 88%
GA        100%      -          Stable performance
```

### Phase Definitions

```yaml
alpha:
  traffic: 5%
  audience: "Internal testing only"
  duration: "24 hours minimum"
  success_criteria:
    - No critical errors
    - No security violations
    - Basic functionality works
  rollback_trigger:
    - Any security issue
    - >5% error rate
    - Critical bug reported

beta:
  traffic: 20%
  audience: "Early adopters / power users"
  duration: "3 days minimum"
  success_criteria:
    - Success rate >= 85%
    - No increase in corrections
    - Positive user feedback
  rollback_trigger:
    - Success rate < 80%
    - >10% increase in corrections
    - Multiple user complaints

canary:
  traffic: 50%
  audience: "50% of all users"
  duration: "3 days minimum"
  success_criteria:
    - Success rate >= 88%
    - Corrections <= baseline
    - No performance regression
  rollback_trigger:
    - Success rate < 85%
    - Performance degradation >10%
    - Error patterns emerging

general_availability:
  traffic: 100%
  monitoring: "Continue for 7 days"
  success_criteria:
    - Success rate >= 90%
    - All metrics at or above baseline
```

### Traffic Splitting Implementation

```yaml
# .agent/config.yaml
routing:
  strategy: "percentage"
  variants:
    stable:
      version: "v1.1.1"
      weight: 50
    canary:
      version: "v2.0.0"
      weight: 50

  rules:
    # Always use stable for critical operations
    - match:
        workflow: ["deploy", "database-migration"]
      route: stable

    # Route specific users to canary
    - match:
        user_segment: "beta_testers"
      route: canary
```

---

## 4. Rollback Procedures

### Automatic Rollback Triggers

```yaml
auto_rollback:
  enabled: true

  triggers:
    - metric: "error_rate"
      threshold: ">10%"
      window: "5 minutes"

    - metric: "success_rate"
      threshold: "<75%"
      window: "15 minutes"

    - metric: "security_violations"
      threshold: ">0"
      window: "immediate"

  action:
    - Revert to previous stable version
    - Alert team immediately
    - Log incident details
    - Pause further rollouts
```

### Manual Rollback Process

```markdown
## Rollback Procedure

### 1. Identify Issue
- Review error logs
- Identify affected component
- Assess severity

### 2. Execute Rollback
```bash
# Revert to previous version
git checkout v1.1.1 -- .agent/

# Or use version control command
/agent rollback --to v1.1.1
```

### 3. Verify Recovery
- [ ] Error rate normalized
- [ ] Success rate recovered
- [ ] No lingering issues

### 4. Post-Mortem
- Document what went wrong
- Identify root cause
- Plan prevention measures
```

### Rollback Communication

```markdown
## Rollback Notification

**Time:** [Timestamp]
**Version Reverted:** v2.0.0 → v1.1.1
**Reason:** [Brief description]
**Impact:** [User/system impact]
**Resolution ETA:** [If known]

### Timeline
- [Time]: Issue detected
- [Time]: Rollback initiated
- [Time]: Rollback completed
- [Time]: Verification complete

### Next Steps
1. Investigate root cause
2. Fix and re-test
3. Plan new rollout
```

---

## 5. Version Archive

### File Structure

```
.agent/
├── versions/
│   ├── current/          # Symlink to active version
│   ├── v1.0.0/
│   ├── v1.1.0/
│   ├── v1.1.1/
│   └── v2.0.0/
├── changelog.md
└── rollback-history.md
```

### Archive Policy

```yaml
archive:
  retain_versions: 5
  retention_days: 90

  always_keep:
    - current version
    - last stable version
    - any version with known issues (for reference)

  archive_process:
    - Compress old version files
    - Store in separate archive
    - Update version index
```

---

## 6. Comparison Tools

### Version Diff

```bash
# Compare two versions
/agent diff v1.1.1 v2.0.0

# Show specific file changes
/agent diff v1.1.1 v2.0.0 --file skills/backend-dev.md

# Performance comparison
/agent compare-performance v1.1.1 v2.0.0
```

### Migration Guide

When upgrading major versions:

```markdown
## Migration Guide: v1.x → v2.0

### Breaking Changes
1. **Constitutional principles required**
   - All operations now require self-verification
   - Action: Review new `rules/constitutional-principles.md`

2. **Enhanced skills supersede old skills**
   - `backend-dev.md` replaced by `backend-dev-enhanced.md`
   - Action: Update any direct skill references

### New Features
1. Chain-of-thought reasoning
2. Few-shot examples
3. Verification gates in workflows

### Recommended Actions
1. Read constitutional principles document
2. Review enhanced skill examples
3. Test with sample tasks before full adoption
```

---

## 7. Monitoring Dashboard

### Key Metrics to Track

```yaml
dashboard:
  real_time:
    - current_version
    - traffic_distribution
    - error_rate_by_version
    - success_rate_by_version

  daily:
    - version_performance_comparison
    - rollback_events
    - user_corrections_by_version

  weekly:
    - version_adoption_curve
    - performance_trends
    - issue_patterns
```

### Health Check

```bash
# Check agent health
/agent health

# Output:
# Version: v2.0.0
# Status: Healthy
# Success Rate (24h): 91.2%
# Error Rate (24h): 2.1%
# Active Rollout: Canary (50%)
# Last Rollback: None in 7 days
```

---

## Quick Reference

```
Command                              Description
────────────────────────────────────────────────────────────
/agent version                       Show current version
/agent versions                      List all versions
/agent rollback --to v1.1.1          Rollback to version
/agent diff v1 v2                    Compare versions
/agent health                        Check agent health
/agent rollout start v2.0.0          Start staged rollout
/agent rollout pause                 Pause current rollout
/agent rollout resume                Resume paused rollout
/agent rollout complete              Complete rollout (100%)
```
