---
trigger: always_on
glob: "**/*"
description: Core project rules for AI Navigation Platform
---

# AI导航平台 - 开发规范

## 项目概述

本项目是面向中国用户的下一代AI工具导航与学习平台，需要特别关注：
- 中国网络环境优化（CDN、访问性检测）
- SEO优化（百度、Google双引擎）
- 多语言支持（中文优先，英文辅助）

## 代码规范

### TypeScript/React (Frontend)

```typescript
// 组件命名：PascalCase
export function ToolCard({ tool }: ToolCardProps) { ... }

// 函数命名：camelCase
const handleSearch = async (query: string) => { ... }

// 类型定义：Interface优先
interface Tool {
  id: string
  name: string
  nameZh: string
  description: string
}

// 使用中文注释说明业务逻辑
// 工具卡片：展示AI工具的基本信息和访问状态
```

### Python (Backend)

```python
# 函数命名：snake_case
async def get_tool_by_id(tool_id: str) -> Tool:
    ...

# 类命名：PascalCase
class ToolService:
    ...

# 使用类型注解
from typing import Optional, List

# API路由使用kebab-case
@router.get("/tools/{tool_id}")
```

### 数据库

```sql
-- 表名：snake_case，复数形式
CREATE TABLE tools (
    id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_zh VARCHAR(200),  -- 中文名称
    ...
);

-- 索引命名：idx_{table}_{column}
CREATE INDEX idx_tools_category_id ON tools(category_id);
```

## 文件结构规范

### Frontend (ainav-web)
```
src/
├── app/                 # Next.js App Router
│   ├── (home)/         # 首页路由组
│   ├── tools/          # 工具页面
│   └── learn/          # 学习中心
├── components/
│   ├── ui/             # shadcn/ui基础组件
│   ├── tools/          # 工具相关组件
│   └── layout/         # 布局组件
├── lib/                # 工具函数
├── hooks/              # 自定义Hooks
├── stores/             # Zustand stores
└── types/              # 类型定义
```

### Backend (ainav-backend)
```
app/
├── api/
│   └── v1/             # API版本
│       ├── tools.py
│       └── search.py
├── core/               # 核心配置
├── models/             # SQLAlchemy模型
├── schemas/            # Pydantic schemas
├── services/           # 业务逻辑
├── workers/            # Celery任务
└── utils/              # 工具函数
```

## Git 规范

### 分支命名
- `feat/add-tool-comparison` - 新功能
- `fix/search-result-empty` - Bug修复
- `docs/api-documentation` - 文档更新

### Commit 格式
```
<type>(<scope>): <description>

feat(tools): 添加工具对比功能
fix(search): 修复空搜索结果问题
docs(api): 更新API文档
```

## 性能要求

- 首屏加载时间 (LCP): < 2.5s
- 搜索响应时间: < 200ms
- API响应时间: < 100ms (P95)
- Core Web Vitals: 全部达到"良好"标准

## SEO 要求

- 所有页面必须有唯一的 title 和 description
- 使用语义化HTML标签
- 图片必须有 alt 属性
- 实现结构化数据 (JSON-LD)
- 支持 SSR/ISR 渲染

## 安全要求

- 所有用户输入必须验证和清洗
- API必须实现速率限制
- 敏感配置使用环境变量
- 实现CORS白名单
- SQL查询使用参数化

## 中国网络优化

- 静态资源使用国内CDN
- 实现工具访问性检测
- 提供访问方式提示（直连/代理）
- 图片使用WebP格式 + 懒加载
