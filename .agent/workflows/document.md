---
name: document
description: Workflow for maintaining and creating project documentation
triggers:
  - "/workflow document"
  - "add documentation"
  - "update docs"
  - "document feature"
---

# Documentation Workflow

本文档定义了维护项目文档的标准流程，确保技术文档与代码实现保持同步。

## Phase 1: Assessment

- [ ] **确定范围**: 识别受新功能或变更影响的文档（如：System Architecture, API Spec, README）。
- [ ] **识别受众**: 确定文档的目标读者（开发者、管理员或最终用户）。

## Phase 2: Creation & Update

### 2.1 Technical Documentation

- [ ] **更新架构图**: 如果系统组件发生变化，更新 Mermaid 图表。
- [ ] **更新 API 文档**: 确保 `api-specification.md` 反映最新的端点和数据模型。
- [ ] **更新数据库模式**: 反映 `database-schema.md` 中的物理变更。

### 2.2 Project Guides

- [ ] **更新快速开始**: 确保 `README.md` 中的安装和运行步骤仍然有效。
- [ ] **更新开发指南**: 在 `docs/` 下记录新引入的设计模式或依赖项。

## Phase 3: Project Index Maintenance

- [ ] **更新 PROJECT_INDEX.md**:
  - 更新文件计数和模块描述。
  - 确保关键文件路径准确无误。
  - 更新版本号和最后修改日期。

## Phase 4: Verification

- [ ] **链接检查**: 验证所有相对路径和内部锚点链接。
- [ ] **排版校验**: 确保 Markdown 格式正确，无代码块闭合错误。
- [ ] **双语校验**: 核心概念需提供中英文对照。

## Checklist Summary

- [ ] `docs/` 目录下相关文件已更新
- [ ] `PROJECT_INDEX.md` 已刷新
- [ ] Mermaid 图表渲染正常
- [ ] 无拼写和逻辑错误
