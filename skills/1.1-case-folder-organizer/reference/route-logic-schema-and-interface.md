# 案由路由逻辑 - 下游接口与字段规则

> 本文档是 `route-logic.md` 的拆分版本，按阶段组织。
> 完整逻辑由以下文件组成：
> - `route-logic-overview.md` - 概述 + 触发条件
> - `route-logic-prediction.md` - 案由预判流程
> - `route-logic-user-choice-index.md` - 用户选择 + 缓存Schema
> - `route-logic-schema-and-interface.md` - 下游接口 + 字段规则
> - `route-logic-resync.md` - 缓存同步机制
> - `route-logic-fallback-and-constraints.md` - 兜底规则 + 约束

---

## 第六部分：与下游skill的接口

### 6.1 下游skill读取缓存的规范

所有下游 skill 执行时，按以下优先级读取：

```
优先级 1：案件文件夹根目录存在 .case_route_cache.json
  → 直接读取对应字段，不再路由，不再 view _index.json
  → 如需 route md 原文（超出缓存摘要时），直接 view 案件根目录的 route 文件

优先级 2：.case_route_cache.json 不存在，但案件文件夹根目录存在 route md 文件
  → 提示"建议先运行 case-folder-organizer（1.1）以生成缓存"
  → 如用户选择继续，直接 view route md 文件执行路由（降级模式）

优先级 3：.case_route_cache.json 不存在，route md 文件不存在
  → 尝试访问 case-cause-knowledge/（共享知识库）
  → 访问失败 → 输出降级警告，LLM 通用框架兜底
```

### 6.2 判断缓存是否为降级版

下游 skill 读取 `.case_route_cache.json` 后：

```
IF cause_source == "llm_fallback"
 OR cause_zh == null
 OR sections_available 为空数组
 THEN 标注 layer_s_status = "fallback"
      降级执行（质量7分）
 ELSE 标注 layer_s_status = "normal"
      正常执行（质量8.5分）
```

---

## 第八部分：字段使用规则

> 本部分对应原 1.05 SKILL.md §3.2，合并至此。

| 字段 | 消费方 | 用途 |
|------|-------|------|
| `cause_zh` + `cause_variants` | 所有下游 | 案由标准名称，用于完成通知和文书抬头 |
| `sections_available` | 所有下游 | 判断哪些节有效，避免 view 空节 |
| `s0_extract_summary` | extract-case-summary（1.2） | 追问字段清单 + 叙事重心 |
| `s1_legal_relationship` | legal-opinion（1.4）、legal-theory-analysis（2.3） | 法律关系定性直接引用 |
| `s2_plaintiff_claims` | legal-theory-analysis（2.3）代理原告时 | 请求权基础 + 构成要件主轴 |
| `s3_defendant_defenses` | legal-theory-analysis（2.3）代理被告时 | 抗辩策略主轴 |
| `s4_legal_provisions` | 所有文书类 skill | 法条引用，避免重复检索 |
| `s5_fact_narrative_template` | case-pleadings（2.6） | 事实陈述段落参考结构 |
| `s6_evidence_checklist` | evidence-list（2.5）、evidence-gap-analysis（2.2） | 标准证据分组 + 证明目的关键词 |
| `s7_trial_examination` | trial-outline（2.8）、closing-statement（2.9） | 质证要点（缺失时下游自动降级） |
| `s8_judicial_patterns` | legal-opinion（1.4）、evidence-gap-analysis（2.2） | 裁判规律 + 风险提示 |
