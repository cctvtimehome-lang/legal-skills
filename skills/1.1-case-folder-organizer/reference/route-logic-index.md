# 案由路由逻辑索引

> 本文档是 `route-logic.md` 的拆分版本，按阶段组织。
> 完整的案由路由逻辑由以下6个文件组成，按需加载。

---

## 文件清单

| 文件名 | 内容 | 行数 | 大小 | 使用场景 |
|--------|------|------|------|---------|
| **route-logic-overview.md** | 概述 + 触发条件 | ~50行 | 5KB | 了解全貌、判断是否需要路由 |
| **route-logic-prediction.md** | 案由预判流程 | ~50行 | 8KB | 首次路由、预判案由 |
| **route-logic-user-choice-index.md** | 用户选择后处理 + 缓存Schema（索引） | ~50行 | 3KB | 了解拆分结构、按需加载 |
| **route-logic-user-choice-processing.md** | 用户选择后处理逻辑 | ~100行 | 8KB | 用户选择后、生成缓存 |
| **route-logic-user-choice-schema.md** | 缓存生成Schema | ~140行 | 9KB | 生成.case_route_cache.json |
| **route-logic-schema-and-interface.md** | 下游接口 + 字段规则 | ~70行 | 10KB | 下游skill开发、字段使用 |
| **route-logic-resync.md** | 缓存同步机制 | ~100行 | 8KB | 增量执行、resync模式 |
| **route-logic-fallback-and-constraints.md** | 兜底规则 + 约束 | ~70行 | 3KB | 异常处理、约束检查 |

---

## 使用指南

### 场景1：首次路由（完整流程）
```
1. 读取 route-logic-overview.md       (5KB)  ← 了解全貌和触发条件
2. 读取 route-logic-prediction.md    (8KB)  ← 预判案由
3. 读取 route-logic-user-choice-index.md   (3KB)  ← 了解拆分结构
   → 根据场景加载 processing 或 schema 文件
4. 参考 route-logic-schema-and-interface.md (10KB) ← 生成缓存
```

### 场景2：增量执行（stale检测）
```
1. 读取 route-logic-overview.md       (5KB)  ← 了解stale检测规则
2. 读取 route-logic-resync.md         (8KB)  ← 执行resync
```

### 场景3：resync模式（仅同步metadata）
```
1. 读取 route-logic-resync.md         (8KB)  ← 完整的resync逻辑
```

### 场景4：兜底处理（选项4 + 留空）
```
1. 读取 route-logic-overview.md                (5KB)  ← 了解降级模式
2. 读取 route-logic-fallback-and-constraints.md (3KB)  ← 兜底规则
```

### 场景5：下游skill开发（读取缓存）
```
1. 读取 route-logic-schema-and-interface.md (10KB) ← 字段使用规则
```

---

## 与原 route-logic.md 的对比

| 维度 | 原文件（600行） | 拆分后（6个文件） | 优势方 |
|------|----------------|------------------|--------|
| **上下文占用** | 一次性 23KB | 按需 3-12KB | 拆分后 ✅ |
| **焦点清晰度** | 可能飘移 ⚠️ | 清晰 ✅ | 拆分后 ✅ |
| **修改安全性** | 容易引入bug ⚠️ | 安全 ✅ | 拆分后 ✅ |
| **查找效率** | 全文搜索 ✅ | 按文件查找 ✅ | 相当 |
| **学习曲线** | 一次性理解较难 ⚠️ | 分阶段理解 ✅ | 拆分后 ✅ |

---

## 文件依赖关系

```
route-logic-overview.md (入口)
    ├── 触发条件 → route-logic-prediction.md
    ├── 用户选择 → route-logic-user-choice-index.md
    │       ├── 处理逻辑 → route-logic-user-choice-processing.md
    │       └── 缓存Schema → route-logic-user-choice-schema.md
    ├── 增量执行 → route-logic-resync.md
    └── 兜底处理 → route-logic-fallback-and-constraints.md
```

---

## 维护说明

### 修改逻辑时
1. **修改预判流程** → 只编辑 `route-logic-prediction.md`
2. **修改用户选择处理** → 只编辑 `route-logic-user-choice-processing.md`
   │       或 `route-logic-user-choice-schema.md`（视修改内容而定）
3. **修改resync逻辑** → 只编辑 `route-logic-resync.md`
4. **修改兜底规则** → 只编辑 `route-logic-fallback-and-constraints.md`

### 新增内容时
1. 判断属于哪个阶段
2. 在对应的文件中添加
3. 如果跨多个阶段，在 `route-logic-overview.md` 中添加索引

---

## 常见问题

### Q1: 如何知道需要读取哪个文件？
**A**: 先读取 `route-logic-overview.md`（5KB），了解全貌后按需读取。

### Q2: 拆分后，LLM会忘记前面的内容吗？
**A**: 不会。每个文件都是独立的逻辑单元，LLM可以深度理解（50-260行）。

### Q3: 如果需要一次性理解所有逻辑怎么办？
**A**: 可以连续读取多个文件（总大小23KB），但通常不需要。

### Q4: 修改了一个文件，其他文件需要同步修改吗？
**A**: 通常不需要。每个文件是独立的逻辑单元。如果修改了接口（如缓存Schema），才需要同步更新 `route-logic-schema-and-interface.md`。

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-12 | 创建 `route-logic.md`（600行，23KB） |
| v2.0 | 2026-05-15 | 按阶段拆分为6个文件（方案A） |

---

**最后更新**: 2026-05-15
**维护者**: case-folder-organizer (1.1)
