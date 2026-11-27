---
name: 1.1-case-folder-organizer
display_name: 案件文件夹整理
part: 1
index: 1.1
version: 3.1.0
tags: [case-management, file-organization, index, incremental]
description: >
  案件文件夹智能整理工具。核心功能：自动分析混乱的文件和文件夹，自动改名，
  自动按需建立二级、三级子目录，自动将文件归类到对应目录。
  用户只需将与案件有关的文件随时扔进一级目录，skill 负责识别、分类、整理。
  支持增量处理：通过快照对比，仅对新增或变更的文件执行分析，不重复处理已处理文件。
  触发词：整理案件文件夹 / 规范文件命名 / 帮我整理这个案件 / 用户提供案件文件夹路径。
  本 skill 是所有其他案件相关 skill 的执行前提，每次执行后生成 .case_index.json，
  供后续所有 skill 读取，作为案件文件夹的统一入口索引。
  运行模式：增量（仅处理新增/变更文件）。生成操作计划后暂停等待用户确认，确认后才执行写入操作。
  下游依赖（通过 .case_index.json 交付）：1.2~3.3（注：1.05 已合并到本 skill 的 §4.5）。
depends_on:
  hard:
    - 1.0-output-quality-rule     # 证据级输出标准 + Hooks（P0+P2）
  soft:
    - case-cause-knowledge      # 案由知识库，§4.5 案由预判时读取
outputs:
  - .case_snapshot.json         # 快照文件，增量判断 + skill_handoff
  - .case_index.json            # 案件文件索引，所有后续 skill 的强依赖
  - .case_progress.json         # 案件全生命周期推进状态面板
  - .case_route_cache.json      # 案由路由缓存（由 §4.5 生成）
downstream:
  - 1.2-extract-case-summary
  - 1.3-case-law-research
  - 1.4-legal-opinion
  - 1.5-party-due-diligence
  - 1.6-legal-service-proposal
  - 2.2-evidence-gap-analysis
  - 2.3-legal-theory-analysis
  - 2.1-case-timeline
  - 2.6-case-pleadings
  - 2.7-trial-simulation
  - 2.8-trial-outline
  - 2.9-closing-statement
  - 3.3-smart-case-archive
last_updated: 2026-05-14
---

## 🔧 配置化说明（重要）

**本 skill 已支持配置化架构**（2026-05-16更新）

### 配置文件位置

```
1.1-case-folder-organizer/
├── assets/                          # 配置文件目录
│   ├── allowed_directories_whitelist.json  # 允许的目录白名单
│   ├── confidence_levels.json            # 置信度等级定义
│   ├── directory_template.json          # 案件目录结构模板
│   ├── naming_rules_default.json        # 文件命名规则默认值
│   └── operation_types.json            # 操作类型分类定义
├── scripts/                         # Python脚本目录
│   ├── config_loader.py             # 配置加载器
│   ├── analyze.py                   # 智能分析脚本
│   ├── execute.py                   # 执行写入脚本
│   └── generate_index.py           # 生成索引脚本
└── reference/                      # 规则详解目录
    └── (路由规则等文档)
```

### 【强制】配置加载策略（LLM直接读取模式）

**本 skill 的 Python 脚本（analyze.py / execute.py / generate_index.py）为老脚本，不导入 config_loader。LLM 在执行时需直接读取 assets/ 下的JSON配置：**

> ⚠️ **脚本职责边界（重要）**：`analyze.py` 仅为骨架，只负责扫描文件、计算 MD5、快照增量对比、全角括号转半角、乱码文件名初筛（归入 `llm_needed`），**不包含任何归类/改名决策逻辑**。某文件应归入哪个目录、如何重命名，由 LLM 在对话中依据 `reference/` 下对应规则文件（见 §4.4 路由表）逐场景判断后写入操作计划。切勿误认为脚本已自动化完成归类。

```
LLM侧（SKILL.md内）:
    当分析文件时 → Read assets/ 下的配置文件获取规则
    当生成目录结构时 → Read directory_template.json 获取标准目录模板
    当验证命名时 → Read naming_rules_default.json 获取命名规则
    当判断置信度时 → Read confidence_levels.json 获取等级阈值
    当确定操作类型时 → Read operation_types.json 获取操作分类
    当验证目录合法性时 → Read allowed_directories_whitelist.json 获取白名单
```

```
Python侧（scripts/内）:
    from config_loader import load_config
    whitelist = load_config("allowed_directories_whitelist")
    confidence = load_config("confidence_levels")
    template = load_config("directory_template")
    naming = load_config("naming_rules_default")
    operations = load_config("operation_types")

LLM侧（SKILL.md内）:
    当分析文件时，读取 assets/ 下的配置文件获取规则
    当生成目录结构时，读取 directory_template.json 获取标准目录模板
    当验证命名时，读取 naming_rules_default.json 获取命名规则
```

### 配置文件自定义

