---
name: lint
description: Run linters and formatters
usage: /lint [scope]
args:
  - name: scope
    description: "all | frontend | backend | fix"
    default: "all"
---

# Lint Command

运行代码检查和格式化。

## Usage

```bash
/lint           # 检查所有代码
/lint frontend  # 检查前端代码
/lint backend   # 检查后端代码
/lint fix       # 自动修复问题
```

## Actions

### Frontend Linting
```bash
cd "/home/dislove/document/ai 导航/ainav-web"

# ESLint
pnpm lint

# TypeScript check
pnpm type-check

# Prettier check
pnpm prettier --check .

# Fix issues
pnpm lint --fix
pnpm prettier --write .
```

### Backend Linting
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate

# Ruff (fast Python linter)
ruff check app/

# Type checking
mypy app/

# Format check
ruff format --check app/

# Fix issues
ruff check --fix app/
ruff format app/
```

### Full Lint (Pre-commit)
```bash
cd "/home/dislove/document/ai 导航"

# Run all pre-commit hooks
pre-commit run --all-files
```

## Configuration Files

### Frontend (ainav-web/.eslintrc.js)
```javascript
module.exports = {
  extends: ['next/core-web-vitals', 'prettier'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    'react-hooks/exhaustive-deps': 'warn',
  },
}
```

### Backend (ainav-backend/pyproject.toml)
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N", "UP", "B", "C4"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### Pre-commit (.pre-commit-config.yaml)
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: local
    hooks:
      - id: eslint
        name: eslint
        entry: bash -c 'cd ainav-web && pnpm lint'
        language: system
        types: [typescript, tsx]
```

## Common Issues

### Frontend
- **Unused imports**: Remove or use `// @ts-ignore` for necessary cases
- **Hook dependencies**: Add missing deps or use `// eslint-disable-next-line`
- **Type errors**: Fix types or use `as unknown as Type` for complex cases

### Backend
- **Import sorting**: Run `ruff check --fix --select I`
- **Type annotations**: Add missing annotations
- **Line too long**: Break into multiple lines
