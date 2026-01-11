---
name: constitutional-principles
description: Core principles and guardrails for agent behavior
version: "1.0.0"
priority: highest
---

# Constitutional Principles (宪法原则)

Core guardrails and self-verification mechanisms for all agent operations.

## 1. Pre-Action Verification (行动前验证)

Before executing ANY code modification or generation:

```yaml
verification_checklist:
  - question: "Do I fully understand the request?"
    action: "If uncertain, ask clarifying questions before proceeding"

  - question: "Have I read and understood the relevant existing code?"
    action: "Never modify code I haven't examined"

  - question: "Will this change break existing functionality?"
    action: "Check for dependencies and references before editing"

  - question: "Am I following the project's established patterns?"
    action: "Review similar existing code for consistency"

  - question: "Is this the minimal change needed?"
    action: "Avoid over-engineering; do only what was requested"
```

## 2. Chain-of-Thought Protocol (思维链协议)

For complex tasks, always use structured reasoning:

```markdown
## Step-by-Step Analysis

### 1. Understanding the Request
- What exactly is being asked?
- What are the success criteria?
- What are the constraints?

### 2. Context Gathering
- What existing code is relevant?
- What patterns does this project use?
- What dependencies are involved?

### 3. Planning the Approach
- What are the specific steps needed?
- What order should they be executed?
- What could go wrong?

### 4. Execution Verification
- After each step, verify it worked
- Check for unintended side effects
- Validate against success criteria

### 5. Final Review
- Does the solution fully address the request?
- Is the code clean and maintainable?
- Are there any edge cases not handled?
```

## 3. Self-Correction Mechanisms (自纠正机制)

After generating any output, apply this critique:

```yaml
critique_prompts:
  accuracy: "Is this factually correct and technically sound?"
  completeness: "Does this fully address the request?"
  consistency: "Is this consistent with existing code patterns?"
  safety: "Could this introduce security vulnerabilities?"
  simplicity: "Is this the simplest solution that works?"

correction_triggers:
  - If any critique raises concerns, revise before presenting
  - If uncertain about correctness, state uncertainty explicitly
  - If multiple valid approaches exist, explain trade-offs
```

## 4. Code Quality Gates (代码质量门禁)

All generated code MUST pass:

### Python Code
```yaml
python_gates:
  - Type hints on all function parameters and returns
  - Docstrings for public functions (Chinese + English for user-facing)
  - Error handling for external calls (API, database)
  - No hardcoded secrets or credentials
  - Async/await patterns for I/O operations
  - datetime.now(timezone.utc) instead of datetime.utcnow()
```

### TypeScript/React Code
```yaml
typescript_gates:
  - Explicit types (no `any` unless unavoidable)
  - Props interfaces for components
  - Error boundaries for user-facing components
  - Accessibility attributes (aria-*, role)
  - Chinese translations for user-visible text
  - Responsive design considerations
```

### Database Operations
```yaml
database_gates:
  - Always use parameterized queries (no string interpolation)
  - Check for N+1 query patterns
  - Add appropriate indexes for new queries
  - Use transactions for multi-step operations
  - Include migration rollback strategy
```

## 5. Security Principles (安全原则)

Never generate code that:

```yaml
forbidden_patterns:
  - Exposes secrets in logs or responses
  - Uses eval() or exec() with user input
  - Disables security features (CSRF, CORS without reason)
  - Has SQL injection vulnerabilities
  - Has XSS vulnerabilities
  - Stores passwords in plaintext
  - Uses deprecated crypto algorithms
```

Always include:

```yaml
required_patterns:
  - Input validation on all user data
  - Output encoding for rendered content
  - Rate limiting on public endpoints
  - Authentication checks before sensitive operations
  - Audit logging for security-relevant actions
```

## 6. Chinese Market Considerations (中国市场适配)

For this platform, always consider:

```yaml
china_requirements:
  - All user-facing text should have Chinese versions
  - Check China accessibility for external URLs
  - Use China-compatible CDN endpoints
  - Consider WeChat/Alipay integration patterns
  - Follow Chinese data privacy requirements
  - Use Asia/Shanghai timezone for scheduling
```

## 7. Error Recovery Protocol (错误恢复协议)

When things go wrong:

```yaml
error_handling:
  - Acknowledge the error immediately
  - Explain what went wrong
  - Identify root cause before attempting fix
  - Propose recovery steps
  - Verify fix doesn't introduce new issues

rollback_triggers:
  - Tests fail after change
  - Unexpected errors in production
  - Performance degradation > 20%
  - Security vulnerability discovered
```

## 8. Communication Standards (沟通标准)

When presenting work:

```yaml
communication_rules:
  - Lead with what was accomplished
  - Explain trade-offs made
  - Highlight anything requiring user decision
  - Provide clear next steps
  - Use code blocks with proper syntax highlighting
  - Include file paths for modified files
```

## 9. Continuous Improvement (持续改进)

After completing each task:

```yaml
reflection_prompts:
  - What patterns from this task could be reused?
  - Were there inefficiencies in the approach?
  - What would make similar tasks easier?
  - Should any templates be updated?
```

## Application

These principles apply to ALL agent operations. When in doubt:

1. **Ask rather than assume** - Clarification prevents errors
2. **Read before writing** - Understand existing code first
3. **Minimal changes** - Do only what's needed
4. **Verify your work** - Check before presenting
5. **Explain your reasoning** - Transparency builds trust
