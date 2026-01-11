# Frontend Development Guide: Next.js & UI Architecture

本平台的前端基于 Next.js 15 构建，追求卓越的用户体验 (WOW Experience) 和极高的交互性能。

## 🎨 Design Philosophy

我们遵循 "Rich Aesthetics" 原则：

- **颜色**: 使用 HSL 定制的品牌色，支持完美的深色模式。
- **动效**: 广泛应用 `framer-motion` 进行微交互（Hover, Transition）。
- **材质**: 结合 Glassmorphism (玻璃拟态) 和平滑的渐变，营造高级感。

## 🏗 Directory Structure

```bash
ainav-web/src/
├── app/               # App Router pages (React Server Components)
├── components/
│   ├── ui/           # shadcn/ui 基础原子组件
│   ├── tools/        # 业务相关的工具列表和卡片
│   ├── agents/       # Agent 可视化编辑器组件
│   └── layout/       # 导航及侧边栏
├── hooks/             # 自定义 React Hooks
├── lib/               # 工具函数 (API clients, Utils)
├── stores/            # Zustand 状态管理
└── types/             # TypeScript 类型定义
```

## 🚀 Key Patterns

### 1. Data Fetching (TanStack Query)

所有动态数据获取应使用 `useQuery` 或 `useMutation`：

```typescript
const { data, isLoading } = useQuery({
  queryKey: ["tools", categoryId],
  queryFn: () => api.getTools(categoryId),
});
```

### 2. UI Components (shadcn/ui)

我们不重复造轮子。优先使用 `components/ui` 下的基础组件，并通过 `cn()` 函数定制样式。

### 3. State Management (Zustand)

轻量级状态（如侧边栏收起、搜索查询）使用 Zustand：

```typescript
interface GlobalState {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}
```

## 🛠 Available Commands

```bash
pnpm dev      # 启动开发服务器 (port 3000)
pnpm build    # 生产环境构建
pnpm lint     # 运行 ESLint 和 Prettier 检查
```

## 📱 Responsive & Performance

- **Mobile First**: 所有页面必须完美适配移动端。
- **Image Optimization**: 使用 Next.js `Image` 组件并配置 WebP 转换。
- **Code Splitting**: 复杂的 Agent 编辑器使用 `next/dynamic` 异步加载。

---

_Last Updated: 2026-01-09_