律师可根据实践需要，**直接编辑 assets/ 下的JSON文件**，无需修改代码：

- **调整白名单目录**：编辑 `allowed_directories_whitelist.json`
- **修改置信度阈值**：编辑 `confidence_levels.json`
- **自定义目录模板**：编辑 `directory_template.json`
- **调整命名规则**：编辑 `naming_rules_default.json`
- **修改操作类型**：编辑 `operation_types.json`

---

# 案件文件夹整理 Skill

> **渐进式披露说明**：本 SKILL.md 只包含核心骨架与路由表。具体规则按需从 `reference/` 加载（路由表见 §4.4），Python 代码在 `scripts/`。全局设计原则由 Project Instructions 注入，本文件不复述。

---

## 第一部分：设计目标 <!-- section-type: whitelist, standard: 定位 -->

本 skill 的目标是让用户以"随时扔文件"的方式管理案件材料，无需手动整理。具体能力：

- **自动改名**：按命名规范识别并重命名文件
- **自动建目录**：按需建立二级、三级子目录（有文件才建，没有不建）
- **自动归类**：将识别后的文件移入对应目录
- **增量处理**：通过快照对比，只处理新增或变更的文件，避免重复消耗资源
- **最小化 LLM token**：绝大多数工作由本地 Python 完成，LLM 只介入无法用代码处理的部分
- **生成案件索引**：每次执行完成后输出 `.case_index.json`，作为后续所有 skill 的统一入口
- **案由预判**：首次运行时预判案由，生成 `.case_route_cache.json`，供后续所有 skill 读取（§4.5）

**整个流程分两阶段，中间必须暂停等待用户确认，未经确认绝不执行任何文件操作。**

---

## 第二部分：触发机制 <!-- section-type: whitelist, standard: 触发词 -->

用户在对话中提及案件文件夹路径时触发。skill 自行读取快照文件判断模式，**无需询问用户是首次还是增量**：

```
触发 → 检查 .case_snapshot.json + .case_index.json + 文件整理操作日志.txt 是否同时存在
    ├─ 三者均存在 → 增量模式（自动，不询问用户）
    │   ├─ snapshot.file_index 对比磁盘扫描
    │   │   ├─ 全部一致 → 静默退出（提示"文件结构无变化，无需整理"）
    │   │   ├─ 有新文件(diff中添加) → 仅分析新增文件
    │   │   │   └─ 对新增文件同样适用表格A/B/C反馈机制
    │   │   ├─ 有文件变更(md5变化) → 仅重分析变更文件
    │   │   │   └─ 同样适用表格A/B/C反馈机制
    │   │   └─ 有文件消失(diff中移除) → 检查是否为用户手动操作(§3.1.5)
    │   ├─ 操作计划仅含变更项（新增/移动/改名/元数据变化）
    │   └─ 标注：增量更新（第N次），本次新增X个文件，移动Y个，重分析Z个
    │
    └─ 任一缺失 → 全量模式（自动，不询问用户）
        ├─ 首次整理，全面扫描，执行完整流程
        └─ 标注：全量整理（首次）
```

> ⚠️ 禁止反问用户"检测到已整理过，是否增量更新？"——模式判断由 skill 根据文件存在性自动完成。

---

## 第三部分：隐藏文件管理（快照 + 索引） <!-- section-type: whitelist, standard: 依赖注入 -->

本 skill 在案件一级目录根目录维护四个隐藏文件，均以 `.` 开头，macOS Finder 默认不可见，防止用户误操作：

| 文件 | 用途 | 读写方 |
|------|------|--------|
| `.case_snapshot.json` | 增量判断、代理方向、skill_handoff 交接状态 | case-folder-organizer 读写；后续 skill 可读用于增量判断 |
| `.case_index.json` | 当前文件结构对外暴露，供所有后续 skill 读取 | case-folder-organizer 写（含 cause_route 节点）；所有其他 skill **只读** |
| `.case_progress.json` | 案件全生命周期推进状态面板 | case-folder-organizer 初始化；所有 skill 增量回写各自节点；**软依赖**，不存在时各 skill 降级运行 |
| `.case_route_cache.json` | 案由路由缓存，供所有后续 skill 读取 | case-folder-organizer §4.5 生成；所有其他 skill **只读** |

四个文件职责明确，互不替代。

### 3.1 `.case_snapshot.json` — 快照文件

**核心用途**：增量判断 + skill_handoff 交接。

**增量判断逻辑**（每次触发时 Python 脚本执行）：

| 情况 | 处理方式 |
|------|---------|
| 文件数量、文件名、元数据完全一致 | 静默退出，不调用任何 OCR 或 LLM |
| 有新增文件 | 仅对新增文件执行分析和命名 |
| 有文件元数据变化（mtime/size/md5） | 仅对变化文件重新分析 |
| 已处理文件无变化 | 跳过，不重复处理 |

