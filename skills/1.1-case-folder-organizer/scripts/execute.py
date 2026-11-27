"""
case-folder-organizer / execute.py

用户确认后,按 /tmp/case_plan.json 中的操作列表执行文件操作。

执行顺序(固定,不可调换):
  1. 新建目录(先建目录,再移文件)
  2. 文件重命名、移动、删除
  3. 文件夹重命名(最后执行,避免路径失效)
  4. 更新 .case_snapshot.json
  5. 生成/更新 .case_index.json(收尾最后一步)

每项操作均捕获异常,失败时记录错误继续执行,不中断整体流程。
"""

import os
import sys
import json
import shutil
from datetime import datetime

# 导入配置加载器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config

# 从同目录导入索引生成函数
from generate_index import generate_case_index


# ============ 原子操作 ============

def do_mkdir(path, log):
    os.makedirs(path, exist_ok=True)
    log.append(f"[新建目录] {path}")


def do_rename(src, dst, log):
    if not os.path.exists(src):
        log.append(f"[跳过] {src} 不存在")
        return
    if os.path.exists(dst):
        log.append(f"[跳过] 目标已存在: {dst}")
        return
    os.rename(src, dst)
    log.append(f"[重命名] {os.path.basename(src)} → {os.path.basename(dst)}")


def do_move(src, dst, log):
    shutil.move(src, dst)
    log.append(f"[移动] {os.path.basename(src)} → {dst}")


def do_move_preserve_mtime(src, dst, log):
    """Z.原始证据 专用:移动时还原时间戳"""
    stat = os.stat(src)
    shutil.move(src, dst)
    os.utime(dst, (stat.st_atime, stat.st_mtime))
    log.append(f"[移动(保留mtime)] {os.path.basename(src)} → {dst}")


def do_delete(path, reason, log):
    os.remove(path)
    log.append(f"[删除] {os.path.basename(path)}  原因:{reason}")


def do_rename_folder(src, dst, log):
    os.rename(src, dst)
    log.append(f"[文件夹] {os.path.basename(src)} → {os.path.basename(dst)}")


# ============ 收尾步骤 ============

