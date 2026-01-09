---
name: new-feature
description: Standard workflow for developing new features
triggers:
  - "/workflow new-feature"
  - "add new feature"
  - "implement feature"
---

# New Feature Development Workflow

新功能开发的标准工作流程。

## Phase 1: Planning

### 1.1 Requirements Gathering
- [ ] 明确功能需求和用户故事
- [ ] 确定技术方案
- [ ] 评估影响范围
- [ ] 创建任务分解

### 1.2 Design Review
- [ ] 创建设计文档（如需要）
- [ ] 确认API设计
- [ ] 确认数据库变更（如需要）
- [ ] 确认UI/UX设计

## Phase 2: Setup

### 2.1 Branch Creation
```bash
# 创建功能分支
git checkout main
git pull origin main
git checkout -b feat/<feature-name>
```

### 2.2 Environment Preparation
```bash
# 确保环境最新
cd "/home/dislove/document/ai 导航"
docker-compose up -d
cd ainav-backend && pip install -r requirements.txt
cd ainav-web && pnpm install
```

## Phase 3: Implementation

### 3.1 Backend Development
```
Order of implementation:
1. Database models (if needed)
2. Pydantic schemas
3. Service layer
4. API endpoints
5. Unit tests
```

**Database Migration (if needed):**
```bash
cd ainav-backend
alembic revision --autogenerate -m "add_feature_name_table"
alembic upgrade head
```

**API Development:**
```bash
# Create API file
touch app/api/v1/feature_name.py

# Register in router
# Edit app/api/v1/__init__.py
```

### 3.2 Frontend Development
```
Order of implementation:
1. Type definitions
2. API hooks (TanStack Query)
3. Components
4. Page integration
5. Component tests
```

**Component Development:**
```bash
cd ainav-web

# Create component
mkdir -p src/components/feature-name
touch src/components/feature-name/FeatureComponent.tsx
touch src/components/feature-name/index.ts
```

### 3.3 Integration
- [ ] Connect frontend to backend API
- [ ] Verify data flow
- [ ] Handle loading and error states

## Phase 4: Testing

### 4.1 Unit Tests
```bash
# Backend
cd ainav-backend
pytest tests/unit/test_feature_name.py -v

# Frontend
cd ainav-web
pnpm test src/components/feature-name
```

### 4.2 Integration Tests
```bash
# API tests
pytest tests/integration/test_api_feature_name.py -v

# E2E tests
cd ainav-web
pnpm test:e2e e2e/feature-name.spec.ts
```

### 4.3 Manual Testing
- [ ] 测试正常流程
- [ ] 测试边界情况
- [ ] 测试错误处理
- [ ] 测试移动端响应式

## Phase 5: Review & Deploy

### 5.1 Code Review Checklist
- [ ] 代码符合项目规范
- [ ] 所有测试通过
- [ ] 无安全漏洞
- [ ] 性能符合要求
- [ ] 文档已更新

### 5.2 Create Pull Request
```bash
git add .
git commit -m "feat(<scope>): <description>"
git push origin feat/<feature-name>
# Create PR on GitHub/GitLab
```

### 5.3 Deploy
```bash
# Deploy to staging first
/deploy staging

# After verification, deploy to production
/deploy production
```

## Checklist Summary

### Must Have
- [ ] 功能完整实现
- [ ] 测试覆盖率 > 80%
- [ ] 无 linting 错误
- [ ] API文档已更新
- [ ] 中文本地化完成

### Nice to Have
- [ ] 性能优化
- [ ] SEO优化
- [ ] Analytics埋点
- [ ] 错误监控集成
