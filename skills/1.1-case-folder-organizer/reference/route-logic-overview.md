# 案由路由逻辑 - 概述与触发条件

> 本文档是 `route-logic-index.md` 的拆分版本（原route-logic.md已按阶段拆分）。
> 完整逻辑由以下文件组成：
> - `route-logic-overview.md` - 概述 + 触发条件
> - `route-logic-prediction.md` - 案由预判流程
> - `route-logic-user-choice-index.md` - 用户选择 + 缓存Schema
> - `route-logic-schema-and-interface.md` - 下游接口 + 字段规则
> - `route-logic-resync.md` - 缓存同步机制
> - `route-logic-fallback-and-constraints.md` - 兜底规则 + 约束

---

# 案由路由详细逻辑（概述与触发条件）

> 本文档包含案由预判、匹配、生成缓存的完整逻辑。
> 从 SKILL.md §4.5 提取，按需加载。

---

## 第一部分：触发条件

### 1.1 执行条件

**执行**：
- 首次运行，且 `.case_index.json` 中 `cause_route` 节点不存在，或 `status` 为 `not_initialized`

**静默跳过**：
- `cause_route.status` 已为 `pending_route` / `ready` / `stale`（案由已确认，无需重复）

### 1.2 案由变更检测

**主动变更**：律师在对话中说"变更案由为XXX"

**被动变更**：1.1 增量执行时，LLM 检测新文件包含的案由信息与现有 `cause_zh` 不一致

**触发后动作**：
1. 更新 `.case_index.json` `cause_route`（更新 `cause_zh`，`status` 重置为 `pending_route`）
2. 更新 `.case_progress.json`
3. 如 `.case_route_cache.json` 已存在，`status` 标 `stale`，提示律师重新运行路由逻辑
