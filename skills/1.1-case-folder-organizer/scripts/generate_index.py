"""
case-folder-organizer / generate_index.py

生成 .case_index.json,作为所有后续 skill 的统一入口。

在 execute.py 所有文件操作完成、.case_snapshot.json 更新后最后调用,
确保索引反映最新状态。
"""

import os
import json
import sys
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))

# 导入配置加载器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config

# 从配置加载标准目录（降级到硬编码）
directory_config = load_config("directory_template")
if directory_config and "standard_dirs" in directory_config:
    STANDARD_DIRS = [d["name"] for d in directory_config["standard_dirs"] if isinstance(d, dict) and "name" in d]
else:
    STANDARD_DIRS = [
        "0.委托发票",
        "1.起诉状和证据",
        "2.法院通知 一审",
        "3.答辩和证据",
        "4.反诉和证据",
        "5.上诉状和证据",
        "6.法院通知 二审",
        "7.答辩二审",
        "8.再审申请和证据",
        "9.法院通知 再审",
        "A.财产保全",
        "B.执行",
        "C.参考案例和法规",
        "D.管辖",
        "Z.原始证据",
        "Z.待归类",
    ]

# 从配置加载版本信息（降级到硬编码）
meta_config = load_config("directory_template")
if meta_config and "meta" in meta_config:
    SKILL_VERSION = meta_config["meta"].get("version", "20260423")
    SCHEMA_VERSION = meta_config["meta"].get("schema_version", "1.0")
    SKILL_NAME = meta_config["meta"].get("skill_name", "case-folder-organizer")
else:
    SKILL_VERSION = "20260423"
    SCHEMA_VERSION = "1.0"
    SKILL_NAME = "case-folder-organizer"


