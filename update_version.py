#!/usr/bin/env python3
"""
版本更新脚本
用于更新项目中所有文件的版本号
"""

import sys
import os
from pathlib import Path

# 添加mcu_code_analyzer到路径
sys.path.insert(0, str(Path(__file__).parent / "mcu_code_analyzer"))

from utils.version_manager import VersionManager

def main():
    """主函数"""
    print("🔧 MCU Code Analyzer 版本更新工具")
    print("=" * 50)
    
    try:
        # 初始化版本管理器
        config_path = Path(__file__).parent / "mcu_code_analyzer" / "config.yaml"
        vm = VersionManager(config_path)
        
        # 显示当前版本信息
        current_version = vm.get_version()
        version_info = vm.get_version_info()
        
        print(f"📋 当前版本: {current_version}")
        print(f"📅 发布日期: {version_info['release_date']}")
        print(f"📝 描述: {version_info['description']}")
        print()
        
        # 同步版本号到所有文件
        print("🔄 正在同步版本号到所有相关文件...")
        updated_files = vm.sync_version_to_files()
        
        if updated_files:
            print(f"✅ 成功更新了 {len(updated_files)} 个文件:")
            for file_path in updated_files:
                print(f"   - {file_path}")
        else:
            print("ℹ️  所有文件的版本号已经是最新的")
        
        print()
        print(f"🎉 版本同步完成! 当前版本: {current_version}")
        
    except Exception as e:
        print(f"❌ 版本更新失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
