#!/usr/bin/env python3
"""
MCU Code Analyzer v2.1.0 - 30MB目标构建脚本
基于老版本1.1的成功配置，目标文件大小30MB
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
║          MCU Code Analyzer v2.1.0 - 30MB目标构建             ║
║                                                              ║
║  🎯 基于老版本1.1成功配置                                     ║
║  📦 移除PIL等大型库                                           ║
║  ⚡ 目标文件大小: ~30MB                                       ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def create_30mb_spec():
    """创建30MB目标的PyInstaller配置文件"""
    print("📝 创建30MB目标配置文件...")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# 基于老版本1.1的成功配置，目标30MB

block_cipher = None

a = Analysis(
    ['mcu_code_analyzer/simple_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('mcu_code_analyzer/config.yaml', '.'),
        ('mcu_code_analyzer/localization.py', '.'),
        ('mcu_code_analyzer/templates', 'templates'),
        ('mcu_code_analyzer/utils', 'utils'),
        ('mcu_code_analyzer/core', 'core'),
        ('mcu_code_analyzer/intelligence', 'intelligence'),
        ('mcu_code_analyzer/ui', 'ui'),
    ],
    hiddenimports=[
        # 完全复制老版本的4个库
        'tkinter',
        'yaml',
        'requests',
        'chardet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除所有大型库 (关键!)
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'Pillow',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.patches',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'networkx',
        'numpy',
        'pandas',
        'scipy',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
        'cairosvg',
        'tksvg',
        'customtkinter',

        # 排除测试和开发工具
        'test',
        'tests',
        'testing',
        'unittest',
        'pytest',
        'jupyter',
        'IPython',
        'notebook',

        # 排除其他GUI框架
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'kivy',
        'pygame',
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
    name='MCU_Code_Analyzer_v2.1.0_30MB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 保持与老版本一致
    upx=False,    # 保持与老版本一致
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

    with open('MCU_Code_Analyzer_v2.1.0_30MB.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ 30MB目标配置文件已创建")

def check_image_dependencies():
    """检查并移除图像处理依赖"""
    print("🔍 检查图像处理依赖...")

    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    if not main_gui_file.exists():
        print("❌ main_gui.py文件不存在")
        return False

    # 读取文件内容
    with open(main_gui_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否有PIL导入
    if 'from PIL import' in content or 'import PIL' in content:
        print("⚠️  发现PIL导入，这会增加文件大小")
        print("💡 建议：移除图像处理功能以达到30MB目标")

        # 询问是否继续
        response = input("是否继续构建? (y/n): ")
        if response.lower() != 'y':
            return False

    print("✅ 依赖检查完成")
    return True

def build_30mb_exe():
    """构建30MB目标exe文件"""
    print("🔨 开始构建30MB目标exe文件...")

    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--log-level=WARN",
            "MCU_Code_Analyzer_v2.1.0_30MB.spec"
        ]

        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 构建中，请耐心等待...")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 30MB目标exe构建成功！")

            exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0_30MB.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")

                # 评估结果
                if size_mb <= 35:
                    print("🎯 ✅ 30MB目标达成！")
                elif size_mb <= 50:
                    print("🎯 ⚠️  接近目标，但仍可优化")
                else:
                    print("🎯 ❌ 超出目标，需要进一步优化")

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

def compare_with_old_version():
    """与老版本进行比较"""
    print("\n📊 与老版本比较:")

    new_exe = Path("dist/MCU_Code_Analyzer_v2.1.0_30MB.exe")
    old_exe = Path("dist/MCU_Code_Analyzer_v2.1.0.exe")

    if new_exe.exists():
        new_size = new_exe.stat().st_size / 1024 / 1024
        print(f"  30MB版本: {new_size:.1f} MB")

        if old_exe.exists():
            old_size = old_exe.stat().st_size / 1024 / 1024
            reduction = old_size - new_size
            reduction_percent = (reduction / old_size) * 100

            print(f"  原版本: {old_size:.1f} MB")
            print(f"  减少: {reduction:.1f} MB ({reduction_percent:.1f}%)")

            if new_size <= 35:
                print("✅ 30MB目标成功达成！")
            else:
                print("❌ 仍需进一步优化")
        else:
            print("  (无原版本对比)")

def create_30mb_release():
    """创建30MB版本发布包"""
    print("📦 创建30MB版本发布包...")

    exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0_30MB.exe")
    if not exe_path.exists():
        print("❌ 找不到30MB版本exe文件")
        return False

    # 创建发布目录
    release_dir = Path("MCU_Code_Analyzer_v2.1.0_30MB_Release")
    if release_dir.exists():
        shutil.rmtree(release_dir)

    release_dir.mkdir()

    # 复制exe文件 (重命名为标准名称)
    shutil.copy2(exe_path, release_dir / "MCU_Code_Analyzer_v2.1.0.exe")

    # 创建启动脚本
    start_script = release_dir / "启动 MCU Code Analyzer.bat"
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write('''@echo off
chcp 65001 >nul
title MCU Code Analyzer v2.1.0 (30MB优化版)
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                MCU Code Analyzer v2.1.0                     ║
echo ║                    (30MB优化版)                              ║
echo ║                                                              ║
echo ║  🚀 智能MCU代码分析器                                         ║
echo ║  📊 仅支持在线mermaid渲染                                     ║
echo ║  ⚡ 30MB超小体积版本                                          ║
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
        f.write('''MCU Code Analyzer v2.1.0 (30MB优化版) 使用说明
================================================

📋 版本信息:
  版本: v2.1.0 (30MB优化版)
  发布日期: 2025-06-16
  类型: 超小体积优化版本

🚀 快速开始:
  1. 双击 "启动 MCU Code Analyzer.bat" 启动程序
  2. 或直接运行 "MCU_Code_Analyzer_v2.1.0.exe"

✨ 优化特点:
  ⚡ 超小体积 (~30MB)
  ⚡ 启动极快
  ⚡ 移除所有图像处理库
  ⚡ 基于老版本1.1成功配置

🔧 功能说明:
  ✅ 在线mermaid渲染 (kroki.io + 备用API)
  ✅ 智能编码方式选择
  ✅ 网络诊断工具
  ✅ 备用API自动切换
  ❌ 不支持本地图像处理
  ❌ 不支持本地渲染

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

    print(f"✅ 30MB版本发布包已创建: {release_dir.absolute()}")
    return True

def main():
    """主函数"""
    print_banner()

    # 清理旧文件
    print("🧹 清理构建目录...")
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("MCU_Code_Analyzer_v2.1.0_30MB.spec").exists():
        Path("MCU_Code_Analyzer_v2.1.0_30MB.spec").unlink()

    # 检查图像依赖
    if not check_image_dependencies():
        print("\n❌ 依赖检查失败，构建终止")
        return False

    # 创建30MB配置
    create_30mb_spec()

    # 构建30MB exe
    if not build_30mb_exe():
        print("\n❌ 30MB构建失败")
        return False

    # 比较结果
    compare_with_old_version()

    # 创建发布包
    create_30mb_release()

    # 显示结果
    print("\n" + "="*60)
    print("🎉 MCU Code Analyzer v2.1.0 (30MB版) 构建完成！")
    print("="*60)

    exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0_30MB.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / 1024 / 1024
        print(f"📁 30MB版exe: {exe_path.absolute()}")
        print(f"📊 文件大小: {size_mb:.1f} MB")

        if size_mb <= 35:
            print("🎯 ✅ 30MB目标成功达成！")
        else:
            print("🎯 ❌ 仍超出30MB目标")

    print(f"📦 发布包: MCU_Code_Analyzer_v2.1.0_30MB_Release/")
    print("\n💡 优化措施:")
    print("  ✅ 移除PIL/Pillow图像处理库")
    print("  ✅ 精简hiddenimports列表")
    print("  ✅ 基于老版本1.1成功配置")
    print("  ✅ 排除所有大型科学计算库")

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
