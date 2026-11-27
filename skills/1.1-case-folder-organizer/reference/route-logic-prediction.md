# 案由路由逻辑 - 案由预判流程

> 本文档是 `route-logic-index.md` 的拆分版本（原route-logic.md已按阶段拆分）。
> 完整逻辑由以下文件组成：
> - `route-logic-overview.md` - 概述 + 触发条件
> - `route-logic-prediction.md` - 案由预判流程
> - `route-logic-user-choice-index.md` - 用户选择 + 缓存Schema
> - `route-logic-schema-and-interface.md` - 下游接口 + 字段规则
> - `route-logic-resync.md` - 缓存同步机制
> - `route-logic-fallback-and-constraints.md` - 兜底规则 + 约束

---

## 第二部分：案由预判流程

### 2.1 扫描材料（按优先级）

LLM 扫描以下材料（仅在预判阶段扫描文件名，不读取文件内容）：

1. **起诉状 docx/pdf**（`role: complaint_draft / complaint_signed`）
2. **委托协议**（`0.委托发票/`，`role: engagement_contract`）
3. **案情摘要.json**（若已存在）
4. **根目录文件名**（含案由关键词）

**性能优化**：
- 仅扫描文件名和目录名（~1秒）
- 不读取文件内容（除非文件名无法判断，才进入Step 2.2）

### 2.2 匹配案由知识库

从 `case-cause-knowledge/` 扫描可用案由 route 文件列表，按三级结构匹配，置信度分级：

| 匹配结果 | 置信度 | 处理方式 |
|---------|---------|---------|
| 匹配到具体案由（第三级） | `high` | 直接作为选项1 |
| 只能匹配到中类（第二级） | `medium` | 弹窗列出该 level2 下全部 level3 供律师选择 |
| 只能匹配到大类（第一级） | `low` | 强制律师手动确认 |
| 无法访问 case-cause-knowledge/ | - | 降级为手动输入案由名称 |

### 2.3 生成 AskUserQuestion（固定4个选项）

**核心规则**：选项不超过4个。

```
AskUserQuestion：
  question: "检测到以下案由线索，请确认："
  header: "案由确认"
  options:
    - label: "[案由1]"
      description: "检测到关键词：[关键词列表]（推荐）"
    - label: "[案由2]"
      description: "检测到关键词：[关键词列表]"
    - label: "以上皆是（多案由）"
      description: "本案涉及多个法律关系"
    - label: "以上皆不是"
      description: "手动输入案由，或跳过案由路由"
```

**选项生成规则**：
- 预判到1个高置信度案由 → 选项1=该案由，选项2=空（或次高置信度）
- 预判到2个高置信度案由 → 选项1=案由1，选项2=案由2
- 预判到≥3个 → 只显示前2个，其余归入"以上皆是"
- 未预判到 → 选项1和选项2都显示"手动输入案由"
