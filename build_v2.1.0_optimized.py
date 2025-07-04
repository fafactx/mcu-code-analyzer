#!/usr/bin/env python3
"""
MCU Code Analyzer v2.1.0 - 优化的exe构建脚本
专门优化文件大小，目标：30MB左右
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
║          MCU Code Analyzer v2.1.0 - 优化构建工具              ║
║                                                              ║
║  🎯 目标文件大小: ~30MB                                       ║
║  ⚡ 优化打包配置                                              ║
║  🚀 仅包含必要依赖                                            ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def create_optimized_spec():
    """创建优化的PyInstaller配置文件"""
    print("📝 创建优化的PyInstaller配置文件...")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mcu_code_analyzer/main_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('mcu_code_analyzer/config.yaml', '.'),
        ('mcu_code_analyzer/templates', 'templates'),
        ('mcu_code_analyzer/utils', 'utils'),
        ('mcu_code_analyzer/core', 'core'),
        ('mcu_code_analyzer/intelligence', 'intelligence'),
        ('mcu_code_analyzer/ui', 'ui'),
        ('mcu_code_analyzer/localization.py', '.'),
    ],
    hiddenimports=[
        # 仅包含必要的模块
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'yaml',
        'requests',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的大型模块
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tensorflow',
        'torch',
        'cv2',
        'sklearn',
        'jupyter',
        'IPython',
        'notebook',
        'qtpy',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'kivy',
        'pygame',
        'selenium',
        'test',
        'tests',
        'testing',
        'unittest',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MCU_Code_Analyzer_v2.1.0_Optimized',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用strip减小文件大小
    upx=True,    # 启用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''

    with open('MCU_Code_Analyzer_v2.1.0_Optimized.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ 优化配置文件已创建")

def check_upx():
    """检查UPX是否可用"""
    try:
        result = subprocess.run(['upx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ UPX压缩工具可用")
            return True
        else:
            print("⚠️  UPX不可用，将跳过压缩")
            return False
    except FileNotFoundError:
        print("⚠️  UPX未安装，将跳过压缩")
        return False

def build_optimized_exe():
    """构建优化的exe文件"""
    print("🔨 开始构建优化的exe文件...")

    # 检查UPX
    upx_available = check_upx()

    try:
        # 构建命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--log-level=WARN",  # 减少日志输出
            "MCU_Code_Analyzer_v2.1.0_Optimized.spec"
        ]

        print(f"执行命令: {' '.join(cmd)}")

        # 执行构建
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 优化exe文件构建成功！")

            # 检查输出文件
            exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0_Optimized.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")

                # 与目标大小比较
                if size_mb <= 40:
                    print("🎯 ✅ 文件大小优化成功！")
                elif size_mb <= 60:
                    print("🎯 ⚠️  文件大小可接受，但仍可优化")
                else:
                    print("🎯 ❌ 文件大小仍然过大，需要进一步优化")

                return True
            else:
                print("❌ 未找到生成的exe文件")
                return False
        else:
            print("❌ 构建失败")
            print("错误输出:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def analyze_size_difference():
    """分析文件大小差异"""
    print("\n📊 文件大小分析:")

    original_exe = Path("dist/MCU_Code_Analyzer_v2.1.0.exe")
    optimized_exe = Path("dist/MCU_Code_Analyzer_v2.1.0_Optimized.exe")

    if original_exe.exists() and optimized_exe.exists():
        original_size = original_exe.stat().st_size / 1024 / 1024
        optimized_size = optimized_exe.stat().st_size / 1024 / 1024
        reduction = original_size - optimized_size
        reduction_percent = (reduction / original_size) * 100

        print(f"  原始版本: {original_size:.1f} MB")
        print(f"  优化版本: {optimized_size:.1f} MB")
        print(f"  减少大小: {reduction:.1f} MB ({reduction_percent:.1f}%)")

        if reduction > 0:
            print("✅ 优化成功！")
        else:
            print("❌ 优化失败，文件反而变大了")
    else:
        print("⚠️  无法比较，缺少文件")

def create_optimized_release():
    """创建优化版本的发布包"""
    print("📦 创建优化版本发布包...")

    exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0_Optimized.exe")
    if not exe_path.exists():
        print("❌ 找不到优化的exe文件")
        return False

    # 创建发布目录
    release_dir = Path("MCU_Code_Analyzer_v2.1.0_Optimized_Release")
    if release_dir.exists():
        shutil.rmtree(release_dir)

    release_dir.mkdir()

    # 复制exe文件
    shutil.copy2(exe_path, release_dir / "MCU_Code_Analyzer_v2.1.0.exe")

    # 创建启动脚本
    start_script = release_dir / "启动 MCU Code Analyzer.bat"
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write('''@echo off
chcp 65001 >nul
title MCU Code Analyzer v2.1.0 (优化版)
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                MCU Code Analyzer v2.1.0                     ║
echo ║                      (优化版本)                              ║
echo ║                                                              ║
echo ║  🚀 智能MCU代码分析器                                         ║
echo ║  📊 仅支持在线mermaid渲染                                     ║
echo ║  ⚡ 优化版本 - 更小更快                                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 正在启动程序...
start "" "MCU_Code_Analyzer_v2.1.0.exe"
echo ✅ 程序已启动！
echo.
pause
''')

    # 创建说明文件
    readme = release_dir / "使用说明.txt"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write('''MCU Code Analyzer v2.1.0 (优化版) 使用说明
=============================================

📋 版本信息:
  版本: v2.1.0 (优化版)
  发布日期: 2025-06-16
  类型: 功能增强 + 大小优化版本

🚀 快速开始:
  1. 双击 "启动 MCU Code Analyzer.bat" 启动程序
  2. 或直接运行 "MCU_Code_Analyzer_v2.1.0.exe"

✨ 优化特点:
  ⚡ 文件大小大幅减小 (目标30MB左右)
  ⚡ 启动速度更快
  ⚡ 仅包含必要依赖
  ⚡ 移除了所有本地渲染功能

🔧 功能说明:
  ✅ 在线mermaid渲染 (kroki.io + 备用API)
  ✅ 智能编码方式选择
  ✅ 网络诊断工具
  ✅ 备用API自动切换
  ❌ 不支持本地渲染 (已移除nodejs)

🔧 系统要求:
  - Windows 10 或更高版本
  - 建议内存: 256MB+
  - 在线功能需要互联网连接

📞 技术支持:
  如遇问题请检查:
  1. 网络连接是否正常
  2. 防火墙设置
  3. 杀毒软件是否误报

Copyright (c) 2025 MCU Code Analyzer Team
License: MIT
''')

    print(f"✅ 优化版发布包已创建: {release_dir.absolute()}")
    return True

def main():
    """主函数"""
    print_banner()

    # 清理旧文件
    print("🧹 清理构建目录...")
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("MCU_Code_Analyzer_v2.1.0_Optimized.spec").exists():
        Path("MCU_Code_Analyzer_v2.1.0_Optimized.spec").unlink()

    # 创建优化配置
    create_optimized_spec()

    # 构建优化exe
    if not build_optimized_exe():
        print("\n❌ 优化构建失败")
        return False

    # 分析大小差异
    analyze_size_difference()

    # 创建发布包
    create_optimized_release()

    # 显示结果
    print("\n" + "="*60)
    print("🎉 MCU Code Analyzer v2.1.0 优化构建完成！")
    print("="*60)

    optimized_exe = Path("dist/MCU_Code_Analyzer_v2.1.0_Optimized.exe")
    if optimized_exe.exists():
        size_mb = optimized_exe.stat().st_size / 1024 / 1024
        print(f"📁 优化版exe: {optimized_exe.absolute()}")
        print(f"📊 文件大小: {size_mb:.1f} MB")

        if size_mb <= 40:
            print("🎯 ✅ 大小优化目标达成！")
        else:
            print("🎯 ⚠️  仍需进一步优化")

    print(f"📦 发布包: MCU_Code_Analyzer_v2.1.0_Optimized_Release/")
    print("\n💡 优化措施:")
    print("  ✅ 移除了大型不必要模块")
    print("  ✅ 启用了strip和UPX压缩")
    print("  ✅ 精简了hiddenimports列表")
    print("  ✅ 添加了大量excludes排除项")

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