def update_snapshot(case_root, snapshot):
    """Step 4:更新 .case_snapshot.json (符合 01-snapshot-schema.md 完整 schema)"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 确保 metadata 存在 (SKILL.md §9.14)
    metadata = snapshot.get("metadata", {})
    metadata.setdefault("schema_version", "1.0")
    metadata.setdefault("skill_name", "case-folder-organizer")
    metadata["execution_count"] = metadata.get("execution_count", 0) + 1
    metadata.setdefault("resync_count", 0)
    metadata["last_normal_run"] = now
    metadata.setdefault("last_resync", None)

    snapshot["metadata"] = metadata
    snapshot["last_run"] = now

    # 确保必要字段存在
    snapshot.setdefault("file_index", {})
    snapshot.setdefault("first_instance", {})
    snapshot.setdefault("second_instance", {})
    snapshot.setdefault("third_instance", {})
    snapshot.setdefault("skill_handoff", {})
    snapshot.setdefault("run_count", metadata["execution_count"] - 1)

    # 保留已有的 case_stage
    if "case_stage" in snapshot and snapshot["case_stage"]:
        snapshot["last_run"] = now
    else:
        snapshot["case_stage"] = snapshot.get("case_stage", "")

    path = os.path.join(case_root, ".case_snapshot.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)


def init_or_update_progress(case_root):
    """
    Step 7:初始化或更新 .case_progress.json (SKILL.md §3.3)
    首次执行时创建,后续执行时回写 folder_organized 节点
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    progress_path = os.path.join(case_root, ".case_progress.json")

    if os.path.exists(progress_path):
        with open(progress_path, "r", encoding="utf-8") as f:
            progress = json.load(f)
    else:
        # 首次创建 — 初始化所有 milestone 节点
        progress = {
            "metadata": {
                "schema_version": "1.0",
                "skill_name": "case-folder-organizer",
                "execution_count": 1,
                "resync_count": 0,
                "last_normal_run": now,
                "last_resync": None
            },
            "version": "1.0",
            "case_folder": case_root,
            "last_updated_at": now,
            "current_stage": "Part1-收案",
            "milestones": {
                "folder_organized":  {"done": True, "run_count": 1, "done_at": now},
                "cause_routed":      {"done": False, "run_count": 0, "done_at": None, "cause_zh": "", "secondary_causes": []},
                "summary_extracted": {"done": False, "run_count": 0, "done_at": None},
                "law_researched":    {"done": False, "run_count": 0, "done_at": None},
                "opinion_generated": {"done": False, "run_count": 0, "done_at": None},
                "service_proposed":  {"done": False, "run_count": 0, "done_at": None},
                "legal_theory_done": {"done": False, "run_count": 0, "done_at": None},
                "case_closed":       {"done": False, "run_count": 0, "done_at": None, "close_type": ""}
            }
        }
        with open(progress_path, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        return progress

    # 回写 folder_organized 节点 — 外科手术式,只改本节点
    fo = progress.setdefault("milestones", {}).setdefault("folder_organized", {})
    fo["done"] = True
    fo["run_count"] = fo.get("run_count", 0) + 1
    fo["done_at"] = now

    # 更新 metadata
    meta = progress.setdefault("metadata", {})
    meta.setdefault("schema_version", "1.0")
    meta.setdefault("skill_name", "case-folder-organizer")
    meta["execution_count"] = meta.get("execution_count", 0) + 1
    meta.setdefault("resync_count", 0)
    meta["last_normal_run"] = now
    meta.setdefault("last_resync", None)

    progress["last_updated_at"] = now

    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

    return progress


def ensure_route_cache_placeholder(case_root):
    """
    Step 6:确保 .case_route_cache.json 占位文件存在。
    LLM 端的 §4.5 负责填充实际内容,Python 端只需确保文件骨架存在。
    """
    cache_path = os.path.join(case_root, ".case_route_cache.json")
    if os.path.exists(cache_path):
        return  # 已存在,由 LLM 端更新

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 加载配置
    confidence_config = load_config("confidence_levels")
    default_confidence = "low"
    
    placeholder = {
        "metadata": {
            "schema_version": "1.0",
            "skill_name": "case-folder-organizer",
            "execution_count": 1,
            "resync_count": 0,
            "source_route_md": None,
            "source_route_md_mtime": None,
            "last_normal_run": now,
            "last_resync": None
        },
        "version": "1.0",
        "generated_at": now,
        "cause_zh": None,
        "cause_variants": [],
        "route_file": None,
        "route_file_path": None,
        "confidence": default_confidence,
        "cause_source": "placeholders_only",
        "sections_available": [],
        "sections_pending": [],
        "sections": {},
        "route_full_text_available": False,
        "route_full_text_note": "占位文件,待 LLM §4.5 案由预判后更新"
    }
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(placeholder, f, ensure_ascii=False, indent=2)


def finalize(case_root, snapshot, log):
    """
    收尾步骤(Step 4-7,顺序不可颠倒,对应 SKILL.md §7):
      Step 4: 更新 .case_snapshot.json (完整 schema + metadata)
      Step 5: 生成/更新 .case_index.json (含 metadata + cause_route)
      Step 6: 生成 .case_route_cache.json 占位 (LLM §4.5 后续填充)
      Step 7: 初始化/更新 .case_progress.json
    """
    update_snapshot(case_root, snapshot)
    generate_case_index(case_root, snapshot)
    log.append("[索引更新] .case_index.json 已更新")
    ensure_route_cache_placeholder(case_root)
    log.append("[路由缓存] .case_route_cache.json 占位已创建")
    init_or_update_progress(case_root)
    log.append("[推进面板] .case_progress.json 已更新")


def write_operation_log(case_root, log_lines, trigger_type, total_files):
    """追加写入文件整理操作日志.txt (符合 22-logging-spec.md)"""
    log_path = os.path.join(case_root, "文件整理操作日志.txt")

    # 检查文件是否存在 — 已存在时简单追加分隔行,不重复写头部
    if os.path.exists(log_path):
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n")
    else:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("文件整理操作日志\n")
            f.write(f"案件:{os.path.basename(case_root.rstrip('/'))}\n")
            f.write(f"执行时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"触发方式:{trigger_type}\n")
            f.write(f"本次处理文件数:{total_files}\n")
            f.write("=" * 70 + "\n")

    # 追加本次操作日志
    with open(log_path, "a", encoding="utf-8") as f:
        for line in log_lines:
            f.write("  " + line + "\n")

        # 统计 Z.待归类/ 文件数 (22-logging-spec.md 要求)
        pending_dir = os.path.join(case_root, "Z.待归类")
        if os.path.isdir(pending_dir):
            pending_count = len([n for n in os.listdir(pending_dir) if not n.startswith(".")])
            f.write(f"  当前 Z.待归类/ 文件数:{pending_count}\n")
        else:
            f.write("  当前 Z.待归类/ 文件数:0\n")

        f.write("=" * 70 + "\n")


# ============ 主流程 ============

def execute_plan(plan_path, case_root, trigger_type="manual"):
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)

    log = []
    snapshot_path = os.path.join(case_root, ".case_snapshot.json")
    snapshot = {}
    if os.path.exists(snapshot_path):
        with open(snapshot_path, encoding="utf-8") as f:
            snapshot = json.load(f)

    # Step 1:新建目录
    for op in plan.get("mkdirs", []):
        try:
            do_mkdir(op["path"], log)
        except Exception as e:
            log.append(f"[错误] 新建目录失败 {op['path']}: {e}")

    # Step 2:文件操作(重命名、移动、删除)
    for op in plan.get("file_ops", []):
        try:
            op_type = op["type"]
            if op_type == "rename":
                do_rename(op["src"], op["dst"], log)
            elif op_type == "move":
                do_move(op["src"], op["dst"], log)
            elif op_type == "move_preserve_mtime":
                do_move_preserve_mtime(op["src"], op["dst"], log)
            elif op_type == "delete":
                do_delete(op["path"], op.get("reason", "未说明"), log)
        except Exception as e:
            log.append(f"[错误] {op}: {e}")

    # Step 3:文件夹重命名(最后执行)
    for op in plan.get("folder_renames", []):
        try:
            do_rename_folder(op["src"], op["dst"], log)
        except Exception as e:
            log.append(f"[错误] 文件夹重命名失败: {e}")

    # Step 4 + Step 5:更新快照 + 生成索引
    finalize(case_root, snapshot, log)

    # 写日志
    total = len(plan.get("file_ops", [])) + len(plan.get("mkdirs", [])) + len(plan.get("folder_renames", []))
    write_operation_log(case_root, log, trigger_type, total)

    print(f"执行完成,共 {total} 项操作")
    return log


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python execute.py <plan_path> <case_root> [trigger_type]")
        sys.exit(1)

    plan_path = sys.argv[1]
    case_root = sys.argv[2]
    trigger_type = sys.argv[3] if len(sys.argv) > 3 else "manual"

    execute_plan(plan_path, case_root, trigger_type)
