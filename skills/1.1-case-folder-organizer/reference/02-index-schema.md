# .case_index.json 完整 Schema 与字段说明

> **用途**:case-folder-organizer 向所有后续 skill 暴露的统一入口。**所有其他 skill 只读此文件**,不读取 `.case_snapshot.json`。

---

## 完整结构示例

```json
{
  "metadata": {
    "schema_version": "1.0",
    "skill_name": "case-folder-organizer",
    "skill_version": "3.1.0",
    "execution_count": 1,
    "resync_count": 0,
    "last_normal_run": "2026-04-03T15:30:00+08:00",
    "last_resync": null,
    "generated_at": "2026-04-03T15:30:00+08:00"
  },
  "case_name": "001 买卖合同纠纷-张三",

  "representing_side": "原告",
  "_representing_side_note": "取值：原告/被告/申请人/被申请人/上诉人/被上诉人。从 representation 对象推导，代理方向未确定时为 null。",

  "representation": {
    "first_instance": "原告",
    "second_instance": null,
    "third_instance": null,
    "counterclaim_side": null
  },

  "cause_route": {
    "status": "pending_route",
    "cause_zh": "物业服务合同纠纷",
    "cause_zh_source": "LLM预判+律师确认",
    "secondary_causes": [],
    "route_file": null,
    "routed_at": null,
    "cache_file": ".case_route_cache.json",
    "sections_available": [],
    "sections_pending": [],
    "route_md_role": null,
    "stale_reason": null
  },

  "directory_tree": {
    "root": {
      "path": ".",
      "files": [
        { "name": "判决书(张三 一审).pdf", "ext": "pdf", "role": "judgment_first" },
        { "name": "文件整理操作日志.txt", "ext": "txt", "role": "log" }
      ]
    },
    "0.委托发票": {
      "path": "0.委托发票",
      "files": [
        { "name": "身份证 张三.jpg", "ext": "jpg", "role": "id_card" },
        { "name": "法律服务合同 张三.pdf", "ext": "pdf", "role": "engagement_contract" },
        { "name": "授权委托书 张三.pdf", "ext": "pdf", "role": "poa" },
        { "name": "所函 张三.pdf", "ext": "pdf", "role": "firm_letter" },
        { "name": "发票 20000元.pdf", "ext": "pdf", "role": "invoice" }
      ]
    },
    "1.起诉状和证据": {
      "path": "1.起诉状和证据",
      "files": [
        { "name": "起诉状_张三.docx", "ext": "docx", "role": "complaint_draft" },
        { "name": "起诉状_张三.pdf", "ext": "pdf", "role": "complaint_signed" },
        { "name": "证据目录_张三.docx", "ext": "docx", "role": "evidence_list_draft" },
        { "name": "证据目录_张三.pdf", "ext": "pdf", "role": "evidence_list_signed" },
        { "name": "证据1 买卖合同.pdf", "ext": "pdf", "role": "evidence", "seq": 1 },
        { "name": "证据2 转账记录.pdf", "ext": "pdf", "role": "evidence", "seq": 2 },
        { "name": "证据3 催款函.pdf", "ext": "pdf", "role": "evidence", "seq": 3 },
        { "name": "证据(合并).pdf", "ext": "pdf", "role": "evidence_merged" }
      ]
    },
    "2.法院通知 一审": {
      "path": "2.法院通知 一审",
      "files": [
        { "name": "受理通知.pdf", "ext": "pdf", "role": "acceptance_notice" },
        { "name": "传票20260315 0930.pdf", "ext": "pdf", "role": "summons" }
      ]
    },
    "3.答辩和证据": {
      "path": "3.答辩和证据",
      "files": [
        { "name": "答辩状_张三.docx", "ext": "docx", "role": "defense_draft" },
        { "name": "答辩状_张三.pdf", "ext": "pdf", "role": "defense_signed" }
      ]
    },
    "4.反诉和证据": null,
    "5.上诉状和证据": null,
    "6.法院通知 二审": null,
    "7.答辩二审": null,
    "8.再审申请和证据": null,
    "9.法院通知 再审": null,
    "A.财产保全": null,
    "B.执行": null,
    "C.参考案例和法规": null,
    "D.管辖": null,
    "Z.原始证据": {
      "path": "Z.原始证据",
      "files": [
        { "name": "微信转账记录.jpg", "ext": "jpg", "role": "raw_evidence", "ocr": ".微信转账记录.jpg.ocr.txt" }
      ]
    },
    "Z.待归类": null
  },

  "role_index": {
    "id_card": ["0.委托发票/身份证 张三.jpg"],
    "engagement_contract": ["0.委托发票/法律服务合同 张三.pdf"],
    "poa": ["0.委托发票/授权委托书 张三.pdf"],
    "firm_letter": ["0.委托发票/所函 张三.pdf"],
    "invoice": ["0.委托发票/发票 20000元.pdf"],
    "complaint_draft": ["1.起诉状和证据/起诉状_张三.docx"],
    "complaint_signed": ["1.起诉状和证据/起诉状_张三.pdf"],
    "evidence_list_draft": ["1.起诉状和证据/证据目录_张三.docx"],
    "evidence_list_signed": ["1.起诉状和证据/证据目录_张三.pdf"],
    "evidence_merged": ["1.起诉状和证据/证据(合并).pdf"],
    "defense_draft": ["3.答辩和证据/答辩状_张三.docx"],
    "defense_signed": ["3.答辩和证据/答辩状_张三.pdf"],
    "judgment_first": ["判决书(张三 一审).pdf"],
    "raw_evidence": ["Z.原始证据/微信转账记录.jpg"]
  },

  "exclude_hints": {
    "extract_case_summary": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "smart_archive_checker": ["Z.待归类"],
    "cn_litigation": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"]
  },

  "pending_issues": [
    "Z.待归类 中有 1 个文件未能归类,待人工处理"
  ],

  "stats": {
    "total_files": 13,
    "pending_files": 1,
    "evidence_count_first": 3,
    "evidence_merged_first": true,
    "evidence_count_defense": 0,
    "evidence_merged_defense": false
  }
}
```

