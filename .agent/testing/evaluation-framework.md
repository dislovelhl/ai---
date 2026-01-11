---
name: evaluation-framework
description: Agent testing and evaluation framework
version: "1.0.0"
---

# Agent Evaluation Framework (评估框架)

Comprehensive testing and validation framework for measuring agent performance.

## 1. Performance Metrics

### Task-Level Metrics

```yaml
task_metrics:
  completion_rate:
    description: "Percentage of tasks completed successfully"
    target: ">= 90%"
    calculation: "successful_tasks / total_tasks * 100"

  accuracy_score:
    description: "Correctness of generated code/content"
    target: ">= 85%"
    calculation: "correct_outputs / total_outputs * 100"

  iteration_count:
    description: "Average corrections needed per task"
    target: "<= 1.5"
    calculation: "total_corrections / total_tasks"

  first_attempt_success:
    description: "Tasks completed without corrections"
    target: ">= 70%"
    calculation: "zero_correction_tasks / total_tasks * 100"
```

### Quality Metrics

```yaml
quality_metrics:
  code_quality:
    description: "Adherence to project coding standards"
    components:
      - type_coverage: "% of functions with type hints"
      - documentation: "% of public functions with docstrings"
      - error_handling: "% of external calls with try/except"
      - pattern_compliance: "% following project patterns"
    target: ">= 90% average across components"

  security_score:
    description: "Absence of security vulnerabilities"
    checks:
      - sql_injection: "No string interpolation in queries"
      - xss_prevention: "Proper output encoding"
      - secret_exposure: "No hardcoded credentials"
      - input_validation: "All user input validated"
    target: "100% (zero violations)"

  consistency_score:
    description: "Alignment with existing codebase"
    checks:
      - naming_conventions: "Follows project naming"
      - file_organization: "Correct directory placement"
      - import_patterns: "Matches existing imports"
      - code_style: "Matches existing style"
    target: ">= 95%"
```

### Efficiency Metrics

```yaml
efficiency_metrics:
  response_time:
    description: "Time from request to completion"
    target: "Context-dependent"

  tool_efficiency:
    description: "Ratio of useful to total tool calls"
    target: ">= 80%"
    calculation: "productive_calls / total_calls * 100"

  context_usage:
    description: "Relevance of information retrieved"
    target: ">= 85% relevant"
```

---

## 2. Test Categories

### Category A: Golden Path Scenarios

Common successful use cases that should always work.

```yaml
golden_path_tests:
  - id: "GP001"
    name: "Create React Component"
    input: "/gen component ToolCard"
    expected:
      - File created at correct path
      - Component has proper TypeScript types
      - Follows project structure
      - Includes className prop

  - id: "GP002"
    name: "Add API Endpoint"
    input: "/gen api tools/compare"
    expected:
      - Router file created
      - Schema definitions included
      - Service layer connection
      - Proper error handling

  - id: "GP003"
    name: "Database Migration"
    input: "Add is_featured column to tools table"
    expected:
      - Migration file generated
      - Rollback included
      - Correct column type
      - Index if appropriate
```

### Category B: Previously Failed Tasks (Regression)

Tasks that previously caused issues.

```yaml
regression_tests:
  - id: "REG001"
    name: "Chinese Character Handling"
    input: "Create a tool with name '文心一言'"
    expected:
      - Proper UTF-8 encoding
      - No character corruption
      - Database stores correctly

  - id: "REG002"
    name: "Large File Modification"
    input: "Add method to service with 50+ existing methods"
    expected:
      - Only adds new method
      - Doesn't modify existing code
      - Correct placement in file

  - id: "REG003"
    name: "Async Context Awareness"
    input: "Create database query in async service"
    expected:
      - Uses AsyncSession
      - Proper await usage
      - No sync/async mixing
```

### Category C: Edge Cases

Unusual scenarios that should still be handled.

```yaml
edge_case_tests:
  - id: "EC001"
    name: "Empty Input Handling"
    input: "Create API endpoint for empty request body"
    expected:
      - Validates empty body
      - Returns appropriate error
      - Doesn't crash

  - id: "EC002"
    name: "Special Characters in Names"
    input: "Create component Tool-Card_v2.0"
    expected:
      - Normalizes to valid identifier
      - Warns about naming
      - Suggests alternative

  - id: "EC003"
    name: "Conflicting Requirements"
    input: "Add sync operation in async context"
    expected:
      - Identifies conflict
      - Suggests async alternative
      - Doesn't silently create issues
```

### Category D: Stress Tests

Complex multi-step tasks.

```yaml
stress_tests:
  - id: "ST001"
    name: "Full Feature Implementation"
    input: "Implement tool comparison feature with database, API, and UI"
    expected:
      - Breaks into logical steps
      - Completes all components
      - Components integrate correctly
      - Tests included

  - id: "ST002"
    name: "Cross-Service Changes"
    input: "Add field that affects multiple services"
    expected:
      - Identifies all affected services
      - Updates each appropriately
      - Maintains consistency
```