#### 3.1.5 用户手动操作优先规则

> ⚠️ 律师可能在两次整理之间手动改名、移动文件。snapshot 对比时发现"旧路径文件消失 + 新路径文件出现（且 md5 与某个旧文件一致）"，**不得将其视为"需整理的新文件"**。

**检测逻辑**：

| 情况 | snapshot 检测 | 处理 |
|------|------------|------|
| 文件 A 从路径 X 消失，同 md5 文件出现在路径 Y | 用户手动移动/改名 | ✅ 保留用户操作，更新 snapshot.file_index 记录新路径，**不生成 rename/move 操作** |
| 文件 A 从路径 X 消失，无同 md5 文件出现 | 文件被删除 | 从 snapshot.file_index 移除，标注 `[已删除]`，不报错 |
| 文件 B 是新文件（snapshot 无对应 md5 记录） | 用户新增 | 正常分析和整理 |
| 文件 C 仍在 snapshot 路径，md5 变化 | 文件内容更新 | 重新分析 |

**实现**（`scripts/execute.py` 的 `update_snapshot()` 内）：
```python
# 对比旧 snapshot.file_index 和新磁盘扫描
old_keys = set(snapshot["file_index"].keys())
new_scan = scan_disk(case_root)  # {path: {md5, size, mtime}}
new_keys = set(new_scan.keys())

# 1. 检测用户手动操作：旧md5出现在新路径 → 保留用户操作
removed = old_keys - new_keys
added = new_keys - old_keys
for old_path in list(removed):
    old_md5 = snapshot["file_index"][old_path]["md5"]
    for new_path in list(added):
        if new_scan[new_path]["md5"] == old_md5:
            # 用户手动改名/移动 → 标记为"用户操作，已保留"
            snapshot["file_index"][new_path] = new_scan[new_path]
            snapshot["file_index"][new_path]["user_managed"] = True
            snapshot["file_index"][new_path]["previous_path"] = old_path
            del snapshot["file_index"][old_path]
            removed.remove(old_path)
            added.remove(new_path)
            break

# 2. 真正删除的（无同md5匹配）→ 从index移除
for old_path in removed:
    del snapshot["file_index"][old_path]

# 3. 真正新增的（无旧md5匹配）→ 留给 LLM 分析
# added 中剩余的就是真正的新文件
```

**禁止**：
- ❌ 将用户手动改名/移动的文件重新改名或移回原位置
- ❌ 在操作计划中显示"建议移动 X → Y"当 X 和 Y 是同一文件时
- ❌ 覆盖用户的目录结构调整

**完整 JSON schema、字段说明、skill_handoff 交接字段** → 见 `reference/01-snapshot-schema.md`

### 3.2 `.case_index.json` — 案件文件索引（对外接口）

**设计定位**：case-folder-organizer 向所有后续 skill 暴露的统一入口。

**后续 skill 强依赖规则**（硬约束）：

```
IF  .case_index.json 不存在
THEN  中止执行
      提示用户："请先对该案件文件夹运行 case-folder-organizer，建立索引后再执行本 skill。"
      不做任何文件操作
```

索引不存在说明文件夹从未整理过，此时文件结构不可靠，后续 skill 的执行结果无法保证质量。

**更新时机**：所有文件操作完成、`.case_snapshot.json` 更新后，由 `scripts/execute.py` 末尾调用 `generate_case_index()` 写入，确保索引反映最新状态（详见 `scripts/generate_index.py`）。

**完整 JSON schema、role_index 角色表、cause_route 节点说明、status 状态机、exclude_hints、后续 skill 标准读取模式** → 见 `reference/02-index-schema.md`

### 3.3 `.case_progress.json` — 案件推进状态面板

**定位**：案件全生命周期 milestone 追踪。1.1 首次执行时创建，所有 skill 执行完成后增量回写各自节点。

**依赖级别**：**软依赖**。不存在时：Part 1 skill 自动创建；Part 2/3 skill 降级运行，输出警告，不中止主流程。

**回写原则**：
1. 只更新本 skill 对应的 milestone 节点，其余节点不触碰
2. 回写前先读取当前文件，合并后写回，防止覆盖其他 skill 的写入
3. 回写失败不中断主流程，记录警告日志

**初始化时机**：1.1 首次执行（`folder_organized.run_count == 0`）时创建，所有 milestone 节点初始化为 `done: false`，`run_count: 0`。