---

## 字段说明

### `directory_tree`

完整目录/文件树。每个目录键值:
- 目录存在且有文件 → 对象,包含 `path` 和 `files` 数组
- 目录不存在或为空 → `null`(明确区分"未建立"与"已建立但空")

每个文件对象包含:`name`(含扩展名)、`ext`(格式)、`role`(语义角色标签)、`ocr`(可选,Z.原始证据 内文件的隐藏 OCR 伴生文件路径,如 `.微信转账记录.jpg.ocr.txt`,为下游 skill 读取该文件文本的唯一契约,不在文件夹中显式展示)。证据文件额外附 `seq`(序号)。

### `role_index` — 语义角色倒排索引

值为相对路径数组。供后续 skill 按角色直接定位文件,无需遍历 `directory_tree`。

| role 标签 | 对应文件 |
|-----------|---------|
| `id_card` | 身份证 |
| `engagement_contract` | 法律服务合同 |
| `poa` | 授权委托书 |
| `firm_letter` | 所函 |
| `invoice` | 发票 |
| `complaint_draft` | 起诉状 docx |
| `complaint_signed` | 起诉状 pdf |
| `evidence_list_draft` | 证据目录 docx |
| `evidence_list_signed` | 证据目录 pdf |
| `evidence` | 单份证据(附 `seq` 序号) |
| `evidence_merged` | 证据(合并).pdf |
| `counterclaim_draft` | 反诉状 docx |
| `counterclaim_signed` | 反诉状 pdf |
| `defense_draft` | 答辩状 docx |
| `defense_signed` | 答辩状 pdf |
| `appeal_draft` | 上诉状 docx |
| `appeal_signed` | 上诉状 pdf |
| `retrial_draft` | 再审申请书 docx |
| `retrial_signed` | 再审申请书 pdf |
| `judgment_first` | 一审判决书(根目录) |
| `judgment_second` | 二审判决书(根目录) |
| `judgment_retrial` | 再审判决书(根目录) |
| `summons` | 传票 |
| `acceptance_notice` | 受理通知 |
| `preservation_order` | 财产保全裁定书 |
| `route_md` | 案由路由 md 文件（律师手动放入根目录，1.1 §4.5 读取） |
| `raw_evidence` | Z.原始证据 内原始材料（如聊天截图、录音、合同原件等），其 `ocr` 字段指向隐藏 .ocr.txt 伴生文件 |