---

## 3. Evaluation Rubric

### Code Generation Scoring

```yaml
code_rubric:
  correctness: # 40 points
    compiles: 10
    runs_without_error: 10
    produces_expected_output: 10
    handles_edge_cases: 10

  quality: # 30 points
    type_safety: 8
    documentation: 7
    error_handling: 8
    code_organization: 7

  style: # 20 points
    naming_conventions: 5
    formatting: 5
    pattern_compliance: 5
    readability: 5

  security: # 10 points
    input_validation: 3
    no_vulnerabilities: 4
    secure_defaults: 3

  total: 100
  passing_score: 75
```

### Task Completion Scoring

```yaml
task_rubric:
  understanding: # 25 points
    correct_interpretation: 15
    appropriate_scope: 10

  execution: # 50 points
    all_requirements_met: 20
    correct_implementation: 20
    no_side_effects: 10

  communication: # 25 points
    clear_explanation: 10
    appropriate_detail: 10
    helpful_suggestions: 5

  total: 100
  passing_score: 70
```

---

## 4. A/B Testing Protocol

### Test Configuration

```yaml
ab_test_config:
  test_name: "Enhanced Prompts v2.0"
  start_date: "2025-01-15"
  duration_days: 14

  variants:
    control:
      name: "Current Agent"
      config: ".agent/skills/*.md"
      traffic_percentage: 50

    treatment:
      name: "Enhanced Agent"
      config: ".agent/skills/*-enhanced.md"
      traffic_percentage: 50

  sample_size:
    minimum_tasks_per_variant: 100
    confidence_level: 0.95
    minimum_detectable_effect: 0.10
```

### Evaluation Criteria

```yaml
ab_metrics:
  primary:
    - metric: "task_completion_rate"
      hypothesis: "treatment >= control + 10%"

  secondary:
    - metric: "first_attempt_success"
      hypothesis: "treatment >= control + 15%"
    - metric: "user_corrections"
      hypothesis: "treatment <= control - 20%"

  guardrails:
    - metric: "security_violations"
      threshold: "treatment <= control"
    - metric: "response_time"
      threshold: "treatment <= control * 1.1"
```

---

## 5. Continuous Monitoring

### Real-Time Dashboard Metrics

```yaml
dashboard_metrics:
  hourly:
    - task_success_rate
    - average_iterations
    - error_count

  daily:
    - completion_by_category
    - quality_scores_trend
    - user_satisfaction_proxy

  weekly:
    - performance_regression
    - new_failure_patterns
    - improvement_opportunities
```

### Alert Thresholds

```yaml
alerts:
  critical:
    - condition: "success_rate < 70%"
      action: "Immediate investigation"

    - condition: "security_violation == true"
      action: "Pause and review"

  warning:
    - condition: "success_rate < 85%"
      action: "Review recent changes"

    - condition: "avg_iterations > 2.5"
      action: "Identify problem patterns"
```

---

## 6. Improvement Tracking

### Version History

```yaml
version_history:
  v1.0.0:
    date: "2025-01-01"
    changes: "Initial agent configuration"
    metrics:
      task_success: "78%"
      first_attempt: "55%"

  v2.0.0:
    date: "2025-01-15"
    changes:
      - "Added constitutional principles"
      - "Enhanced chain-of-thought"
      - "Added few-shot examples"
      - "Implemented self-verification"
    metrics:
      task_success: "TBD"
      first_attempt: "TBD"
    expected_improvement: "+15% task success"
```

### Improvement Cycle

```
Week 1-2: Collect baseline metrics
Week 3-4: Implement improvements
Week 5-6: A/B test improvements
Week 7: Analyze results
Week 8: Full rollout or iterate
```

---

## 7. Human Evaluation Protocol

For tasks requiring subjective assessment:

```yaml
human_eval:
  evaluator_count: 3
  evaluation_method: "blind"

  questions:
    - "Does the output correctly address the request? (1-5)"
    - "Is the code quality acceptable? (1-5)"
    - "Would you need to make corrections? (Yes/No/Minor)"
    - "Is the explanation clear and helpful? (1-5)"

  inter_rater_reliability:
    method: "Krippendorff's alpha"
    threshold: ">= 0.7"
```

---

## Usage

### Running Evaluations

```bash
# Run golden path tests
/test golden-path

# Run regression tests
/test regression

# Run full evaluation suite
/test all --report

# Compare versions
/test compare v1.0.0 v2.0.0
```

### Generating Reports

```bash
# Weekly performance report
/report performance --period weekly

# A/B test results
/report ab-test --name "Enhanced Prompts v2.0"

# Improvement tracking
/report improvements --since 2025-01-01
```