# 默认的排除提示,为已知后续 skill 预设
DEFAULT_EXCLUDE_HINTS = {
    "extract_case_summary": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "smart_archive_checker": ["Z.待归类"],
    "cn_litigation": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "case_law_research": ["0.委托发票", "Z.原始证据", "Z.待归类"],
    "legal_opinion": ["0.委托发票", "Z.待归类"],
    "party_due_diligence": ["C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "evidence_organizer": ["0.委托发票", "C.参考案例和法规", "Z.待归类"],
    "evidence_list": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "case_pleadings": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "case_timeline": ["0.委托发票", "C.参考案例和法规", "Z.待归类"],
    "trial_outline": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
    "closing_statement": ["0.委托发票", "C.参考案例和法规", "Z.原始证据", "Z.待归类"],
}


# 标准二级目录列表(按需建立的完整集合)
STANDARD_DIRS = [
    "0.委托发票",
    "1.起诉状和证据",
    "2.法院通知 一审",
    "3.答辩和证据",
    "4.反诉和证据",
    "5.上诉状和证据",
    "6.法院通知 二审",
    "7.答辩二审",
    "8.再审申请和证据",
    "9.法院通知 再审",
    "A.财产保全",
    "B.执行",
    "C.参考案例和法规",
    "D.管辖",
    "Z.原始证据",
    "Z.待归类",
]

# 追加劳动争议特殊目录(从 directory_template.json 的 labor_dispute 模板加载,与模板单一事实源一致)
if directory_config and "case_type_templates" in directory_config:
    _labor = directory_config["case_type_templates"].get("labor_dispute", {})
    _labor_dirs = [d["name"] for d in _labor.get("level1", []) if isinstance(d, dict) and "name" in d]
    for _d in _labor_dirs:
        if _d not in STANDARD_DIRS:
            STANDARD_DIRS.append(_d)


# 文件角色识别规则(基于文件名 + 所在目录)
def identify_role(filename, parent_dir):
    """根据文件名和所在目录推断语义角色"""
    name = filename.lower()

    # 0.委托发票
    if parent_dir == "0.委托发票":
        if "身份证" in filename:
            return "id_card"
        if "法律服务合同" in filename or "服务合同" in filename:
            return "engagement_contract"
        if "授权委托书" in filename:
            return "poa"
        if "所函" in filename:
            return "firm_letter"
        if "发票" in filename:
            return "invoice"

    # 1.起诉状和证据
    if parent_dir == "1.起诉状和证据":
        if "起诉状" in filename and filename.endswith(".docx"):
            return "complaint_draft"
        if "起诉状" in filename and filename.endswith(".pdf"):
            return "complaint_signed"
        if "证据目录" in filename and filename.endswith(".docx"):
            return "evidence_list_draft"
        if "证据目录" in filename and filename.endswith(".pdf"):
            return "evidence_list_signed"
        if filename.startswith("证据(合并)"):
            return "evidence_merged"
        if filename.startswith("证据") and filename.endswith(".pdf"):
            return "evidence"

    # 3.答辩和证据
    if parent_dir == "3.答辩和证据":
        if "答辩状" in filename and filename.endswith(".docx"):
            return "defense_draft"
        if "答辩状" in filename and filename.endswith(".pdf"):
            return "defense_signed"

    # 4.反诉和证据
    if parent_dir == "4.反诉和证据":
        if "反诉状" in filename and filename.endswith(".docx"):
            return "counterclaim_draft"
        if "反诉状" in filename and filename.endswith(".pdf"):
            return "counterclaim_signed"

    # 5.上诉状和证据
    if parent_dir == "5.上诉状和证据":
        if "上诉状" in filename and filename.endswith(".docx"):
            return "appeal_draft"
        if "上诉状" in filename and filename.endswith(".pdf"):
            return "appeal_signed"

    # 8.再审申请和证据
    if parent_dir == "8.再审申请和证据":
        if "再审申请书" in filename and filename.endswith(".docx"):
            return "retrial_draft"
        if "再审申请书" in filename and filename.endswith(".pdf"):
            return "retrial_signed"

    # 2.法院通知 一审 / 6.法院通知 二审 / 9.法院通知 再审
    if parent_dir in ("2.法院通知 一审", "6.法院通知 二审", "9.法院通知 再审"):
        if "传票" in filename:
            return "summons"
        if "受理" in filename:
            return "acceptance_notice"

    # A.财产保全
    if parent_dir == "A.财产保全":
        if "财产保全裁定" in filename:
            return "preservation_order"

    # 根目录判决书
    if parent_dir == "." or parent_dir == "":
        if filename.startswith("判决书") and "一审" in filename:
            return "judgment_first"
        if filename.startswith("判决书") and "二审" in filename:
            return "judgment_second"
        if filename.startswith("判决书") and "再审" in filename:
            return "judgment_retrial"
        if filename == "文件整理操作日志.txt":
            return "log"

    return None


def extract_seq(filename):
    """从 '证据3 XXX.pdf' 类文件名提取序号"""
    import re
    m = re.match(r"^证据(\d+)\s", filename)
    if m:
        return int(m.group(1))
    return None


def build_directory_tree(case_root):
    """扫描当前文件结构,生成 directory_tree 字段"""
    tree = {}

    # 根目录
    root_files = []
    for name in os.listdir(case_root):
        if name.startswith("."):
            continue
        full = os.path.join(case_root, name)
        if os.path.isfile(full):
            ext = os.path.splitext(name)[1].lstrip(".")
            role = identify_role(name, ".")
            root_files.append({"name": name, "ext": ext, "role": role})

    if root_files:
        tree["root"] = {"path": ".", "files": root_files}
    else:
        tree["root"] = {"path": ".", "files": []}

    # 各标准二级目录
    for dir_name in STANDARD_DIRS:
        dir_path = os.path.join(case_root, dir_name)
        if not os.path.isdir(dir_path):
            tree[dir_name] = None
            continue

        files = []
        for name in os.listdir(dir_path):
            if name.startswith("."):
                continue
            full = os.path.join(dir_path, name)
            if os.path.isfile(full):
                ext = os.path.splitext(name)[1].lstrip(".")
                role = identify_role(name, dir_name)
                entry = {"name": name, "ext": ext, "role": role}
                seq = extract_seq(name)
                if seq is not None:
                    entry["seq"] = seq
                if dir_name == "Z.原始证据":
                    ocr_companion = os.path.join(dir_path, "." + name + ".ocr.txt")
                    if os.path.isfile(ocr_companion):
                        entry["ocr"] = "." + name + ".ocr.txt"
                files.append(entry)

        if files:
            tree[dir_name] = {"path": dir_name, "files": files}
        else:
            tree[dir_name] = None

    return tree


def build_role_index(case_root):
    """构建 role_index:role → [相对路径...]"""
    index = {}

    # 根目录
    for name in os.listdir(case_root):
        if name.startswith("."):
            continue
        full = os.path.join(case_root, name)
        if os.path.isfile(full):
            role = identify_role(name, ".")
            if role:
                index.setdefault(role, []).append(name)

    # 二级目录
    for dir_name in STANDARD_DIRS:
        dir_path = os.path.join(case_root, dir_name)
        if not os.path.isdir(dir_path):
            continue
        for name in os.listdir(dir_path):
            if name.startswith("."):
                continue
            full = os.path.join(dir_path, name)
            if os.path.isfile(full):
                role = identify_role(name, dir_name)
                if role:
                    rel = os.path.join(dir_name, name)
                    index.setdefault(role, []).append(rel)

    return index


def build_stats(case_root):
    """统计摘要"""
    total = 0
    pending = 0
    evidence_first = 0
    evidence_defense = 0

    for dirpath, _, filenames in os.walk(case_root):
        for name in filenames:
            if name.startswith("."):
                continue
            total += 1
            rel_dir = os.path.relpath(dirpath, case_root)
            if "Z.待归类" in rel_dir:
                pending += 1
            if rel_dir == "1.起诉状和证据" and name.startswith("证据") and "(合并)" not in name:
                evidence_first += 1
            if rel_dir == "3.答辩和证据" and name.startswith("证据") and "(合并)" not in name:
                evidence_defense += 1

    evidence_merged_first = os.path.exists(
        os.path.join(case_root, "1.起诉状和证据", "证据(合并).pdf")
    )
    evidence_merged_defense = os.path.exists(
        os.path.join(case_root, "3.答辩和证据", "证据(合并).pdf")
    )

    return {
        "total_files": total,
        "pending_files": pending,
        "evidence_count_first": evidence_first,
        "evidence_merged_first": evidence_merged_first,
        "evidence_count_defense": evidence_defense,
        "evidence_merged_defense": evidence_merged_defense,
    }


def _derive_representing_side(snapshot):
    """从 snapshot 推导当前的代理方向。

    优先级: first_instance > second_instance > third_instance > counterclaim_side
    返回: "原告"/"被告"/"申请人"/"被申请人"/"上诉人"/"被上诉人" 或 None
    """
    stages = [
        ("first_instance", ["原告", "被告"]),
        ("second_instance", ["上诉人", "被上诉人"]),
        ("third_instance", ["申请人", "被申请人"]),
    ]
    for stage_key, valid_values in stages:
        stage = snapshot.get(stage_key, {})
        side = stage.get("representation_side") if isinstance(stage, dict) else None
        if side in valid_values:
            return side
    counterclaim = snapshot.get("skill_handoff", {}).get("counterclaim_side")
    if counterclaim:
        return counterclaim
    return None


def generate_case_index(case_root, snapshot):
    """生成 .case_index.json 主函数"""
    now = datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')
    case_name = os.path.basename(case_root.rstrip("/"))

    # --- metadata (SKILL.md §9.14 强制要求) ---
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "skill_name": SKILL_NAME,
        "execution_count": snapshot.get("run_count", 0) + 1 if snapshot else 1,
        "resync_count": snapshot.get("resync_count", 0) if snapshot else 0,
        "last_normal_run": now,
        "last_resync": snapshot.get("last_resync") if snapshot else None,
    }

    # --- cause_route 初始化 (SKILL.md §4.5 要求, 必须存在) ---
    cause_route = {
        "status": "not_initialized",
        "cause_zh": None,
        "cause_zh_source": None,
        "secondary_causes": [],
        "route_file": None,
        "routed_at": None,
        "cache_file": ".case_route_cache.json",
        "sections_available": [],
        "sections_pending": [],
        "route_md_role": None,
        "stale_reason": None,
    }

    index = {
        "metadata": metadata,
        "generated_at": now,
        "case_name": case_name,
        "skill_version": SKILL_VERSION,

        "representing_side": _derive_representing_side(snapshot) if snapshot else None,

        "representation": {
            "first_instance":  snapshot.get("first_instance", {}).get("representation_side") if snapshot else None,
            "second_instance": snapshot.get("second_instance", {}).get("representation_side") if snapshot else None,
            "third_instance":  snapshot.get("third_instance", {}).get("representation_side") if snapshot else None,
            "counterclaim_side": snapshot.get("skill_handoff", {}).get("counterclaim_side") if snapshot else None,
        },

        "cause_route": cause_route,

        "directory_tree": build_directory_tree(case_root),
        "role_index":     build_role_index(case_root),
        "exclude_hints":  DEFAULT_EXCLUDE_HINTS,
        "pending_issues": snapshot.get("skill_handoff", {}).get("pending_issues", []) if snapshot else [],
        "stats":          build_stats(case_root),
    }

    # 如果快照有 case_stage(收案前阶段),写入
    if snapshot and "case_stage" in snapshot:
        index["case_stage"] = snapshot["case_stage"]
        if snapshot["case_stage"] == "pre_litigation":
            index["case_stage_note"] = (
                "收案前阶段:未检测到诉讼阶段文件,文件按语义类型归类至根目录子目录"
            )

    index_path = os.path.join(case_root, ".case_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


if __name__ == "__main__":
    import sys
    case_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    snapshot_path = os.path.join(case_root, ".case_snapshot.json")
    snapshot = None
    if os.path.exists(snapshot_path):
        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
    result = generate_case_index(case_root, snapshot)
    print("✅ .case_index.json 已生成")
    print(f"  case_name: {result['case_name']}")
    print(f"  total_files: {result['stats']['total_files']}")