**完整 schema**（所有 skill 均包含以下 milestone 节点，初始 `done: false`，`run_count: 0`）：
```
{
  "metadata": {
    "schema_version": "1.0",
    "skill_name": "case-folder-organizer",
    "execution_count": 1,
    "resync_count": 0,
    "last_normal_run": "ISO 8601",
    "last_resync": null,
    "skill_version": "3.1.0"
  },
  "case_folder": "（案件根目录绝对路径）",
  "last_updated_at": "ISO 8601",
  "current_stage": "Part1-收案",
  "milestones": {
    "folder_organized":  { "done": false, "run_count": 0, "done_at": null },
    "cause_routed":      { "done": false, "run_count": 0, "done_at": null, "cause_zh": "", "secondary_causes": [] },
    "summary_extracted": { "done": false, "run_count": 0, "done_at": null },
    "law_researched":    { "done": false, "run_count": 0, "done_at": null },
    "opinion_generated": { "done": false, "run_count": 0, "done_at": null },
    "service_proposed":  { "done": false, "run_count": 0, "done_at": null },
    "legal_theory_done": { "done": false, "run_count": 0, "done_at": null },
    "case_closed":       { "done": false, "run_count": 0, "done_at": null, "close_type": "" }
  }
}
```
每个 skill 执行完成后增量回写对应节点，其余节点不触碰。

---

## 第四部分：目录结构规则 <!-- section-type: whitelist, standard: 反幻觉规则 -->

### 4.1 层级原则

- 用户操作的文件夹 = **一级目录**，不往上走
- 默认最多**三级目录**，无特殊需要不建立四级目录
- **按需建立二级目录**：有对应文件才建，没有对应文件不建空目录

### 4.2 完整目录结构（终版）

```
一级目录（根目录）：  编号 案由-委托人姓名
│  .case_snapshot.json          ← 隐藏，用户不可见
│  .case_index.json             ← 隐藏，用户不可见，供其他 skill 读取
│  .case_progress.json          ← 隐藏，用户不可见，案件推进状态面板
│  .case_route_cache.json       ← 隐藏，用户不可见，案由路由缓存
│  文件整理操作日志.txt
│  判决书(委托人 一审).pdf
│  判决书(委托人 二审).pdf
│
├── 0.委托发票                   ← 有委托材料才建
├── 1.起诉状和证据               ← 有起诉材料才建
├── 2.法院通知 一审              ← 有一审通知才建
├── 3.答辩和证据                 ← 有答辩材料才建
├── 4.反诉和证据                 ← 识别到反诉状才建
├── 5.上诉状和证据               ← 有二审代理才建
├── 6.法院通知 二审              ← 有二审通知才建
├── 7.答辩二审                   ← 有二审答辩才建
├── 8.再审申请和证据             ← 识别到再审申请书才建
├── 9.法院通知 再审              ← 有再审通知才建
├── A.财产保全                   ← 识别到保全类文件才建
├── B.执行                       ← 识别到执行类文件才建
│   ├── B1.申请执行/
│   ├── B2.执行过程/             ← 兜底目录，无法判断子阶段的归此处
│   ├── B3.执行异议/
│   ├── B4.执行终本/
│   └── B5.恢复执行/
├── C.参考案例和法规             ← 有参考材料才建
├── D.管辖                       ← 识别到管辖类文件才建
├── Z.原始证据                   ← 用户手工放入后才介入管理
└── Z.待归类                     ← 临时中转，清空后自动删除
```

> **劳动争议特殊结构**:若识别到劳动仲裁申请书/裁决书(文档驱动触发,仅限劳动仲裁,不含商事仲裁),启用 `directory_template.json` 的 `case_type_templates.labor_dispute` 子模板,目录为 `1.仲裁和证据`/`2.仲裁通知`/`3.仲裁答辩和证据`/`4.起诉和证据`/`5.法院通知 一审`/`6.一审答辩和证据`/`7.反诉和证据`/`8.上诉状和证据`/`9.法院通知 二审`(详见 §4.3、§4.4 及 `reference/1-dir-仲裁和证据.md`、`reference/2-dir-仲裁通知.md`)。

### 4.3 代理阶段起点判断

律师不一定从一审开始代理，可能直接代理二审或再审。Skill 首次运行时根据识别到的文件类型判断代理起点，按需建立对应文件夹，不建立空文件夹。

| 识别到的最早文件 | 代理起点 | 建立文件夹范围 |
|---------------|---------|-------------|
| 劳动仲裁申请书/裁决书（仅限劳动仲裁） | 劳动仲裁阶段 | 启用劳动子模板,从1号起按需建立(见 `case_type_templates.labor_dispute`) |
| 起诉状（docx/pdf） | 一审 | 1号起按需建立 |
| 无起诉状，有上诉状 | 二审 | 从5号起按需建立，1～4号不建立 |
| 无起诉状/上诉状，有再审申请书 | 再审 | 从8号起按需建立，1～7号不建立 |
| 无起诉状，有传票/反诉状/答辩状（无上诉状/再审申请书） | 已进入诉讼，代理被告 | 从对应应诉阶段起按需建立；**须经 `AskUserQuestion` 二次确认代理方向后再执行** |
| 无任何诉讼阶段文件 | 收案前阶段 | 见 `reference/03-pre-litigation.md` |

### 4.4 按需加载路由表 ⭐

