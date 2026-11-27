# 案由路由逻辑 - 缓存生成Schema

> 本文档是 `route-logic-user-choice.md` 的拆分版本（第四部分）。
> 完整逻辑由以下文件组成：
> - `route-logic-user-choice-index.md` - 索引
> - `route-logic-user-choice-processing.md` - 第三部分（用户选择处理）
> - `route-logic-user-choice-schema.md` - 本文档（第四部分）
> 
> **适用场景**：LLM生成 `.case_route_cache.json` 时作为格式参考。

---

## 第四部分：缓存生成 Schema

### 4.1 正常版 .case_route_cache.json（用户选择选项1/2/3）

```json
{
  "metadata": {
    "schema_version": "1.0",
    "skill_name": "case-folder-organizer",
    "execution_count": 1,
    "resync_count": 0,
    "source_route_md": "property-management.md",
    "source_route_md_mtime": "2026-05-12T19:00:00+08:00",
    "last_normal_run": "2026-05-12T19:00:00+08:00",
    "last_resync": null
  },
  "version": "1.0",
  "generated_at": "2026-05-12T19:00:00",
  "cause_zh": "物业服务合同纠纷",
  "cause_variants": ["物业纠纷", "物业费纠纷"],
  "route_file": "property-management.md",
  "route_file_path": "（案件文件夹根目录，相对路径）",
  "confidence": "high",
  "cause_source": "filename_keywords",
  "sections_available": [0, 1, 2, 3, 4, 5, 6, 8],
  "sections_pending": [7],
  "sections": {
    "s0_extract_summary": {
      "exists": true,
      "core_facts_checklist": ["签约日期", "物业费标准", "欠费起止时间", "催告记录"],
      "key_timeline_nodes": ["合同签订", "首次欠费", "催告发函", "诉讼时效截止"],
      "narrative_focus": "物业费欠缴事实链 + 催告有效性"
    },
    "s1_legal_relationship": {
      "exists": true,
      "relationship_type": "物业服务合同关系",
      "applicable_law": ["民法典第939条", "民法典第944条"],
      "validity_issues": "合同效力通常无争议，重点在履行状态",
      "summary": "（§一核心内容摘要，300字以内）"
    },
    "s2_plaintiff_claims": {
      "exists": true,
      "claims": [
        {
          "claim": "要求被告支付物业费",
          "legal_basis": "民法典第944条",
          "elements": ["合同有效", "原告已履行服务义务", "被告欠费事实", "金额确定"],
          "defendant_defense_prediction": ["服务质量抗辩", "催告程序瑕疵"],
          "our_rebuttal": "（预设反驳要点）"
        }
      ]
    },
    "s3_defendant_defenses": {
      "exists": true,
      "defense_strategies": [
        {
          "defense": "服务质量抗辩",
          "applicable_condition": "原告服务存在瑕疵",
          "legal_basis": "民法典第563条",
          "evidence_needed": ["业主投诉记录", "维修未响应证明"],
          "risk_level": "中"
        }
      ]
    },
    "s4_legal_provisions": {
      "exists": true,
      "provisions": [
        {
          "law": "民法典",
          "article": "第944条",
          "content_summary": "业主应按约定支付物业费，物业服务人已提供服务的，业主不得以未享受或无需接受相关物业服务为由拒绝支付物业费",
          "usage": "主请求权基础"
        }
      ]
    },
    "s5_fact_narrative_template": {
      "exists": true,
      "template_summary": "（§五事实叙述模板摘要，供 case-pleadings 参考）"
    },
    "s6_evidence_checklist": {
      "exists": true,
      "evidence_groups": [
        {
          "group_name": "合同文件组",
          "items": ["物业服务合同", "业主公约"],
          "proving_purpose": "证明合同关系成立及双方权利义务"
        }
      ]
    },
    "s7_trial_examination": {
      "exists": false,
      "note": "§七待律师积累庭审笔录后手动补充"
    },
    "s8_judicial_patterns": {
      "exists": true,
      "common_rulings": [
        "服务质量抗辩举证责任在被告，业主需证明具体瑕疵及损失",
        "催告程序不影响物业费请求权，但影响诉讼时效计算"
      ],
      "risk_warnings": [
        "诉讼时效：物业费诉讼时效3年，从每期到期日分别起算",
        "反诉风险：被告可能提起服务质量反诉，需提前准备"
      ]
    }
  },
  "route_full_text_available": true,
  "route_full_text_note": "下游 skill 如需完整原文，直接 view 案件根目录的 route 文件"
}
```

### 4.2 降级版 .case_route_cache.json（用户选择选项4且留空）

```json
{
  "metadata": {
    "schema_version": "1.0",
    "skill_name": "case-folder-organizer",
    "execution_count": 1,
    "resync_count": 0,
    "source_route_md": null,
    "source_route_md_mtime": null,
    "last_normal_run": "2026-05-12T19:00:00+08:00",
    "last_resync": null
  },
  "version": "1.0",
  "generated_at": "2026-05-12T19:00:00+08:00",
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
```
