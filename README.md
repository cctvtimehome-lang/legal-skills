# legal-skills — 案件文件夹智能整理 AI 技能

面向民商事诉讼承办律师的 AI 技能仓库，当前公开包含核心入口技能 **`1.1-case-folder-organizer`（案件文件夹整理）**。

- 仓库技能数：**1**
- 当前版本：**v3.1.0**
- 更新日期：2026-11-27
- 本仓库仅含**技能定义、参考规则与辅助脚本**，不含任何真实案件材料或当事人信息。

---

## 一、技能清单

| skill_id | 技能名称 | 目录 | version | 说明 |
|---|---|---|---|---|
| 1.1 | 案件文件夹整理 | `skills/1.1-case-folder-organizer` | 3.1.0 | 自动分析、规范命名、按需建目录并归类案件材料，支持增量快照对比与 `.case_index.json` 索引生成 |

---

## 二、安全与合规说明

1. 技能产出的运行时缓存（`*_cache.json`、`.case_index.json`、`.case_snapshot.json` 等）已在 `.gitignore` 中排除，避免误将案件数据提交入库。
2. 仓库内无任何明文凭证或真实案件信息；请勿将真实 Token / API Key 或当事人隐私材料提交至本仓库。

---

## 三、目录结构

```text
skills/
└── 1.1-case-folder-organizer/
    ├── SKILL.md        # 技能主定义与路由骨架
    ├── assets/         # 目录模板、命名规则、白名单等配置文件
    ├── reference/      # 详细分类规则与子目录规范
    └── scripts/        # 本地 Python 分析、执行与索引生成脚本
```
