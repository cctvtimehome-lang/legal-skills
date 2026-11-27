# 案由路由逻辑 - 兜底规则与关键约束

> 本文档是 `route-logic-index.md` 的拆分版本（原route-logic.md已按阶段拆分）。
> 完整逻辑由以下文件组成：
> - `route-logic-overview.md` - 概述 + 触发条件
> - `route-logic-prediction.md` - 案由预判流程
> - `route-logic-user-choice-index.md` - 用户选择 + 缓存Schema
> - `route-logic-schema-and-interface.md` - 下游接口 + 字段规则
> - `route-logic-resync.md` - 缓存同步机制
> - `route-logic-fallback-and-constraints.md` - 兜底规则 + 约束

---

## 第五部分：stale检测与刷新机制

### 5.1 stale检测（增量执行时）

```
IF cause_route.status == "ready"
 AND 根目录 route md 文件的 mtime > cause_route.routed_at
 THEN status → "stale"，stale_reason → "route md 文件已更新"
      提示律师：缓存可能过期，建议重新执行案由路由逻辑
```

### 5.2 刷新机制

| 触发情形 | 处理方式 |
|---------|---------|
| 案由判断有误，律师更换 route md 文件 | 重新执行路由逻辑，覆盖更新 |
| route md 文件内容更新（知识库迭代） | 重新执行路由逻辑，覆盖更新 |
| 案件阶段变化但案由不变 | 无需更新，缓存持续有效 |
| 多个案由（复合案由案件） | 律师指定主案由，写入 `cause_zh`；次案由记录在 `secondary_causes[]` 数组 |

---

## 第七部分：兜底与降级规则

| 情形 | 降级处理 |
|------|---------|
| route md 文件格式不符合八节结构 | 仅提取可识别节，其余节 exists 填 false，完成通知列出解析失败节 |
| 某节内容为空或仅有占位符 | exists 填 false，sections_pending 记录 |
| cause_of_action 无法自动识别 | Step 2.1 询问律师确认，确认后写入 |
| route md 文件体量超过 500 行 | sections 内各节只缓存摘要，`full_text` 置 null，注明"体量过大，下游 skill 直接 view" |
| 案件文件夹中有多个 md 文件 | 列出所有候选，询问律师选择，不自动猜测 |
| 用户选择"以上皆不是"且留空 | LLM降级模式，生成降级版 .case_route_cache.json |

---

## 第十部分：关键约束

> 本部分对应原 1.05 SKILL.md 第六部分，合并至此。

1. **缓存优先原则**：下游 skill 调用时，优先读取 `.case_route_cache.json`，不重复执行路由逻辑
2. **幂等性保证**：同一 route md 文件多次执行，生成相同的 `.case_route_cache.json`（覆盖更新）
3. **route md 为权威源**：`.case_route_cache.json` 是 route md 的缓存，route md 更新后需重新运行 1.1
4. **sections 完整性**：`sections_available` 与 `sections_pending` 必须互斥，不得重复列出同一节
5. **回写原子性**：回写 .case_index.json 和 .case_progress.json 时，使用 merge 而非覆盖，避免丢失其他 skill 写入的字段
6. **resync 模式禁止重生成缓存结构**：`--resync` 模式下严禁重新解析 route md，只能从已有缓存提取 metadata 或验证文件一致性，违者造成用户修改丢失
7. **大文件处理**：route md 单节超过 500 行时，仅缓存摘要，`full_text` 置 null，注明"体量过大，下游 skill 直接 view"
