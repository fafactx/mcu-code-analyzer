#!/usr/bin/env python3
"""
MCU Code Analyzer - 根目录构建脚本
在根目录直接运行构建，自动进入mcu_code_analyzer目录执行构建
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 MCU Code Analyzer - Root Directory Build Script")
    print("=" * 60)
    
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()
    mcu_analyzer_dir = current_dir / "mcu_code_analyzer"
    
    # 检查mcu_code_analyzer目录是否存在
    if not mcu_analyzer_dir.exists():
        print("❌ mcu_code_analyzer目录不存在！")
        print(f"当前目录: {current_dir}")
        input("按回车键退出...")
        return 1
    
    # 检查build_exe.py是否存在
    build_script = mcu_analyzer_dir / "build_exe.py"
    if not build_script.exists():
        print("❌ mcu_code_analyzer/build_exe.py文件不存在！")
        input("按回车键退出...")
        return 1
    
    print(f"📁 切换到目录: {mcu_analyzer_dir}")
    print(f"🔨 执行构建脚本: {build_script}")
    print("-" * 60)
    
    try:
        # 切换到mcu_code_analyzer目录并执行构建
        result = subprocess.run(
            [sys.executable, "build_exe.py"],
            cwd=mcu_analyzer_dir,
            check=True
        )
        
        print("-" * 60)
        print("✅ 构建完成！")
        
        # 检查生成的exe文件
        dist_dir = mcu_analyzer_dir / "dist"
        if dist_dir.exists():
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                print(f"📦 生成的exe文件: {exe_files[0]}")
                
                # 复制exe文件到根目录
                import shutil
                exe_file = exe_files[0]
                target_file = current_dir / exe_file.name
                shutil.copy2(exe_file, target_file)
                print(f"📋 已复制到根目录: {target_file}")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return 1
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code != 0:
        input("按回车键退出...")
    sys.exit(exit_code)
