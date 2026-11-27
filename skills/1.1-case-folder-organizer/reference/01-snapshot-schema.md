# .case_snapshot.json 完整 Schema 与字段说明

> **用途**：case-folder-organizer 内部运行文件,用于增量判断和 skill_handoff 交接。 读取此文件进行触发判断,其他 skill 不读取此文件。

---

## 完整结构示例

```json
{
  "metadata": {
    "schema_version": "1.0",
    "skill_name": "case-folder-organizer",
    "execution_count": 1,
    "resync_count": 0,
    "last_normal_run": "2026-04-03T15:30:00+08:00",
    "last_resync": null
  },
  "last_run": "2026-04-03T15:30:00+08:00",

  "file_index": {
    "相对路径/文件名.pdf": {
      "size": 102400,
      "mtime": 1736900000,
      "md5": "a3f5e8c9b2d4f7a1e6c3b8a9d2e5f4c（完整32位MD5小写十六进制）"
    }
  },

  "first_instance": {
    "representation_side": "原告",
    "detected_at": "2026-01-15T10:30:00+08:00",
    "basis": "1.起诉状和证据/起诉状_张三.docx 存在"
  },
  "second_instance": {
    "representation_side": "未知",
    "detected_at": null,
    "basis": null
  },
  "third_instance": {
    "representation_side": null,
    "detected_at": null,
    "basis": null
  },

  "skill_handoff": {
    "representation_side_first": "原告",
    "representation_side_second": "未知",
    "representation_side_third": null,
    "counterclaim_side": null,
    "evidence_merged_first": true,
    "evidence_count_first": 10,
    "evidence_merged_defense": false,
    "evidence_count_defense": 0,
    "page_fill_status": "filled",
    "page_fill_skip_reason": null,
    "pending_issues": [
      "Z.待归类 中有 2 个文件未能归类,待人工处理"
    ]
  }
}
```

---

## 字段分类

快照分两类字段:**运行状态**(供增量判断)和 **skill_handoff**(供跨 skill 读取)。

### 运行状态字段

| 字段 | 说明 |
|------|------|
| `last_run` | 上次执行时间戳,ISO 8601 格式 |
| `file_index` | 文件清单字典,key 为相对路径,value 为 {size, mtime, md5} |
| `first_instance` / `second_instance` / `third_instance` | 各审级代理方向判断结果 + 判断依据,首次触发后长期保存 |

### `skill_handoff` 字段说明

| 字段 | 说明 |
|------|------|
| `representation_side_first/second/third` | 一审/二审/再审代理方向,供其他 skill 读取 |
| `counterclaim_side` | 反诉方向:`"我方提起"` / `"被告提起"` / `null` |
| `evidence_merged_first` | 起诉证据是否已合并 |
| `evidence_count_first` | 起诉证据已合并数量 |
| `evidence_merged_defense` | 答辩证据是否已合并 |
| `evidence_count_defense` | 答辩证据已合并数量 |
| `page_fill_status` | 页码回填状态:`filled` / `skipped` / `pending` |
| `page_fill_skip_reason` | 跳过原因,供后续专项 skill 接手处理 |
| `pending_issues` | 本 skill 处理后遗留的未解决问题列表,后续 skill 从此接手 |

---

## 增量判断逻辑

每次触发时,Python 脚本对比当前文件系统与快照:

| 情况 | 处理方式 |
|------|---------|
| 文件数量、文件名、元数据完全一致 | 静默退出,不调用任何 OCR 或 LLM |
| 有新增文件 | 仅对新增文件执行分析和命名 |
| 有文件元数据变化(mtime/size/md5) | 仅对变化文件重新分析 |
| 已处理文件无变化 | 跳过,不重复处理 |

---

## 与 `.case_index.json` 的职责区别

| 维度 | `.case_snapshot.json` | `.case_index.json` |
|------|----------------------|-------------------|
| 读写方 | case-folder-organizer 读写; 读 | case-folder-organizer 写;**所有其他 skill 只读** |
| 用途 | 内部运行文件(增量 + 交接) | 对外接口(结构化目录树 + 角色索引) |
| 是否包含 md5 | ✅ | ❌ |
| 是否包含 role_index | ❌ | ✅ |
