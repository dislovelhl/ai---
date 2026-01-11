# Agentic Creation Platform: Technical Guide

Agentic Creation Platform (ACP) 是本平台的核心竞争力，允许用户通过可视化或低代码方式构建、运行和分享 AI Agent 流程。

## 🌟 Key Features

- **可视化工作流**: 基于 `@xyflow/react` 的拖拽式 Agent 逻辑构建。
- **LangGraph 集成**: 在后台使用 LangGraph 引擎执行复杂的状态机 Agent。
- **版本控制**: 对 Agent 的每一个改动进行版本追踪。
- **技能系统 (Skills)**: 可扩展的工具箱，Agent 可以调用外部 API、执行 Python 代码或访问数据库。

## 🏗 Architecture (Agent Service)

Agent Service (`ainav-backend/services/agent-service/`) 独立于内容管理，专注于执行逻辑。

### 核心组件

1.  **Workflow Engine (`app/engine/langgraph_engine.py`)**:
    - 将 JSON 格式的流程图转换为 Python 可执行的 LangGraph 对象。
    - 处理节点执行、状态转换和条件分支。
2.  **Executor (`app/core/agentic_executor.py`)**:
    - 负责安全地运行 Agent。
    - 处理流式输出 (Streaming) 和中断/人机交互 (HITL)。
3.  **Memory Service (`app/core/memory_service.py`)**:
    - 基于 Redis 的持久化会话存储。
    - 支持短期记忆和基于向量数据库的长期记忆。

### 数据模型

- `AgentWorkflow`: 存储工作流的结构信息（Nodes, Edges）。
- `AgentExecution`: 记录每一次运行的实例和状态。
- `Skill`: 定义 Agent 可用的工具。

## 🚀 Creating a Workflow

### 1. 结构定义

工作流以图的形式存储：

```json
{
  "nodes": [
    { "id": "node1", "type": "llm", "data": { "model": "deepseek-chat" } },
    { "id": "node2", "type": "tool", "data": { "tool": "web_search" } }
  ],
  "edges": [{ "source": "node1", "target": "node2" }]
}
```

### 2. 执行与流式返回

客户端通过 WebSocket 或 Server-Sent Events (SSE) 接收实时节点更新。

```python
# app/routers/chat.py
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    # 调用 executor.stream_run()
    ...
```

## 🧩 Complex Workflow Examples

ACP 支持多节点编排，以下是一个典型的 **"AI 行业研究员"** 复杂工作流示例。

### 多步研究工作流 (JSON)

该流程包含：搜索 -> 数据提取 -> LLM 分析 -> 格式化输出。

```json
{
  "name": "AI Industry Researcher",
  "nodes": [
    {
      "id": "node_1",
      "type": "input",
      "data": { "label": "用户查询" }
    },
    {
      "id": "node_2",
      "type": "skill",
      "data": {
        "label": "Web Search API",
        "skill": {
          "api_endpoint": "https://api.tavily.com/search",
          "http_method": "POST",
          "headers_template": { "Content-Type": "application/json" }
        }
      }
    },
    {
      "id": "node_3",
      "type": "transform",
      "data": {
        "label": "解析搜索结果",
        "transform_type": "extract",
        "field": "results.0.content"
      }
    },
    {
      "id": "node_4",
      "type": "llm",
      "data": {
        "label": "DeepSeek 分析",
        "model": "deepseek-reasoner",
        "prompt": "基于以下搜索内容，总结 2026 年 AI 导航工具的三个核心趋势：\n\n{{input}}",
        "system_prompt": "你是一个资深的 AI 行业分析师。"
      }
    },
    {
      "id": "node_5",
      "type": "output",
      "data": { "label": "完成报告" }
    }
  ],
  "edges": [
    { "id": "e1-2", "source": "node_1", "target": "node_2" },
    { "id": "e2-3", "source": "node_2", "target": "node_3" },
    { "id": "e3-4", "source": "node_3", "target": "node_4" },
    { "id": "e4-5", "source": "node_4", "target": "node_5" }
  ]
}
```

### 核心节点说明

- **Input Node**: 接收用户的初始提问，将其注入状态机的 `messages`。
- **Skill Node**: 通过 `httpx` 调用外部 API。它会自动从上一个节点的 `results` 中提取 context 作为查询参数。
- **Transform Node**: 对非结构化数据进行处理。支持 `extract` (点号路径提取字段) 和 `template` (字符串模板填充)。
- **LLM Node**: 核心推理节点。支持 DeepSeek-V3/R1。使用 `{{input}}` 或 `{{context}}` 占位符来注入前置节点的数据。

## 🔒 Security & Sandboxing

- **API 安全**: 所有 Skill 调用都会经过后端的代理层，隐藏用户的 API Key 并进行速率限制。
- **内存隔离**: 每个执行实例拥有独立的 Redis namespace，确保多租户环境下的状态隔离。
- **异常处理**: 工作流引擎具备自动重试机制，当某个节点（如 LLM 超时）失败时，可以根据配置进行指数退避重试。

---

_Last Updated: 2026-01-09_
