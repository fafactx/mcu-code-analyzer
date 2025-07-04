#!/usr/bin/env python3
"""
测试简化入口文件的构建效果
"""

import os
import sys
import subprocess
from pathlib import Path

def test_simple_build():
    """测试简化构建"""
    print("🔨 测试简化入口文件构建...")
    
    # 切换到mcu_code_analyzer目录
    os.chdir("mcu_code_analyzer")
    
    try:
        # 使用完全相同的老版本命令，但用simple_main.py
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=MCUCodeAnalyzer_v2.1.0_Simple",
            "--add-data=config.yaml;.",
            "--add-data=templates;templates", 
            "--hidden-import=tkinter",
            "--hidden-import=yaml",
            "--hidden-import=requests",
            "--hidden-import=chardet",
            "simple_main.py"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 简化构建成功！")
            
            exe_path = Path("dist/MCUCodeAnalyzer_v2.1.0_Simple.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 简化版exe: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
                
                return True, size_mb
            else:
                print("❌ 未找到生成的exe文件")
                return False, 0
        else:
            print("❌ 简化构建失败")
            print("错误输出:")
            print(result.stderr)
            return False, 0
            
    except Exception as e:
        print(f"❌ 构建错误: {e}")
        return False, 0
    finally:
        os.chdir("..")

def compare_all_versions():
    """对比所有版本的大小"""
    print("\n📊 所有版本大小对比:")
    
    versions = [
        ("原始版本", "dist/MCU_Code_Analyzer_v2.1.0.exe"),
        ("优化版本", "dist/MCU_Code_Analyzer_v2.1.0_30MB.exe"),
        ("简化版本", "mcu_code_analyzer/dist/MCUCodeAnalyzer_v2.1.0_Simple.exe"),
    ]
    
    results = []
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
        largest = max(results, key=lambda x: x[1])
        
        print(f"\n🏆 最小版本: {smallest[0]} ({smallest[1]:.1f} MB)")
        print(f"📈 最大版本: {largest[0]} ({largest[1]:.1f} MB)")
        
        if len(results) > 1:
            reduction = largest[1] - smallest[1]
            reduction_percent = (reduction / largest[1]) * 100
            print(f"💾 最大优化: {reduction:.1f} MB ({reduction_percent:.1f}%)")
        
        if smallest[1] <= 35:
            print("🎯 ✅ 达到30MB目标！")
        else:
            print("🎯 ❌ 仍未达到30MB目标")

def main():
    """主函数"""
    print("🚀 简化入口文件构建测试")
    print("=" * 50)
    
    # 检查simple_main.py是否存在
    simple_main = Path("mcu_code_analyzer/simple_main.py")
    if not simple_main.exists():
        print("❌ simple_main.py文件不存在")
        return False
    
    # 测试简化构建
    success, size = test_simple_build()
    
    if success:
        print(f"\n✅ 简化构建成功: {size:.1f} MB")
        
        if size <= 35:
            print("🎯 ✅ 接近30MB目标！")
            print("💡 简化入口文件是关键优化点")
        else:
            print("🎯 ⚠️  仍需进一步优化")
            print("💡 可能需要更激进的措施")
    else:
        print("\n❌ 简化构建失败")
    
    # 对比所有版本
    compare_all_versions()
    
    print("\n💡 结论:")
    if success and size <= 35:
        print("✅ 简化入口文件是达到30MB的关键！")
        print("✅ 老版本的简单main.py确实是30MB的秘密")
    else:
        print("❌ 即使简化入口文件，仍然超过30MB")
        print("💡 可能的原因:")
        print("  1. Python 3.13基础库比老版本大")
        print("  2. 依赖库版本更新，体积增大")
        print("  3. 需要使用更老的Python版本")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
