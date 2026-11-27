#!/usr/bin/env python3
"""
配置文件版本迁移工具 - 共享版本
用于在不同版本配置之间迁移和兼容处理
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Callable, Optional
from datetime import datetime

class ConfigMigration:
    """配置迁移器"""
    
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        self.migrations = {}  # version -> migration_function
        self.backup_dir = Path.home() / ".workbuddy" / "backups" / skill_name
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def register_migration(self, from_version: str, to_version: str, migration_fn: Callable):
        """注册迁移函数"""
        key = f"{from_version}->{to_version}"
        self.migrations[key] = migration_fn
    
    def backup_config(self, config_path: str) -> str:
        """备份配置文件"""
        config_file = Path(config_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_file.stem}_{timestamp}{config_file.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(config_path, backup_path)
        print(f"✅ 已备份: {backup_path}")
        return str(backup_path)
    
    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self, config: Dict, config_path: str):
        """保存配置文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存: {config_path}")
    
    def get_version(self, config: Dict) -> str:
        """获取配置版本"""
        meta = config.get('_meta') or config.get('meta', {})
        return meta.get('version', '0.0.0')
    
    def set_version(self, config: Dict, version: str):
        """设置配置版本"""
        if '_meta' in config:
            config['_meta']['version'] = version
            config['_meta']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        elif 'meta' in config:
            config['meta']['version'] = version
            config['meta']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    def migrate(self, config_path: str, target_version: str) -> bool:
        """
        执行迁移
        返回: 是否成功
        """
        print(f"\n开始迁移: {config_path}")
        print(f"目标版本: {target_version}")
        
        # 1. 备份
        self.backup_config(config_path)
        
        # 2. 加载配置
        config = self.load_config(config_path)
        current_version = self.get_version(config)
        
        print(f"当前版本: {current_version}")
        
        if current_version == target_version:
            print("ℹ️  版本相同，无需迁移")
            return True
        
        # 3. 执行迁移（简化版：直接更新版本号）
        # 实际使用时，应注册具体的迁移函数
        self.set_version(config, target_version)
        
        # 4. 保存
        self.save_config(config, config_path)
        
        print(f"✅ 迁移完成: {current_version} → {target_version}")
        return True
    
    def auto_migrate(self, config_path: str) -> bool:
        """
        自动迁移到最新版本
        需要在子类中定义 latest_version
        """
        raise NotImplementedError("子类需实现 auto_migrate")


def migrate_config_version(config: Dict, from_ver: str, to_ver: str) -> Dict:
    """
    通用版本迁移函数（简化版）
    实际使用时根据需要添加具体迁移逻辑
    """
    # 示例：从 1.0.0 迁移到 1.1.0
    if from_ver == "1.0.0" and to_ver == "1.1.0":
        # 添加新字段
        if '_meta' in config:
            config['_meta']['migrated'] = True
            config['_meta']['migrated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return config


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python migrate_config.py <config_file> <target_version>")
        print("示例: python migrate_config.py legal_theory_templates.json 1.1.0")
        sys.exit(1)
    
    config_path = sys.argv[1]
    target_version = sys.argv[2]
    
    # 提取skill名称（从路径推断）
    path_parts = Path(config_path).parts
    skill_name = "unknown"
    for i, part in enumerate(path_parts):
        if part == "skills" and i + 1 < len(path_parts):
            skill_name = path_parts[i + 1]
            break
    
    migrator = ConfigMigration(skill_name)
    success = migrator.migrate(config_path, target_version)
    
    sys.exit(0 if success else 1)
