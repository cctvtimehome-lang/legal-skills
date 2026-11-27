#!/usr/bin/env python3
"""
配置文件验证工具 - 共享版本
用于验证各skill的assets配置文件格式是否正确
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, skill_name: str = None):
        self.skill_name = skill_name
        self.errors = []
        self.warnings = []
    
    def validate_meta(self, config: Dict, file_path: str) -> bool:
        """验证_meta字段"""
        if '_meta' not in config and 'meta' not in config:
            self.warnings.append(f"{file_path}: 缺少meta/_meta字段")
            return False
        
        meta = config.get('_meta') or config.get('meta')
        required_fields = ['name', 'version', 'description']
        
        for field in required_fields:
            if field not in meta:
                self.errors.append(f"{file_path}: meta缺少必需字段 '{field}'")
        
        return len(self.errors) == 0
    
    def validate_json_schema(self, config: Dict, schema: Dict) -> bool:
        """验证JSON Schema（简化版）"""
        # 基础结构验证
        for key, value_type in schema.items():
            if key not in config:
                self.errors.append(f"缺少必需字段: {key}")
            elif not isinstance(config[key], value_type):
                self.errors.append(f"字段 {key} 类型错误，应为 {value_type.__name__}")
        
        return len(self.errors) == 0
    
    def validate_file_size(self, file_path: str, max_kb: int = 50) -> bool:
        """验证文件大小"""
        size_kb = os.path.getsize(file_path) / 1024
        if size_kb > max_kb:
            self.warnings.append(f"{file_path}: 文件大小 {size_kb:.1f}KB 超过建议值 {max_kb}KB")
            return False
        return True
    
    def validate_config_file(self, file_path: str) -> Tuple[bool, Dict]:
        """
        验证单个配置文件
        返回: (is_valid, config_data)
        """
        self.errors = []
        self.warnings = []
        
        # 1. 检查文件存在
        if not os.path.exists(file_path):
            self.errors.append(f"文件不存在: {file_path}")
            return False, {}
        
        # 2. 检查文件格式
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON格式错误: {e}")
            return False, {}
        except Exception as e:
            self.errors.append(f"读取失败: {e}")
            return False, {}
        
        # 3. 验证meta信息
        self.validate_meta(config, file_path)
        
        # 4. 验证文件大小
        self.validate_file_size(file_path)
        
        is_valid = len(self.errors) == 0
        return is_valid, config
    
    def print_report(self):
        """打印验证报告"""
        if self.errors:
            print("❌ 错误:")
            for err in self.errors:
                print(f"  - {err}")
        
        if self.warnings:
            print("⚠️  警告:")
            for warn in self.warnings:
                print(f"  - {warn}")
        
        if not self.errors and not self.warnings:
            print("✅ 验证通过")
    
    @staticmethod
    def validate_skill_assets(skill_path: str) -> Dict[str, Tuple[bool, List[str]]]:
        """
        验证单个skill的所有assets配置文件
        返回: {filename: (is_valid, messages)}
        """
        results = {}
        assets_path = Path(skill_path) / "assets"
        
        if not assets_path.exists():
            return results
        
        for json_file in assets_path.glob("*.json"):
            validator = ConfigValidator()
            is_valid, _ = validator.validate_config_file(str(json_file))
            results[json_file.name] = (is_valid, validator.errors + validator.warnings)
        
        return results


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python validate_config.py <skill_path_or_config_file>")
        print("示例: python validate_config.py ~/.gemini/config/plugins/legal-workbuddy/skills/2.3-legal-theory-analysis")
        print("示例: python validate_config.py ~/.gemini/config/plugins/legal-workbuddy/skills/2.3-legal-theory-analysis/assets/legal_theory_templates.json")
        sys.exit(1)
    
    target_path = sys.argv[1]
    
    if os.path.isfile(target_path) and target_path.endswith('.json'):
        # 验证单个文件
        validator = ConfigValidator()
        is_valid, config = validator.validate_config_file(target_path)
        validator.print_report()
        sys.exit(0 if is_valid else 1)
    
    elif os.path.isdir(target_path):
        # 验证整个skill的assets
        results = ConfigValidator.validate_skill_assets(target_path)
        
        print(f"验证结果: {target_path}")
        print("=" * 60)
        
        all_passed = True
        for filename, (is_valid, messages) in results.items():
            status = "✅" if is_valid else "❌"
            print(f"{status} {filename}")
            for msg in messages:
                print(f"    {msg}")
            if not is_valid:
                all_passed = False
        
        print("=" * 60)
        print(f"总计: {len(results)} 个文件, {'全部通过' if all_passed else '存在错误'}")
        sys.exit(0 if all_passed else 1)
    else:
        print(f"错误: 路径不存在 {target_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