**核心原则**：AI 根据当前案件实际涉及的目录和文件情况，只 view 相关的 reference，不预加载全部规则。

| 检测到的情况 | 需加载的 reference |
|-------------|-------------------|
| 无起诉状/上诉状/再审申请书/答辩状/反诉状/法院通知/管辖裁定/保全裁定，纯咨询阶段 | `reference/03-pre-litigation.md` |
| `0.委托发票` 归类判断 | `reference/04-dir-0-entrustment.md` |
| `1.起诉状和证据` 归类判断 | `reference/05-dir-1-complaint.md` |
| 首次检测代理方向，或阶段切换 | `reference/06-representation-detect.md` |
| 证据目录存在且最后证据号对应 PDF 存在 | `reference/07-evidence-merge.md` |
| 代理被告 + 一级目录出现合并大 PDF | `reference/08-pdf-split.md` |
| `3.答辩和证据` 归类判断 | `reference/09-dir-3-defense.md` |
| `4.反诉和证据` 归类判断（出现反诉状） | `reference/10-dir-4-counterclaim.md` |
| `5.上诉状和证据` 归类判断 | `reference/11-dir-5-appeal.md` |
| 二审通知/答辩相关 | `reference/12-dir-6-7-second.md` |
| 检测到劳动仲裁申请书/裁决书（劳动争议） | `reference/06-representation-detect.md`（仲裁阶段代理方向）+ 劳动子模板 `case_type_templates.labor_dispute` |
| `1.仲裁和证据` 归类判断 | `reference/1-dir-仲裁和证据.md` |
| `2.仲裁通知` 归类判断 | `reference/2-dir-仲裁通知.md` |
| `3.仲裁答辩和证据` / `6.一审答辩和证据` 归类判断 | `reference/09-dir-3-defense.md`（劳动语境复用） |
| `4.起诉和证据` 归类判断 | `reference/05-dir-1-complaint.md`（劳动语境复用） |
| `7.反诉和证据` 归类判断 | `reference/10-dir-4-counterclaim.md`（劳动语境复用） |
| `8.上诉状和证据` 归类判断 | `reference/11-dir-5-appeal.md`（劳动语境复用） |
| `5.法院通知 一审` / `9.法院通知 二审` | `reference/08-pdf-split.md` / `reference/12-dir-6-7-second.md`（劳动语境复用） |
| 无起诉状，仅有传票/反诉状/答辩状 | `reference/06-representation-detect.md`（智能判代理被告，须 `AskUserQuestion` 二次确认） |
| 再审相关 | `reference/13-dir-8-9-retrial.md` |
| 保全类文件 | `reference/14-dir-A-preservation.md` |
| 执行类文件 | `reference/15-dir-B-execution.md` |
| 参考案例/法规类文件 | `reference/16-dir-C-reference.md` |
| 管辖异议相关 | `reference/17-dir-D-jurisdiction.md` |
| Z.原始证据 / Z.待归类 操作 | `reference/18-dir-Z-raw-pending.md` |
| 判决书/裁定书识别归类 | `reference/19-judgment-detection.md` |
| 法院文书无法按上述规则归类（兜底） | `reference/20-court-document-fallback.md` |

**加载策略**：当且仅当 Python 扫描或 LLM 识别确认当前案件涉及该场景时才 view；不触发就不加载。一次典型会话预计加载 3–5 个 reference，而非 20 个全读。

---

## §4.5 案由预判交互（Step 0.5） <!-- section-type: whitelist, standard: 核心流程 -->

### 触发条件

- **执行**：首次运行，且 `.case_index.json` 中 `cause_route` 节点不存在，或 `status` 为 `not_initialized`
- **静默跳过**：`cause_route.status` 已为 `pending_route` / `ready` / `stale`（案由已确认，无需重复）

### 执行逻辑（简洁版）

**详细逻辑 → 见 `reference/route-logic-index.md`**

```
Step 0.5.1：扫描材料（仅文件名，不读内容）
  → 起诉状 docx/pdf、委托协议、案情摘要.json、根目录文件名
  → 提取关键词，匹配 case-cause-knowledge/ 中的文件名

Step 0.5.2：生成 AskUserQuestion（固定4个选项）
  → 选项1：[预判案由1]（高置信度）
  → 选项2：[预判案由2]（次高置信度，或无则隐藏）
  → 选项3："以上皆是（多案由）"
  → 选项4："以上皆不是"

Step 0.5.3：根据用户选择执行（详细逻辑见 reference/route-logic-index.md §第三部分）
  → 选项1/2：读取对应 route.md，解析八节，生成 .case_route_cache.json（正常版）
  → 选项3：询问主案由，记录 primary + secondary，生成缓存
  → 选项4：询问是否手动补充
      → 手动输入 → 生成缓存（尝试匹配 route.md，失败则 LLM 降级）
      → 留空 → LLM 降级模式，生成降级版 .case_route_cache.json
```