### `exclude_hints`

为已知后续 skill 预设的排除目录建议(建议性,非强制)。key 为 skill 名称(snake_case),value 为建议跳过的目录列表。后续 skill 读取对应 key,跳过这些目录,减少无效分析。

### `stats`

统计摘要,供快速判断案件完整度,无需遍历文件。

---

### `cause_route` — 案由路由轻量节点

case-folder-organizer（1.1）在 §4.5 完成后写入，§4.5 执行完成后外科手术式回写更新。

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 路由状态，见状态机 |
| `cause_zh` | string | 主案由（第三级），律师确认后写入 |
| `cause_zh_source` | string | 来源：`"LLM预判+律师确认"` / `"manual"` |
| `secondary_causes` | array | 次要案由列表，单案由时为空数组 |
| `route_file` | string\|null | route md 文件名，§4.5 执行后写入 |
| `routed_at` | string\|null | §4.5 执行时间（ISO 8601） |
| `cache_file` | string | 固定值 `".case_route_cache.json"` |
| `sections_available` | array | §4.5 解析到的有效节编号，如 `[0,1,2,3,4]` |
| `sections_pending` | array | 缺失节编号 |
| `route_md_role` | string\|null | 对应 role_index 中的 route_md 路径 |
| `stale_reason` | string\|null | stale 原因说明 |

#### status 状态机

| status | 含义 | 由谁写入 |
|--------|------|---------|
| `not_initialized` | 1.1 首次执行，Step 0.5 无可判断材料 | 1.1 初始化 |
| `pending_route` | Step 0.5 完成，cause_zh 已填，等待律师放入 route md 后触发路由逻辑 | 1.1 §4.5 后写入 |
| `ready` | §4.5 执行完成，.case_route_cache.json 已生成 | 1.1 §4.5 回写 |
| `stale` | route md 文件 mtime > routed_at，或 cause_zh 变更 | 1.1 增量执行时检测 |

**下游 skill 读取规范**（更新后的 Layer S 标准写法）：

```
Step S-0：读 .case_index.json → cause_route.status
  "ready"         → 读 .case_route_cache.json 对应字段，跳过后续路由
  "pending_route" → 提示律师先确认案由或放入 route md 文件
  "stale"         → 提示缓存可能过期，建议重新执行 1.1；用户选继续则按 ready 处理
  节点不存在      → 原有路由逻辑兜底（向后兼容旧版 index）
```

---

## 后续 skill 标准读取模式

```python
def load_case_index(case_root):
    index_path = os.path.join(case_root, ".case_index.json")
    if not os.path.exists(index_path):
        raise RuntimeError(
            "未找到 .case_index.json。\n"
            "请先对该案件文件夹运行 case-folder-organizer,建立索引后再执行本 skill。"
        )
    with open(index_path, encoding="utf-8") as f:
        return json.load(f)

# 示例:extract-case-summary skill
index = load_case_index(case_root)
exclude_dirs  = index["exclude_hints"].get("extract_case_summary", [])
complaint     = index["role_index"].get("complaint_draft")       # 直接定位起诉状 docx
evidence_list = index["role_index"].get("evidence_list_draft")   # 直接定位证据目录 docx
```

---

## 索引生成位置

`generate_case_index()` 在 `scripts/execute.py` 所有文件操作完成、`.case_snapshot.json` 更新后最后调用,确保索引反映最新状态。完整实现见 `scripts/generate_index.py`。
