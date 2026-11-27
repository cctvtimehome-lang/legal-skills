# 案由路由逻辑 - 用户选择后的处理逻辑

> 本文档是 `route-logic-user-choice.md` 的拆分版本（第三部分）。
> 完整逻辑由以下文件组成：
> - `route-logic-user-choice-index.md` - 索引
> - `route-logic-user-choice-processing.md` - 本文档（第三部分）
> - `route-logic-user-choice-schema.md` - 第四部分（缓存Schema）
> 
> **适用场景**：LLM处理用户选择、生成缓存、回写索引时加载本文档。

---

## 第三部分：用户选择后的处理逻辑

### 3.1 用户选择选项1或选项2（单一案由）

```
Step 3.1.1：读取对应的 route md 文件
  → 从 case-cause-knowledge/ 读取 [案由].md
  
Step 3.1.2：解析 route md 文件结构（八节）
  → 解析以下节（sections_available 中存在的节才解析）：
     §零  案情摘要提取要点
     §一  法律关系定性与权利义务
     §二  原告视角：请求权攻防
     §三  被告视角：抗辩策略
     §四  高频争议焦点与常用法条索引
     §五  事实叙述模板
     §六  标准证据清单
     §七  庭审质证要点
     §八  常见裁判规律与风险提示
  
  → 对每一节提炼：
     - 节是否存在（exists: true/false）
     - 节的核心内容（结构化字段）
     - 原文是否超过 500 行（超过则仅缓存摘要）
  
Step 3.1.3：生成 .case_route_cache.json
  → 按 SKILL.md 第三部分 schema 写入缓存文件
  → 存放在案件文件夹根目录
  
Step 3.1.4：回写 .case_index.json（外科手术式）
  → 仅更新 cause_route 节点：
     status          → "ready"
     cause_zh        → 已确认的主案由
     secondary_causes→ []（单一案由为空数组）
     route_file      → route md 文件名
     routed_at       → 当前时间（ISO 8601）
     sections_available → 已解析节编号数组
     sections_pending   → 缺失节编号数组
     route_md_role   → role_index.route_md 对应路径
     stale_reason    → null（清除旧 stale 原因）
  
Step 3.1.5：回写 .case_progress.json
  → 读取案件根目录 .case_progress.json
  → 仅更新 cause_routed 节点：
     done              → true
     done_at           → 当前时间（ISO 8601）
     run_count         → run_count + 1
     cause_zh          → 已确认的主案由
     secondary_causes  → 次要案由数组
  
  → 同步更新顶层字段：
     last_updated_at   → 当前时间
     current_stage     → "Part1-收案"
  
Step 3.1.6：输出结果
  → "✅ 案由路由完成
     案由：[cause_zh]
     route 文件：[文件名]
     已解析节：§[X]§[X]...
     未找到节：§[X]（缺失，下游 skill 将降级）
     
     .case_route_cache.json 已写入案件文件夹根目录。
     后续 skill 将优先读取此缓存，无需重新路由。
     
     建议下一步：运行 extract-case-summary（1.2）"
```

### 3.2 用户选择选项3（"以上皆是（多案由）"）

```
Step 3.2.1：询问主案由
  → 弹出文本框："请选择主案由（将用于文件命名和文书抬头）："
  → 列出所有已识别案由供选择
  
Step 3.2.2：记录 primary + secondary
  → cause_zh = 主案由
  → secondary_causes = [次案由1, 次案由2, ...]
  
Step 3.2.3：读取所有 route md 文件
  → 对每个案由，读取对应的 route md 文件
  → 解析八节结构
  
Step 3.2.4：生成 .case_route_cache.json（合并多个案由）
  → cause_zh = 主案由
  → secondary_causes = [次案由列表]
  → sections 合并（如果多个案由都有§一，则合并为数组）
  
Step 3.2.5：回写 .case_index.json 和 .case_progress.json
  → 同3.1.4和3.1.5
```

### 3.3 用户选择选项4（"以上皆不是"）

**核心逻辑**：允许手动输入留空 → LLM降级，写入`.case_route_cache.json`

```
Step 3.3.1：询问是否手动补充
  → AskUserQuestion：
      question: "请输入案由（如'物业服务合同纠纷'），或留空跳过："
      header: "手动输入案由"
      options:
        - label: "输入案由"
          description: "手动输入案由名称"
        - label: "跳过案由路由"
          description: "LLM通用模式降级，后续质量7分"
  
  → 如果选择"输入案由"：
      → 弹出文本框："请输入案由名称："
      
      → 如果用户输入非空：
          → cause_zh = 用户输入
          → cause_zh_source = "manual"
          → 尝试匹配 case-cause-knowledge/（模糊匹配）
              → 匹配成功 → 读取 route md，生成正常版缓存
              → 匹配失败 → LLM通用模式生成降级版缓存
      
      → 如果用户留空（未输入）：
          → 进入 Step 3.3.2（LLM降级）
  
Step 3.3.2：LLM降级模式
  → 记录 layer_s_status = "skipped_manual"
  → LLM通用模式生成 .case_route_cache.json（降级版）
      {
        "metadata": {
          "schema_version": "1.0",
          "skill_name": "case-folder-organizer",
          "execution_count": 1,
          "resync_count": 0,
          "source_route_md": null,
          "source_route_md_mtime": null,
          "last_normal_run": "ISO 8601",
          "last_resync": null
        },
        "version": "1.0",
        "generated_at": "ISO 8601",
        "cause_zh": null,
        "cause_variants": [],
        "route_file": null,
        "route_file_path": null,
        "confidence": "low",
        "cause_source": "llm_fallback",
        "sections_available": [],
        "sections_pending": [],
        "sections": {},
        "route_full_text_available": false,
        "route_full_text_note": "LLM降级模式，未使用route md"
      }
  
  → 回写 .case_index.json：
      cause_route.status = "skipped"
      cause_route.cause_zh = null
      cause_route.stale_reason = "LLM降级模式"
  
  → 回写 .case_progress.json：
      cause_routed.done = true
      cause_routed.cause_zh = null
  
Step 3.3.3：输出警告
  → "⚠️ 降级模式：未启用案由知识库。
     后续所有skills（1.2, 1.3, 2.3, 2.8...）都将降级到LLM通用模式（质量7分）。
     建议：现在中断，从 case-cause-knowledge/ 复制对应文件到案件文件夹，然后重新执行1.1。"
```