### 案由变更机制

**主动变更**：律师在对话中说"变更案由为XXX"

**被动变更**：1.1 增量执行时，LLM 检测新文件包含的案由信息与现有 `cause_zh` 不一致

**触发后动作**（详细逻辑见 `reference/route-logic-index.md §第一部分`）：
1. 更新 `.case_index.json` `cause_route`（`cause_zh` 更新，`status` 重置为 `pending_route`）
2. 更新 `.case_progress.json`
3. 如 `.case_route_cache.json` 已存在，`status` 标 `stale`，提示律师重新执行案由路由逻辑

### stale 检测（增量执行时）

```
IF cause_route.status == "ready"
 AND 根目录 route md 文件的 mtime > cause_route.routed_at
 THEN status → "stale"，stale_reason → "route md 文件已更新"
      提示律师：缓存可能过期，建议重新执行案由路由逻辑
```

---

## 第五部分：文件识别与命名规则 <!-- section-type: whitelist, standard: 反幻觉规则 -->

### 5.1 Token 使用分层策略

核心原则：绝大多数工作由 Python 完成，LLM 只介入无法代码化的语义判断、视觉识别和用户交互呈现。完整的工作分层表 → 见 `reference/21-token-strategy.md`。

### 5.2 命名规范文件读取

在案件文件夹根目录寻找命名含"规范"或"命名"字样的 .docx 文件：

```bash
pandoc "命名规范文件.docx" -o /tmp/naming_rules.md
```

找不到规范文件时，使用 `reference/23-naming-defaults.md` 中的默认规范。

### 5.3 运行 analyze.py

```bash
python scripts/analyze.py "<案件文件夹完整路径>" --snapshot ".case_snapshot.json" --incremental
```

脚本输出三类结果，保存至 `/tmp/case_analysis_result.json`：

- `auto_ops`：Python 已确定的操作列表
- `llm_needed`：需要 LLM 视觉识别的文件（乱码文件名身份证扫描件等）
- `warnings`：需要人工判断的情况

完整 Python 实现 → `scripts/analyze.py`。

### 5.4 LLM 视觉识别（仅处理 llm_needed）

读取 `llm_needed` 列表，每个文件：
1. 调用 Read 工具读取预览图
2. 识别"姓名"字段
3. 追加至 `auto_ops`：`{"type": "rename", "src": "...", "dst": "身份证 姓名.ext"}`

`llm_needed` 为空时跳过本步骤。

---

## 第六部分：操作计划生成与用户确认 <!-- section-type: unknown -->

### 6.1 操作计划表格

**置信度分档规则**

| 档位 | 判断标准 | 处理方式 |
|------|---------|---------|
| 高置信度 | 文件类型明确、归属目录唯一 | 直接列入表格 A，自动执行 |
| 中置信度 | 能识别类型但归属目录不确定 | 暂存 `Z.待归类/`，列入表格 B，附判断理由和建议选项 |
| 无法识别 | 乱码文件名、格式异常、内容无法判断 | 暂存 `Z.待归类/`，列入表格 B，标注"无法识别，请人工处理" |

**表格 A：高置信度自动操作（auto_ops）**

按目标文件夹分组：

| 当前文件名 | 建议文件名/操作 | 操作类型 | 识别依据 |
|-----------|---------------|---------|---------|

操作类型：`重命名` / `移动` / `新建目录` / `删除（重复）`

**表格 B：需人工决定的情况（warnings）**

| 文件 | 置信度 | 问题描述 | skill 建议 | 选项 |
|------|-------|---------|-----------|------|

同时提示：自动处理 N 项，暂存待归类 M 项（中置信度 X 项 / 无法识别 Y 项），当前 `Z.待归类/` 文件总数：K。

### 6.2 确认机制

- **确认机制**：在对话中等待用户明确确认（输入"确认"/"执行"等）

**未收到确认前，绝不执行任何写入、改名、删除、移动操作。**

---

## 第七部分：执行操作 <!-- section-type: whitelist, standard: 核心流程 -->

用户确认后，将最终操作列表写入 `/tmp/case_plan.json`，运行：

```bash
python scripts/execute.py /tmp/case_plan.json "<案件文件夹完整路径>"
```

**执行顺序**（固定，不可调换）：
1. 新建目录（先建目录，再移文件）
2. 文件重命名、移动、删除
3. 文件夹重命名（最后执行，避免路径失效）
4. 更新 `.case_snapshot.json`
5. 生成/更新 `.case_index.json`（**收尾最后一步，确保索引反映最终状态**）
6. 生成 `.case_route_cache.json`（如 §4.5 已执行）
7. 初始化/更新 `.case_progress.json`（首次执行时创建并初始化全部 milestone 节点；后续执行时回写 `folder_organized` 节点：`done → true`，`run_count++`，`done_at` 更新为当前时间）

