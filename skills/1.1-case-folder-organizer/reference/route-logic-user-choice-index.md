# 案由路由逻辑 - 用户选择与缓存生成（索引）

> 本文档是 `route-logic-user-choice.md` 的拆分版本（原317行）。
> 
> **拆分原因**：原文件包含两个语义独立的部分（用户选择处理 + 缓存Schema），且超过300行阈值，LLM加载时容易上下文漂移。
> 
> **拆分时间**：2026-05-15

---

## 文件组成

| 文件 | 内容 | 适用场景 |
|------|------|----------|
| `route-logic-user-choice-processing.md` | 第三部分：用户选择后的处理逻辑（3.1/3.2/3.3） | LLM处理用户选择、生成缓存、回写索引时 |
| `route-logic-user-choice-schema.md` | 第四部分：缓存生成Schema（4.1/4.2） | LLM生成 `.case_route_cache.json` 时作为格式参考 |

---

## 使用场景导航

### 场景A：用户已选择案由，需要生成缓存
**加载**：`route-logic-user-choice-processing.md`
**内容**：3.1（单一案由）/ 3.2（多案由）/ 3.3（LLM降级）

### 场景B：需要了解缓存JSON的完整格式
**加载**：`route-logic-user-choice-schema.md`
**内容**：4.1（正常版Schema）/ 4.2（降级版Schema）

### 场景C：首次加载，需要了解全貌
**加载**：本索引文件 → 根据实际需要加载对应文件

---

## 与其他文件的关系

- **上游**：`route-logic-overview.md`（触发条件）→ `route-logic-prediction.md`（预判流程）→ 本文档
- **下游**：`route-logic-schema-and-interface.md`（下游接口）→ `route-logic-resync.md`（同步机制）

---

## 原文件信息

| 项目 | 值 |
|------|-----|
| 原文件 | `route-logic-user-choice.md` |
| 原行数 | 317行 |
| 拆分后总文件数 | 3个（含本索引） |
| 拆分后单行文件最大行数 | ~140行 |
