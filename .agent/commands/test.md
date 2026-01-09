---
name: test
description: Run tests
usage: /test [scope]
args:
  - name: scope
    description: "all | frontend | backend | e2e | unit | integration"
    default: "all"
---

# Test Command

运行测试套件。

## Usage

```bash
/test              # 运行所有测试
/test frontend     # 前端测试
/test backend      # 后端测试
/test e2e          # 端到端测试
/test unit         # 单元测试
/test integration  # 集成测试
```

## Actions

### Frontend Tests
```bash
cd "/home/dislove/document/ai 导航/ainav-web"

# Unit tests
pnpm test

# With coverage
pnpm test:coverage

# Watch mode
pnpm test:watch
```

### Backend Tests
```bash
cd "/home/dislove/document/ai 导航/ainav-backend"
source ../.venv/bin/activate

# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific module
pytest tests/test_tools.py -v

# Watch mode
ptw
```

### E2E Tests
```bash
cd "/home/dislove/document/ai 导航/ainav-web"

# Playwright tests
pnpm test:e2e

# With UI
pnpm test:e2e --ui

# Specific browser
pnpm test:e2e --project=chromium
```

## Test Structure

### Frontend
```
ainav-web/
├── __tests__/
│   ├── components/
│   ├── hooks/
│   └── utils/
├── e2e/
│   ├── home.spec.ts
│   └── search.spec.ts
```

### Backend
```
ainav-backend/
├── tests/
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── conftest.py
```

## Coverage Targets

- Overall: > 80%
- Critical paths: > 90%
- API endpoints: 100%