每项操作均捕获异常，失败时记录错误继续执行，不中断整体流程。

完整 Python 实现（do_mkdir / do_rename / do_move / do_delete / do_rename_folder / finalize） → `scripts/execute.py`；索引生成函数 → `scripts/generate_index.py`。

---

## 第八部分：日志规范 <!-- section-type: unknown -->

操作日志保存为 `文件整理操作日志.txt`，存放于案件文件夹根目录。完整日志模板和字段规范 → 见 `reference/22-logging-spec.md`。

---

## 第九部分：关键约束 <!-- section-type: unknown -->

1. **全角→半角**：所有文件名中 `（）` 改为 `()`，`－` 可保留
2. **Z.原始证据 铁律(不可改 + 必须 OCR + 1.1 职责边界)**:内文件一律**禁止改动、改名、编辑、删除**,原样保留;但**必须对其内容执行只读 OCR 提取,不得跳过**;1.1 的 OCR=案件材料内容提取(全新+增量),产物供所有下游 skill 读取;与 2.4 的 OCR(上游完成后转 PDF/合并 PDF)职责不同、不冲突;OCR 机制:**零 token 优先**(原生 PDF/Word 直抽,仅图像/扫描件调 Tesseract;LLM 先探测工具可用性,缺失降级)+ **隐藏持久化**(生成 leading-dot 前缀 .ocr.txt 伴生,如 `.转账记录.jpg.ocr.txt`)+ **注册 .case_index.json 的 `ocr` 字段**作为下游唯一读取契约;移入时 `shutil.move` + `os.utime` 还原时间戳
3. **Z.待归类 临时中转**：有无法归类文件时建立，清空后自动删除，不常驻
4. **docx + pdf 同名配对不算重复**，均保留
5. **未经用户确认绝不执行任何写入/改名/删除/移动操作**
6. **执行顺序**：新建目录 → 文件操作 → 文件夹重命名 → 更新快照 → 生成/更新索引 → 生成路由缓存（顺序固定，不可调换）
7. **按需建目录**：没有对应文件就不建对应二级目录
8. **`.case_snapshot.json`、`.case_index.json`、`case_route_cache.json` 均以 `.` 开头隐藏**，防止用户误操作
9. **每次操作生成日志**，包括索引更新记录，注明触发方式，注明当前 `Z.待归类/` 文件数
10. **`.case_index.json` 是所有后续 skill 的强依赖**：其他 skill 执行前必须检查此文件是否存在，不存在则中止并提示用户先运行本 skill
11. **严禁创建非标准目录**：skill 只能创建 SKILL.md 明确定义的目录（0–9号、A–D、Z.原始证据、Z.待归类、B1–B5）。遇到无法归入任何标准目录的文件，统一进 `Z.待归类/`，不得自行命名新目录。即使文件语义上属于"内部工作文件"、"内部资料"等类别，也必须进 `Z.待归类/`，由律师手动处理。
12. **文件位置联动（服务方案和报价）**：触发条件（满足任一）：（a）`0.委托发票/` 目录首次创建；（b）`0.委托发票/` 内新增文件名含"委托"/"服务合同"/"Legal Service Agreement"的文件。触发动作：检查案件根目录下是否存在 `服务方案和报价_*.docx` 或 `服务方案和报价_*.pdf`，若存在则移入 `0.委托发票/`，写入操作日志。
13. **route_md 文件严格保护**：根目录中识别到的案由 md 文件（注册为 `role_index.route_md`）不移动、不改名、不归入 `Z.待归类`。律师手动放入后本 skill 仅注册角色，不做任何文件操作。
14. **metadata 字段强制**：所有输出 JSON 文件（`.case_snapshot.json` / `.case_index.json` / `.case_progress.json` / `.case_route_cache.json`）必须包含 `metadata` 字段，用于版本跟踪和下游依赖判断。
15. **`.case_route_cache.json` 生成规则**：由 §4.5 生成，存放于案件根目录。后续所有 skill 优先读取此缓存，避免重复路由。

---

## 第十部分：缓存同步机制（--resync 模式） <!-- section-type: blacklist, standard: 缓存重复保护 -->

### 10.1 触发场景

`--resync` 模式在以下场景自动或手动触发：

1. 下游 skill 执行前检测到 JSON 文件已被用户修改（mtime 变化）
2. 用户手动执行 `/case-folder-organizer --resync`

### 10.2 resync 模式行为约束

| 行为 | 正常模式 | resync 模式 |
|------|----------|------------|
| 重新组织文件夹 | ✅ | ❌ 禁止 |
| 重新生成 JSON 结构 | ✅ | ❌ 禁止 |
| 读取已有 JSON | ❌ | ✅ |
| 验证 JSON 与文件系统一致性 | ❌ | ✅ |
| 更新 `.case_snapshot.json`（metadata 部分） | ✅ | ✅ |
| 更新 `.case_index.json`（metadata 部分） | ✅ | ✅ |
| 更新 `.case_progress.json`（metadata 部分） | ✅ | ✅ |
| 更新 `.case_route_cache.json`（metadata 部分） | ✅ | ✅ |
| 更新 metadata.execution_count | ✅ | ❌ 不变 |
| 更新 metadata.resync_count | ❌ | ✅ +1 |
| 更新 metadata.last_resync | ❌ | ✅ |

