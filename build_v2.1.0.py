#!/usr/bin/env python3
"""
MCU Code Analyzer v2.1.0 - exe构建脚本
基于原有build_exe.py，专门为v2.1.0版本构建
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
║              MCU Code Analyzer v2.1.0 - exe构建工具              ║
║                                                              ║
║  🚀 基于PyInstaller构建单文件exe                               ║
║  📦 包含所有依赖和资源文件                                      ║
║  ✨ 支持在线mermaid渲染和网络诊断                               ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_environment():
    """检查构建环境"""
    print("🔍 检查构建环境...")

    # 检查是否在正确目录
    if not Path("mcu_code_analyzer/main_gui.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        return False

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False

    print(f"✅ Python版本: {sys.version}")

    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller安装成功")
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

    return True

def clean_build_dirs():
    """清理构建目录"""
    print("🧹 清理构建目录...")

    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]

    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  ✅ 已清理: {dir_name}")

    # 清理spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"  ✅ 已清理: {spec_file}")

def create_spec_file():
    """创建PyInstaller配置文件"""
    print("📝 创建PyInstaller配置文件...")

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
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'yaml',
        'requests',
        'chardet',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'base64',
        'zlib',
        'urllib.parse',
        'json',
        'pathlib',
        'subprocess',
        'threading',
        'queue',
        'datetime',
        'time',
        'os',
        'sys',
        'io',
        'logging',
        'configparser',
        'collections',
        'itertools',
        'functools',
        're',
        'math',
        'statistics',
        'hashlib',
        'uuid',
        'tempfile',
        'shutil',
        'glob',
        'fnmatch',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除一些大型不必要的模块
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'test',
        'tests',
        'unittest',
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
    name='MCU_Code_Analyzer_v2.1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,   # 启用strip减小文件大小
    upx=False,    # 暂时不用UPX避免问题
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

    with open('MCU_Code_Analyzer_v2.1.0.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ 配置文件已创建: MCU_Code_Analyzer_v2.1.0.spec")

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")
    print("⏳ 这可能需要几分钟时间，请耐心等待...")

    try:
        # 使用spec文件构建
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "MCU_Code_Analyzer_v2.1.0.spec"
        ]

        print(f"执行命令: {' '.join(cmd)}")

        # 执行构建
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ exe文件构建成功！")

            # 检查输出文件
            exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
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

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")

    exe_path = Path("dist/MCU_Code_Analyzer_v2.1.0.exe")
    if not exe_path.exists():
        print("❌ 找不到exe文件")
        return False

    # 创建发布目录
    release_dir = Path("MCU_Code_Analyzer_v2.1.0_Release")
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
title MCU Code Analyzer v2.1.0
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                MCU Code Analyzer v2.1.0                     ║
echo ║                                                              ║
echo ║  🚀 智能MCU代码分析器                                         ║
echo ║  📊 支持在线mermaid渲染                                       ║
echo ║  🔧 内置网络诊断工具                                         ║
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
        f.write('''MCU Code Analyzer v2.1.0 使用说明
========================================

📋 版本信息:
  版本: v2.1.0
  发布日期: 2025-06-16
  类型: 功能增强版本

🚀 快速开始:
  1. 双击 "启动 MCU Code Analyzer.bat" 启动程序
  2. 或直接运行 "MCU_Code_Analyzer_v2.1.0.exe"

✨ 新功能:
  ✅ 多API在线mermaid渲染支持
  ✅ 智能编码方式选择
  ✅ 网络诊断工具集
  ✅ 备用API自动切换机制
  ✅ 修复mermaid语法兼容性问题

🔧 系统要求:
  - Windows 10 或更高版本
  - 建议内存: 512MB+
  - 在线功能需要互联网连接

📞 技术支持:
  如遇问题请检查:
  1. 网络连接是否正常
  2. 防火墙设置
  3. 杀毒软件是否误报

Copyright (c) 2025 MCU Code Analyzer Team
License: MIT
''')

    print(f"✅ 发布包已创建: {release_dir.absolute()}")
    return True

def copy_to_root():
    """复制exe到根目录"""
    print("📋 复制exe到根目录...")

    source_exe = Path("dist/MCU_Code_Analyzer_v2.1.0.exe")
    target_exe = Path("MCU_Code_Analyzer_v2.1.0.exe")

    if source_exe.exists():
        shutil.copy2(source_exe, target_exe)
        size_mb = target_exe.stat().st_size / 1024 / 1024
        print(f"✅ exe已复制到: {target_exe.absolute()}")
        print(f"📊 文件大小: {size_mb:.1f} MB")
        return True
    else:
        print("❌ 源exe文件不存在")
        return False

def main():
    """主函数"""
    print_banner()

    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，构建终止")
        return False

    # 清理旧文件
    clean_build_dirs()

    # 创建配置文件
    create_spec_file()

    # 构建exe
    if not build_exe():
        print("\n❌ exe构建失败")
        return False

    # 创建发布包
    if not create_release_package():
        print("\n❌ 发布包创建失败")
        return False

    # 复制到根目录
    copy_to_root()

    # 显示结果
    print("\n" + "="*60)
    print("🎉 MCU Code Analyzer v2.1.0 构建完成！")
    print("="*60)
    print("📁 输出文件:")
    print("  - dist/MCU_Code_Analyzer_v2.1.0.exe           (原始exe)")
    print("  - MCU_Code_Analyzer_v2.1.0_Release/           (发布包)")
    print("  - MCU_Code_Analyzer_v2.1.0.exe                (根目录副本)")
    print("\n🚀 使用方法:")
    print("  1. 进入 MCU_Code_Analyzer_v2.1.0_Release 目录")
    print("  2. 双击 '启动 MCU Code Analyzer.bat'")
    print("  3. 或直接运行 MCU_Code_Analyzer_v2.1.0.exe")
    print("\n✨ v2.1.0 新功能:")
    print("  ✅ 多API在线mermaid渲染")
    print("  ✅ 智能编码选择")
    print("  ✅ 网络诊断工具")
    print("  ✅ 备用API切换")
    print("\n🎊 构建成功！可以开始使用了！")

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
