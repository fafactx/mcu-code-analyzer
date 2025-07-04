#!/usr/bin/env python3
"""
MCU Code Analyzer v3.0 修复版 - 构建脚本
修复PIL依赖问题，确保在线渲染正常工作
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def print_banner():
    """打印构建横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║           MCU Code Analyzer v3.0 修复版构建工具              ║
║                                                              ║
║  🔧 修复内容:                                                ║
║     • 添加PIL/Pillow支持在线渲染                             ║
║     • 保持DEBUG信息在Execution Log                           ║
║     • 优化依赖，仅包含必要的PIL功能                          ║
║     • 确保在线mermaid渲染正常工作                            ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def create_v3_fixed_spec():
    """创建v3.0修复版的PyInstaller配置文件"""
    print("📝 创建v3.0修复版配置文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# MCU Code Analyzer v3.0 修复版构建配置

block_cipher = None

a = Analysis(
    ['mcu_code_analyzer/main_gui.py'],
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
        # v3.0修复版 - 包含在线渲染必需的库
        'tkinter',
        'yaml',
        'requests', 
        'chardet',
        # 添加PIL支持在线渲染
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        # 网络和编码支持
        'urllib3',
        'base64',
        'io',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的大型库，但保留PIL
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
        'jupyter',
        'IPython',
        'notebook',
        'test',
        'tests',
        'testing',
        'unittest',
        'pytest',
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
    name='MCU_Code_Analyzer_v3.0_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,   # 保持优化
    upx=False,    # 保持稳定性
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
    
    with open('MCU_Code_Analyzer_v3.0_Fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ v3.0修复版配置文件已创建")

def build_v3_fixed_exe():
    """构建v3.0修复版exe文件"""
    print("🔨 开始构建v3.0修复版exe文件...")
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--log-level=WARN",
            "MCU_Code_Analyzer_v3.0_Fixed.spec"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 构建中，请耐心等待...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ v3.0修复版exe构建成功！")
            
            exe_path = Path("dist/MCU_Code_Analyzer_v3.0_Fixed.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
                
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

def create_v3_fixed_release():
    """创建v3.0修复版发布包"""
    print("📦 创建v3.0修复版发布包...")
    
    exe_path = Path("dist/MCU_Code_Analyzer_v3.0_Fixed.exe")
    if not exe_path.exists():
        print("❌ 找不到v3.0修复版exe文件")
        return False
    
    # 创建发布目录
    release_dir = Path("MCU_Code_Analyzer_v3.0_Fixed_Release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制exe文件 (使用标准名称)
    shutil.copy2(exe_path, release_dir / "MCU_Code_Analyzer_v3.0.exe")
    
    # 创建启动脚本
    start_script = release_dir / "启动 MCU Code Analyzer v3.0.bat"
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write('''@echo off
chcp 65001 >nul
title MCU Code Analyzer v3.0 (修复版)
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                MCU Code Analyzer v3.0 (修复版)               ║
║                                                              ║
echo ║  🚀 智能MCU代码分析器                                         ║
echo ║  🔧 DEBUG信息显示在Execution Log页面                         ║
echo ║  📊 在线mermaid渲染 (已修复PIL依赖)                           ║
echo ║  ⚡ 优化版本，功能完整                                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 正在启动v3.0修复版...
start "" "MCU_Code_Analyzer_v3.0.exe"
echo ✅ 程序已启动！
echo.
pause
''')
    
    # 创建修复说明文件
    readme = release_dir / "v3.0修复版说明.txt"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write(f'''MCU Code Analyzer v3.0 修复版说明
======================================

📋 版本信息:
  版本: v3.0 修复版
  发布日期: {datetime.now().strftime("%Y-%m-%d")}
  类型: 功能修复版本

🔧 修复内容:
  ✅ 修复PIL依赖缺失问题
     • 添加了PIL/Pillow库支持
     • 确保在线mermaid渲染正常工作
     • 修复"No module named 'PIL'"错误

  ✅ 保持v3.0所有特性
     • DEBUG信息显示在Execution Log页面
     • 纯在线mermaid渲染
     • 优化的文件大小
     • 更稳定的网络诊断

🚀 快速开始:
  1. 双击 "启动 MCU Code Analyzer v3.0.bat" 启动程序
  2. 或直接运行 "MCU_Code_Analyzer_v3.0.exe"

🔧 在线渲染功能:
  ✅ 现在可以正常使用在线mermaid渲染
  ✅ 支持kroki.io在线服务
  ✅ 自动备用API切换
  ✅ 图像处理功能完整

📊 文件大小说明:
  • 由于添加了PIL库，文件大小会比之前的66MB稍大
  • 但这是确保功能完整性的必要代价
  • 仍然比原始版本小很多

⚠️ 使用注意:
  • 需要网络连接才能使用在线渲染功能
  • 如遇网络问题，请检查防火墙设置
  • 查看Execution Log获取详细DEBUG信息

🔄 从v3.0升级:
  • 直接替换exe文件即可
  • 无需重新配置
  • 功能完全兼容

📞 技术支持:
  如遇问题请:
  1. 查看Execution Log中的DEBUG信息
  2. 检查网络连接
  3. 确认防火墙设置

Copyright (c) 2025 MCU Code Analyzer Team
License: MIT
Version: 3.0 (修复版)
''')
    
    print(f"✅ v3.0修复版发布包已创建: {release_dir.absolute()}")
    return True

def test_pil_availability():
    """测试PIL库是否可用"""
    print("🔍 测试PIL库可用性...")
    
    try:
        import PIL
        from PIL import Image, ImageTk
        print("✅ PIL库测试通过")
        print(f"  PIL版本: {PIL.__version__}")
        return True
    except ImportError as e:
        print(f"❌ PIL库不可用: {e}")
        print("💡 请安装Pillow: pip install Pillow")
        return False

def compare_versions():
    """版本对比"""
    print("\n📊 版本对比:")
    
    versions = [
        ("v3.0原版", "dist/MCU_Code_Analyzer_v3.0.exe"),
        ("v3.0修复版", "dist/MCU_Code_Analyzer_v3.0_Fixed.exe"),
    ]
    
    for name, path in versions:
        file_path = Path(path)
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024 / 1024
            print(f"  {name}: {size_mb:.1f} MB")
        else:
            print(f"  {name}: 未找到")

def main():
    """主函数"""
    print_banner()
    
    # 测试PIL可用性
    if not test_pil_availability():
        print("\n❌ PIL库不可用，无法构建修复版")
        print("💡 请先安装: pip install Pillow")
        return False
    
    # 清理旧文件
    print("\n🧹 清理构建目录...")
    cleanup_files = [
        "build", 
        "dist/MCU_Code_Analyzer_v3.0_Fixed.exe",
        "MCU_Code_Analyzer_v3.0_Fixed.spec"
    ]
    
    for item in cleanup_files:
        path = Path(item)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"  ✅ 已清理: {item}")
    
    # 检查入口文件
    main_gui_file = Path("mcu_code_analyzer/main_gui.py")
    if not main_gui_file.exists():
        print("❌ mcu_code_analyzer/main_gui.py 文件不存在")
        return False
    
    print(f"✅ 找到入口文件: {main_gui_file}")
    
    # 创建修复版配置
    create_v3_fixed_spec()
    
    # 构建修复版exe
    success, size = build_v3_fixed_exe()
    if not success:
        print("\n❌ v3.0修复版构建失败")
        return False
    
    # 创建发布包
    create_v3_fixed_release()
    
    # 版本对比
    compare_versions()
    
    # 显示结果
    print("\n" + "="*60)
    print("🎉 MCU Code Analyzer v3.0 修复版构建完成！")
    print("="*60)
    
    print(f"📁 修复版exe: dist/MCU_Code_Analyzer_v3.0_Fixed.exe")
    print(f"📊 文件大小: {size:.1f} MB")
    print(f"📦 发布包: MCU_Code_Analyzer_v3.0_Fixed_Release/")
    
    print("\n🔧 修复内容:")
    print("  ✅ 添加PIL/Pillow库支持")
    print("  ✅ 修复在线mermaid渲染功能")
    print("  ✅ 保持所有v3.0特性")
    print("  ✅ DEBUG信息仍显示在Execution Log")
    
    print("\n🚀 现在在线渲染功能应该可以正常工作了！")
    
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