**注意：resync 模式更新范围**
- resync 仅更新标记为 `"cache_stale"` 的 JSON 文件
- 标记为 `"cache_valid"` 的文件跳过更新，避免不必要的写入
- 四个 JSON 文件（.case_snapshot / .case_index / .case_progress / .case_route_cache）独立判断 cache 状态
- 此设计确保只更新过期的文件，提升效率

### 10.3 resync 执行流程

```
Step R-1：定位已有 JSON 文件
  → 在案件根目录查找 ".case_snapshot.json" / ".case_index.json" / ".case_progress.json" / ".case_route_cache.json"
  → 找不到任意一个 → 报错："未找到 JSON 文件，无法执行 resync"
  → 找到 → 继续

Step R-2：检查文件系统状态
  → 读取快照中的 file_index
  → 对比当前文件系统状态
  → 一致 → 标注 "cache_valid"，无需更新
  → 不一致 → 标注 "cache_stale"，执行 Step R-3

Step R-3：更新 metadata（仅当 cache_stale 时）
  → 读取已有 JSON 文件
  → 保留所有数据字段不变
  → 仅更新各 JSON 的 metadata：
      resync_count + 1
      last_resync = current_timestamp
      last_normal_run = 当前时间戳
  → 写入文件（覆盖更新）

Step R-4：输出结果
  → cache_valid："✅ 缓存已是最新，无需更新。"
  → cache_stale："✅ 缓存 metadata 已同步（第 {N} 次 resync）。\n⚠️ 注意：文件系统已变更，建议重新执行 /case-folder-organizer（正常模式）以更新缓存数据。"
```

### 10.4 一致性验证失败处理

resync 模式仅验证 metadata，不重新组织文件夹。若文件系统已变更但用户未重新运行本 skill，下游 skill 将读到过时数据。

验证失败时：
```
警告信息：
  "⚠️ 文件系统已变更（文件数量或 mtime 不一致）。
   缓存数据为旧版本，可能不准确。
   建议处理方式：
   1) 手动重新执行 /case-folder-organizer（正常模式，会重新组织文件夹并生成 JSON）
   2) 忽略，强制使用现有缓存（风险：数据可能不一致）"
```

### 10.5 下游 skill 缓存检查逻辑（供下游 skill 实现参考）

下游 skill（如 extract-case-summary、legal-theory-analysis）执行前须执行以下检查：

```
Check 1：.case_index.json 是否存在？
  NO → 标注 `index_status = "missing"`，中止执行，提示用户先运行 case-folder-organizer
  YES → 继续

Check 2：.case_route_cache.json 是否存在？
  NO → 标注 `route_status = "missing"`，降级执行（LLM 通用模式）
  YES → 继续

Check 3：检查 .case_route_cache.json 的 metadata，判断是否为降级版
  cause_source == "llm_fallback" OR cause_zh == null
  → 标注 `route_status = "fallback"`，降级执行（质量7分）
  → 否则标注 `route_status = "normal"`，正常执行（质量8.5分）

Check 4：缓存中 metadata.last_normal_run 是否存在？
  NO → 标注 `index_status = "no_metadata"`，按缺失层级处理
  YES → 继续

Check 5：检查 .case_index.json 的 mtime，与 metadata.last_normal_run 比对
  mtime 一致 → 缓存有效，直接使用，标注 `index_status = "valid"`
  mtime 不一致 → 缓存过期，尝试静默 resync
    成功 → 标注 `index_status = "stale_resynced"`，继续使用缓存（但提示数据可能过时）
    失败 → 标注 `index_status = "stale_resync_failed"`，报错，提示用户选择：
      1) 手动重新执行 /case-folder-organizer（正常模式）
      2) 忽略，强制使用现有缓存（风险：数据可能不一致）
      3) 取消执行
```

### 10.6 实现备注

- resync 模式不重新组织文件夹，仅更新 metadata 中的时间戳和计数
- 若文件系统已变更，必须提醒用户重新执行正常模式
- 正常模式执行时，metadata.execution_count +1，metadata.resync_count 不变
- 下游 skill 检测到缓存过期时，应优先提示用户重新执行正常模式，而非依赖 resync
- 本 skill 的 resync 模式实际使用场景较少，因为律师通常不会手动编辑这些 JSON 文件

---

## 附录：默认命名规范 <!-- section-type: blacklist, standard: 附录 -->

当案件文件夹内无命名规范文件时使用的完整默认规范 → 见 `reference/23-naming-defaults.md`。
