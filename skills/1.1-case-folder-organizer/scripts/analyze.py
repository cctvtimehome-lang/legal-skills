"""
case-folder-organizer / analyze.py

扫描案件文件夹,生成操作计划草稿。
由 AI 在用户确认前阶段调用,产出:
  - auto_ops:高置信度的自动化操作列表
  - llm_needed:需要 LLM 视觉识别的文件(乱码文件名身份证扫描件等)
  - warnings:需要人工决定的情况

输出到 /tmp/case_analysis_result.json。

调用方式:
  python analyze.py "<案件文件夹完整路径>" --snapshot ".case_snapshot.json" --incremental
"""

import os
import sys
import json
import hashlib
import argparse
import re
from datetime import datetime

# 导入配置加载器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config, calculate_md5


# ============ 文件扫描与元数据 ============

def scan_files(case_root):
    """递归扫描所有文件(排除隐藏文件)，计算MD5"""
    file_index = {}
    for dirpath, _, filenames in os.walk(case_root):
        for name in filenames:
            if name.startswith("."):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, case_root)
            stat = os.stat(full)
            # 使用 config_loader 的 calculate_md5
            md5_hash = calculate_md5(full)
            # 强制32位：如果前导零被省略，补回来
            md5_hash = md5_hash.zfill(32)
            file_index[rel] = {
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
                "md5": md5_hash,
            }
    return file_index


# ============ 增量判断 ============

def load_snapshot(case_root):
    path = os.path.join(case_root, ".case_snapshot.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff_files(current, previous):
    """对比当前文件索引与快照,返回新增/变更列表"""
    if previous is None:
        return {"added": list(current.keys()), "changed": [], "removed": []}

    prev_idx = previous.get("file_index", {})
    added, changed = [], []
    for rel, meta in current.items():
        if rel not in prev_idx:
            added.append(rel)
        elif (meta["size"] != prev_idx[rel]["size"]
              or meta["mtime"] != prev_idx[rel]["mtime"]):
            changed.append(rel)

    removed = [rel for rel in prev_idx if rel not in current]
    return {"added": added, "changed": changed, "removed": removed}


# ============ 文件名规范化 ============

def normalize_brackets(name):
    """全角括号→半角"""
    return name.replace("(", "(").replace(")", ")")


# ============ 分析主流程 ============

def analyze(case_root, incremental=True):
    """
    主分析入口。
    返回 {auto_ops, llm_needed, warnings} 三类结果。

    注意:本实现提供骨架和增量判断框架,
    具体的 role 识别、归类决策由 AI 在对话中结合 reference/ 规则做出。
    """
    result = {
        "auto_ops": [],      # 高置信度操作:{type, src, dst, reason}
        "llm_needed": [],    # 需要 LLM 视觉识别的文件
        "warnings": [],      # 需要人工判断的情况
    }

    current = scan_files(case_root)
    snapshot = load_snapshot(case_root)

    if incremental and snapshot:
        diff = diff_files(current, snapshot)
        targets = diff["added"] + diff["changed"]
        result["diff"] = diff
        result["mode"] = "incremental"
    else:
        targets = list(current.keys())
        result["mode"] = "full"

    # 全角括号批量修复(零 token 操作)
    for rel in targets:
        name = os.path.basename(rel)
        fixed = normalize_brackets(name)
        if name != fixed:
            result["auto_ops"].append({
                "type": "rename",
                "src": os.path.join(case_root, rel),
                "dst": os.path.join(os.path.dirname(os.path.join(case_root, rel)), fixed),
                "reason": "全角括号→半角",
            })

    # 乱码文件名检测(身份证扫描件常见):以 IMG_/scan/扫描件/DOC 开头,
    # 或包含大量非中文非字母数字字符,归入 llm_needed
    for rel in targets:
        name = os.path.basename(rel)
        stem, _ = os.path.splitext(name)
        is_garbled = (
            re.match(r"^(IMG_|scan|扫描件|DOC|image|photo)", stem, re.IGNORECASE)
            or len([c for c in stem if not (c.isalnum() or '\u4e00' <= c <= '\u9fff' or c in ' _-')]) > 2
        )
        if is_garbled:
            result["llm_needed"].append({
                "path": os.path.join(case_root, rel),
                "reason": "文件名疑似乱码,需要视觉识别确认内容",
            })

    # 更新的 file_index 供后续快照写入使用
    result["file_index"] = current

    return result


# ============ CLI ============

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case_root", help="案件文件夹完整路径")
    parser.add_argument("--snapshot", default=".case_snapshot.json")
    parser.add_argument("--incremental", action="store_true", default=True)
    parser.add_argument("--full", action="store_true", help="全量模式,忽略快照")
    args = parser.parse_args()

    incremental = not args.full
    result = analyze(args.case_root, incremental=incremental)

    output_path = "/tmp/case_analysis_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    summary = {
        "mode": result["mode"],
        "auto_ops": len(result["auto_ops"]),
        "llm_needed": len(result["llm_needed"]),
        "warnings": len(result["warnings"]),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
