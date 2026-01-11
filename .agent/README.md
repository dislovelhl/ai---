# AI导航平台 - Agent Configuration

项目专属的Agent配置，包含命令、工作流、技能和模板。

**Version:** 2.0.0 | **Updated:** 2025-01-10

## What's New in v2.0.0

- **Constitutional Principles** - Self-verification and guardrails for safe operations
- **Chain-of-Thought Reasoning** - Structured thinking before actions
- **Few-Shot Examples** - Annotated good/bad examples for learning
- **Verification Gates** - Checkpoints in workflows to catch issues early
- **Testing Framework** - Systematic evaluation of agent performance
- **Version Control** - Staged rollout and rollback procedures

## 目录结构

```
.agent/
├── config.yaml              # 主配置文件
├── README.md                # 本文档
├── commands/                # 开发命令
│   ├── dev.md              # 启动开发环境
│   ├── build.md            # 构建生产包
│   ├── test.md             # 运行测试
│   ├── lint.md             # 代码检查
│   ├── db.md               # 数据库操作
│   ├── crawl.md            # 内容爬取
│   ├── deploy.md           # 部署操作
│   └── gen.md              # 代码生成
├── workflows/               # 开发工作流
│   ├── workflow.md         # 工作流概览
│   ├── new-feature.md      # 新功能开发
│   ├── new-feature-enhanced.md  # 增强版 (v2.0)
│   ├── add-tool.md         # 添加AI工具
│   ├── api-endpoint.md     # API开发
│   ├── database-migration.md    # 数据库迁移
│   ├── content-pipeline.md      # 内容管线
│   └── bug-fix.md          # Bug修复
├── skills/                  # 开发技能
│   ├── frontend-dev.md          # 前端开发
│   ├── backend-dev.md           # 后端开发
│   ├── backend-dev-enhanced.md  # 增强版 (v2.0)
│   ├── database-ops.md          # 数据库操作
│   ├── content-automation.md    # 内容自动化
│   └── seo-optimization.md      # SEO优化
├── templates/               # 代码模板
│   ├── react-component.tsx      # React组件
│   ├── nextjs-page.tsx          # Next.js页面
│   ├── api-route.py             # FastAPI路由
│   ├── pydantic-schema.py       # Pydantic Schema
│   ├── sqlalchemy-model.py      # SQLAlchemy模型
│   └── celery-task.py           # Celery任务
├── rules/                   # 项目规范
│   ├── rule.md                  # 代码规范
│   └── constitutional-principles.md  # 宪法原则 (v2.0)
├── testing/                 # 测试框架 (v2.0)
│   └── evaluation-framework.md  # 评估框架
├── versioning/              # 版本控制 (v2.0)
│   └── version-control.md       # 版本策略
└── hooks/                   # Git钩子
```

## 快速命令

### 开发环境
```bash
/dev              # 启动所有服务
/dev frontend     # 仅前端
/dev backend      # 仅后端
```

### 构建测试
```bash
/build            # 构建生产包
/test             # 运行测试
/lint             # 代码检查
/lint fix         # 自动修复
```

### 数据库
```bash
/db migrate       # 运行迁移
/db rollback      # 回滚迁移
/db seed          # 填充数据
/db shell         # 数据库Shell
```

### 内容管理
```bash
/crawl producthunt  # 爬取Product Hunt
/crawl github       # 爬取GitHub Trending
/crawl arxiv        # 爬取ArXiv论文
/crawl status       # 查看爬取状态
```

### 代码生成
```bash
/gen component ToolCard      # 生成React组件
/gen page tools/compare      # 生成Next.js页面
/gen api compare             # 生成API路由
/gen model Comparison        # 生成数据库模型
/gen service CompareService  # 生成服务类
/gen worker screenshot       # 生成Celery任务
```

### 部署
```bash
/deploy staging     # 部署到预发布
/deploy production  # 部署到生产
/deploy rollback    # 回滚
```

## 工作流

### 新功能开发
```bash
/workflow new-feature
```
完整的功能开发流程：需求分析 → 分支创建 → 开发 → 测试 → 代码审查 → 部署

### 添加AI工具
```bash
/workflow add-tool
```
添加新AI工具的完整流程：信息收集 → 内容丰富 → 质量检查 → 发布

### API开发
```bash
/workflow api-endpoint
```
创建新API端点：Schema定义 → Service实现 → Router配置 → 测试 → 文档

### 数据库迁移
```bash
/workflow database-migration
```
安全的数据库变更流程：规划 → 开发 → 测试 → 预发布验证 → 生产部署

## 技能配置

每个技能文件包含：
- 技术栈说明
- 项目结构规范
- 代码模板
- 常用模式
- 最佳实践

## 代码模板

使用 `/gen` 命令生成代码时，会自动应用对应的模板。模板包含：
- 类型定义
- 错误处理
- 日志记录
- 测试结构
- 文档注释

## 项目规范

详见 `rules/rule.md`，包含：
- 代码风格（TypeScript/Python）
- 命名约定
- 文件结构
- Git规范
- 性能要求
- SEO要求
- 安全要求

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14+, TypeScript, Tailwind CSS, shadcn/ui |
| 后端 | FastAPI, Python 3.11+, SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 16, pgvector, Redis, Meilisearch |
| 任务队列 | Celery, Redis |
| AI | DeepSeek API, BGE-M3 embeddings |
| 部署 | Docker, Aliyun Hong Kong |

## 环境变量

开发环境所需的环境变量见各服务的 `.env.example` 文件。

## v2.0 Enhanced Features

### Constitutional Principles (宪法原则)

All agent operations now follow constitutional principles for safety and quality:

```bash
# View constitutional principles
cat .agent/rules/constitutional-principles.md
```

Key principles:
- **Pre-Action Verification** - Always verify before modifying code
- **Chain-of-Thought** - Structured reasoning for complex tasks
- **Self-Correction** - Automatic critique and revision
- **Code Quality Gates** - Mandatory quality checks
- **Security Principles** - Never generate vulnerable code

### Enhanced Skills

The `*-enhanced.md` skill files include:
- Step-by-step reasoning protocols
- Annotated few-shot examples (good vs bad)
- Verification checklists
- Common mistake patterns to avoid

### Workflow Verification Gates

Enhanced workflows include checkpoint gates:

```
Phase          Gate                    Pass Criteria
──────────────────────────────────────────────────────────
Discovery   → Requirements clear?    → Feature summary
Planning    → Tasks identified?      → Task breakdown
Design      → Approach validated?    → Technical design
Implement   → Code quality met?      → Working code
Testing     → All tests pass?        → Verified feature
Deploy      → Production stable?     → Live feature
```

### Testing Framework

Evaluate agent performance:

```bash
# Run evaluation suite
/test all --report

# Compare versions
/test compare v1.0.0 v2.0.0
```

Metrics tracked:
- Task completion rate (target: ≥90%)
- First-attempt success (target: ≥70%)
- Code quality score (target: ≥90%)
- Security violations (target: 0)

### Version Control

Staged rollout with automatic rollback:

```bash
# Check agent health
/agent health

# Start staged rollout
/agent rollout start v2.0.0

# Rollback if issues
/agent rollback --to v1.1.1
```

## 更多信息

- 设计文档: `design-specs/`
- API文档: `http://localhost:8000/docs`
- 前端: `http://localhost:3000`
- Agent v2.0 Features: `.agent/rules/constitutional-principles.md`
