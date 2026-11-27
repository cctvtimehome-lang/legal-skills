# 案由路由逻辑 - 缓存同步机制#

> 本文档是 `route-logic-index.md` 的拆分版本（原route-logic.md已按阶段拆分）。
> 完整逻辑由以下文件组成：
> - `route-logic-overview.md` - 概述 + 触发条件
> - `route-logic-prediction.md` - 案由预判流程
> - `route-logic-user-choice-index.md` - 用户选择 + 缓存Schema
> - `route-logic-schema-and-interface.md` - 下游接口 + 字段规则
> - `route-logic-resync.md` - 缓存同步机制
> - `route-logic-fallback-and-constraints.md` - 兜底规则 + 约束

---

## 第九部分：缓存同步机制（--resync 模式）

> 本部分对应原 1.05 SKILL.md 第七部分，合并至此。
> resync 模式的完整逻辑由 case-folder-organizer（1.1）第十部分定义，此处描述与下游 skill 的接口。

### 9.1 触发场景

`--resync` 模式在以下场景自动或手动触发：

1. 下游 skill 执行前检测到 route md 已被用户修改（mtime 变化）
2. 用户手动执行 `/case-folder-organizer --resync`

### 9.2 resync 模式行为约束

| 行为 | 正常模式 | resync 模式 |
|------|----------|------------|
| 重新解析 route md | ✅ | ❌ 禁止 |
| 重新生成缓存结构 | ✅ | ❌ 禁止 |
| 读取已有缓存 | ❌ | ✅ |
| 验证 route md 与缓存一致性 | ❌ | ✅ |
| 更新 `.case_route_cache.json`（metadata 部分） | ✅ | ✅ |
| 更新 metadata.execution_count | ✅ | ❌ 不变 |
| 更新 metadata.resync_count | ❌ | ✅ +1 |
| 更新 metadata.last_resync | ❌ | ✅ |

### 9.3 resync 执行流程（由 1.1 执行）

```
Step R-1：定位已有缓存
  → 在案件根目录查找 ".case_route_cache.json"
  → 找不到 → 报错："未找到 .case_route_cache.json，无法执行 resync"
  → 找到 → 继续
  
Step R-2：检查 route md 文件状态
  → 读取缓存中 metadata.source_route_md 字段
  → 检查该文件是否存在
  → 不存在 → 标注 "source_route_md_missing"，跳过一致性检查
  → 存在 → 继续
  
Step R-3：验证一致性（仅当 route md 存在时）
  → 计算 route md 当前 mtime
  → 与 metadata.source_route_md_mtime 比对
  → 一致 → 标注 "cache_valid"，无需更新
  → 不一致 → 标注 "cache_stale"，执行 Step R-4
  
Step R-4：更新 metadata（仅当 cache_stale 时）
  → 读取已有 .case_route_cache.json
  → 获取 route md 文件的当前 mtime（= 新 mtime）
  → 保留所有数据字段不变
  → 仅更新 metadata：
      resync_count + 1
      last_resync = current_timestamp
      source_route_md_mtime = 新 mtime
  → 写入文件（覆盖更新）
  
Step R-5：输出结果
  → cache_valid："✅ 缓存已是最新，无需更新。"
  → cache_stale："✅ 缓存 metadata 已同步（第 {N} 次 resync）。\n⚠️ 注意：route md 内容已变更，建议重新执行 case-folder-organizer（1.1 正常模式）以更新缓存数据。"
  → source_route_md_missing：报错，提示用户确认 route md 文件状态
```

### 9.4 一致性验证失败处理

resync 模式仅验证 metadata，不重新解析 route md。若 route md 内容已变更但用户未重新运行 1.1，下游 skill 将读到过时数据。

验证失败时：
```
警告信息：
  "⚠️ route md 文件已变更（mtime 不一致）。
   缓存数据为旧版本，可能不准确。
   建议处理方式：
   1) 手动重新执行 case-folder-organizer（1.1 正常模式，会重新解析 route md）
   2) 忽略，强制使用现有缓存（风险：数据可能不一致）"
```

### 9.5 下游 skill 缓存检查逻辑（供下游 skill 实现参考）

下游 skill（如 extract-case-summary、legal-theory-analysis）执行前须执行以下检查：

```
Check 1：.case_route_cache.json 是否存在？
  NO → 标注 `layer_status = "missing"`，降级处理（直接 view route md 或 LLM 兜底）
  YES → 继续
  
Check 2：缓存中 metadata.source_route_md 文件是否存在？
  NO → 标注 `layer_status = "source_route_md_missing"`，按缺失层级处理
  YES → 继续
  
Check 3：计算 source_route_md 当前 mtime，与 metadata.source_route_md_mtime 比对
  mtime 一致 → 缓存有效，直接使用，标注 `layer_status = "valid"`
  mtime 不一致 → 缓存过期，尝试静默 resync
    成功 → 标注 `layer_status = "stale_resynced"`，继续使用缓存（但提示数据可能过时）
    失败 → 标注 `layer_status = "stale_resync_failed"`，报错，提示用户选择：
      1) 手动重新执行 case-folder-organizer（1.1 正常模式，会重新解析 route md）
      2) 忽略，强制使用现有缓存（风险：数据可能不一致）
      3) 取消执行
```

### 9.6 实现备注

- resync 模式不重新解析 route md，仅更新 metadata 中的时间戳和计数
- 若 route md 内容已变更，必须提醒用户重新执行正常模式
- 正常模式执行时，metadata.execution_count +1，metadata.resync_count 不变
- 下游 skill 检测到缓存过期时，应优先提示用户重新执行正常模式，而非依赖 resync
