#!/usr/bin/env python3
"""
MCU Code Analyzer v2.1.0 - 真正的30MB构建脚本
完全基于老版本成功的命令行配置
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_banner():
    """打印构建横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║        MCU Code Analyzer v2.1.0 - 真正30MB构建               ║
║                                                              ║
║  🎯 完全复制老版本成功命令                                    ║
║  📦 最小化hiddenimports                                       ║
║  ⚡ 目标: 真正的30MB                                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🔍 当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("⚠️  Python 3.11+版本较大，建议使用Python 3.8-3.10")
        print("💡 这可能是文件大的主要原因")
    
    return True

def build_with_old_command():
    """使用老版本的完全相同命令构建"""
    print("🔨 使用老版本命令构建...")
    
    # 切换到mcu_code_analyzer目录
    os.chdir("mcu_code_analyzer")
    
    try:
        # 完全复制老版本的命令
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed", 
            "--name=MCUCodeAnalyzer_v2.1.0_True30MB",
            "--add-data=config.yaml;.",
            "--add-data=templates;templates",
            "--hidden-import=tkinter",
            "--hidden-import=yaml", 
            "--hidden-import=requests",
            "--hidden-import=chardet",
            "main_gui.py"  # 使用当前的入口文件
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 构建中...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 老版本命令构建成功！")
            
            exe_path = Path("dist/MCUCodeAnalyzer_v2.1.0_True30MB.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
                
                if size_mb <= 35:
                    print("🎯 ✅ 接近30MB目标！")
                elif size_mb <= 50:
                    print("🎯 ⚠️  比预期大，但有改善")
                else:
                    print("🎯 ❌ 仍然太大")
                
                return True, size_mb
            else:
                print("❌ 未找到生成的exe文件")
                return False, 0
        else:
            print("❌ 构建失败")
            print("错误输出:")
            print(result.stderr)
            return False, 0
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False, 0
    finally:
        # 切换回原目录
        os.chdir("..")

def build_minimal_version():
    """构建最小化版本"""
    print("\n🔨 尝试最小化版本...")
    
    os.chdir("mcu_code_analyzer")
    
    try:
        # 更激进的最小化命令
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=MCUCodeAnalyzer_v2.1.0_Minimal", 
            "--add-data=config.yaml;.",
            "--hidden-import=tkinter",
            "--hidden-import=yaml",
            "--exclude-module=PIL",
            "--exclude-module=matplotlib",
            "--exclude-module=numpy",
            "--exclude-module=pandas",
            "--exclude-module=scipy",
            "--exclude-module=requests.packages.urllib3.contrib.pyopenssl",
            "--exclude-module=requests.packages.urllib3.contrib.socks",
            "main_gui.py"
        ]
        
        print(f"执行最小化命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 最小化版本构建成功！")
            
            exe_path = Path("dist/MCUCodeAnalyzer_v2.1.0_Minimal.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 最小化exe: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
                
                return True, size_mb
            else:
                return False, 0
        else:
            print("❌ 最小化构建失败")
            print(result.stderr)
            return False, 0
            
    except Exception as e:
        print(f"❌ 最小化构建错误: {e}")
        return False, 0
    finally:
        os.chdir("..")

def analyze_size_factors():
    """分析文件大小因素"""
    print("\n🔍 分析文件大小因素...")
    
    # 检查Python版本影响
    version = sys.version_info
    if version.minor >= 11:
        estimated_python_overhead = 15
        print(f"  Python {version.major}.{version.minor} 基础开销: ~{estimated_python_overhead}MB")
    else:
        estimated_python_overhead = 8
        print(f"  Python {version.major}.{version.minor} 基础开销: ~{estimated_python_overhead}MB")
    
    # 检查依赖库
    try:
        import requests
        print(f"  requests库: ~10-15MB")
    except:
        pass
    
    try:
        import tkinter
        print(f"  tkinter库: ~8-12MB")
    except:
        pass
    
    try:
        import yaml
        print(f"  yaml库: ~2-3MB")
    except:
        pass
    
    estimated_total = estimated_python_overhead + 15 + 10 + 3
    print(f"  预估最小大小: ~{estimated_total}MB")
    
    if estimated_total > 35:
        print("💡 建议:")
        print("  1. 使用Python 3.8-3.10")
        print("  2. 移除requests，使用urllib")
        print("  3. 精简tkinter组件")

def create_comparison_report():
    """创建对比报告"""
    print("\n📊 构建结果对比:")
    
    results = []
    
    # 检查各个版本的文件
    versions = [
        ("原始版本", "dist/MCU_Code_Analyzer_v2.1.0.exe"),
        ("优化版本", "dist/MCU_Code_Analyzer_v2.1.0_30MB.exe"), 
        ("老命令版本", "mcu_code_analyzer/dist/MCUCodeAnalyzer_v2.1.0_True30MB.exe"),
        ("最小化版本", "mcu_code_analyzer/dist/MCUCodeAnalyzer_v2.1.0_Minimal.exe")
    ]
    
    for name, path in versions:
        file_path = Path(path)
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024 / 1024
            results.append((name, size_mb))
            print(f"  {name}: {size_mb:.1f} MB")
        else:
            print(f"  {name}: 未找到")
    
    if results:
        smallest = min(results, key=lambda x: x[1])
        print(f"\n🏆 最小版本: {smallest[0]} ({smallest[1]:.1f} MB)")
        
        if smallest[1] <= 35:
            print("🎯 ✅ 接近30MB目标！")
        else:
            print("🎯 ❌ 仍需优化")

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    check_python_version()
    
    # 清理旧文件
    print("\n🧹 清理构建目录...")
    cleanup_dirs = ["build", "dist", "mcu_code_analyzer/build", "mcu_code_analyzer/dist"]
    for dir_path in cleanup_dirs:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
            print(f"  ✅ 已清理: {dir_path}")
    
    # 分析大小因素
    analyze_size_factors()
    
    # 使用老版本命令构建
    success1, size1 = build_with_old_command()
    
    # 尝试最小化版本
    success2, size2 = build_minimal_version()
    
    # 创建对比报告
    create_comparison_report()
    
    # 总结
    print("\n" + "="*60)
    print("🎉 真正30MB构建测试完成！")
    print("="*60)
    
    if success1:
        print(f"✅ 老版本命令结果: {size1:.1f} MB")
    if success2:
        print(f"✅ 最小化版本结果: {size2:.1f} MB")
    
    print("\n💡 结论:")
    if success1 and size1 <= 35:
        print("🎯 老版本命令接近30MB目标！")
    elif success2 and size2 <= 35:
        print("🎯 最小化版本接近30MB目标！")
    else:
        print("🎯 可能需要更老的Python版本才能达到30MB")
        print("💡 主要原因: Python 3.13基础库比老版本大很多")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建过程中发生未知错误: {e}")
        sys.exit(1)
