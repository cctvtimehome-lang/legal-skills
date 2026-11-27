#!/usr/bin/env python3
"""
统一配置加载器 - 共享版本
所有skills可以调用此模块加载配置文件
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, skill_name: str = None):
        """
        初始化配置加载器
        
        Args:
            skill_name: skill名称，用于定位assets目录
                      如果为None，则使用当前文件所在目录
        """
        self.skill_name = skill_name
        if skill_name:
            # 定位到 ~/.gemini/config/plugins/legal-workbuddy/skills/<skill_name>/assets/
            self.asset_dir = Path.home() / ".gemini" / "config" / "plugins" / "legal-workbuddy" / "skills" / skill_name / "assets"
        else:
            # 使用当前脚本所在目录的../assets/
            self.asset_dir = Path(__file__).parent.parent / "assets"
    
    def load(self, config_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_name: 配置文件名（不含.json后缀）或完整文件名
            use_cache: 是否使用缓存（暂未实现）
        
        Returns:
            配置字典
        
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: JSON格式错误
        """
        # 自动添加.json后缀
        if not config_name.endswith('.json'):
            config_name += '.json'
        
        config_path = self.asset_dir / config_name
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config
    
    def load_with_default(self, config_name: str, default_value: Dict = None) -> Dict[str, Any]:
        """
        加载配置文件，如果不存在则返回默认值
        
        Args:
            config_name: 配置文件名
            default_value: 默认配置（如果文件不存在）
        
        Returns:
            配置字典
        """
        try:
            return self.load(config_name)
        except FileNotFoundError:
            return default_value if default_value else {}
    
    def list_configs(self) -> list:
        """列出所有可用的配置文件"""
        if not self.asset_dir.exists():
            return []
        
        return sorted([f.name for f in self.asset_dir.glob("*.json")])
    
    def get_meta(self, config_name: str) -> Dict[str, Any]:
        """
        获取配置文件的meta信息
        
        Returns:
            meta字典，如果不存在则返回空字典
        """
        config = self.load(config_name)
        return config.get('_meta') or config.get('meta', {})
    
    def validate(self, config_name: str) -> tuple:
        """
        验证配置文件
        
        Returns:
            (is_valid, errors_list)
        """
        config_path = self.asset_dir / (config_name if config_name.endswith('.json') else f"{config_name}.json")
        
        # 调用validate_config.py
        import subprocess
        validate_script = Path(__file__).parent / "validate_config.py"
        
        if not validate_script.exists():
            return False, ["validate_config.py 不存在"]
        
        result = subprocess.run(
            ["python3", str(validate_script), str(config_path)],
            capture_output=True,
            text=True
        )
        
        is_valid = result.returncode == 0
        messages = result.stdout + result.stderr
        
        return is_valid, [messages] if messages else []


# ============ 便捷函数接口 ============

def load_config(config_name: str, skill_name: str = None) -> Dict[str, Any]:
    """
    便捷函数: 加载当前 skill 的配置文件
    
    Args:
        config_name: 配置文件名（不含.json后缀）
        skill_name: skill名称，默认自动从调用栈推断
    
    Returns:
        配置字典
    """
    if skill_name is None:
        # 从调用栈推断 skill 名称
        import inspect
        caller_file = inspect.stack()[1].filename
        # 路径形如 ~/.gemini/config/plugins/legal-workbuddy/skills/<skill_name>/scripts/xxx.py
        parts = Path(caller_file).parts
        for i, part in enumerate(parts):
            if part == "skills" and i + 1 < len(parts):
                skill_name = parts[i + 1]
                break
        if skill_name is None:
            skill_name = "1.1-case-folder-organizer"
    
    loader = ConfigLoader(skill_name)
    return loader.load(config_name)


def calculate_md5(file_path: str) -> str:
    """
    计算文件 MD5（32位小写十六进制）
    """
    import hashlib
    h = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    """命令行测试"""
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python config_loader.py <skill_name> <config_name>")
        print("示例: python config_loader.py 2.3-legal-theory-analysis legal_theory_templates")
        sys.exit(1)
    
    skill_name = sys.argv[1]
    config_name = sys.argv[2]
    
    loader = ConfigLoader(skill_name)
    
    try:
        config = loader.load(config_name)
        print(f"✅ 成功加载: {config_name}")
        print(f"Keys: {list(config.keys())}")
        
        meta = loader.get_meta(config_name)
        if meta:
            print(f"Meta: {meta.get('description', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# 模块级函数（供其他脚本导入）
# ---------------------------------------------------------------------------

def get_assets_dir(skill_name: str = None) -> Path:
    """
    模块级函数：获取assets目录路径
    
    Args:
        skill_name: skill名称（默认自动检测）
    
    Returns:
        assets目录Path对象
    """
    loader = ConfigLoader(skill_name)
    return loader.asset_dir


def get_skill_dir(skill_name: str = None) -> Path:
    """
    模块级函数：获取skill根目录路径
    
    Args:
        skill_name: skill名称（默认自动检测）
    
    Returns:
        skill根目录Path对象
    """
    if skill_name:
        return Path.home() / ".gemini" / "config" / "plugins" / "legal-workbuddy" / "skills" / skill_name
    else:
        return Path(__file__).parent.parent


if __name__ == "__main__":
    main()
