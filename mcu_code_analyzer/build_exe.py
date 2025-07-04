"""
MCU代码分析器 - exe打包脚本
使用PyInstaller将Python项目打包为Windows可执行文件
"""

import os
import sys
import subprocess
import shutil
import yaml
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        print("正在安装PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

def create_spec_file():
    """创建PyInstaller配置文件"""
    version = get_version()
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('localization.py', '.'),
        ('templates', 'templates'),
        ('utils', 'utils'),
        ('core', 'core'),
        ('intelligence', 'intelligence'),
        ('ui', 'ui'),

    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.font',
        'customtkinter',
        'yaml',
        'pathlib',
        'threading',
        'json',
        'xml.etree.ElementTree',
        're',
        'collections',
        'dataclasses',
        'typing',
        'datetime',
        'tempfile',
        'webbrowser',
        'shutil',
        'subprocess',
        'os',
        'sys',
        'argparse',
        'requests',
        'urllib3',
        'encodings.utf_8',
        'encodings.cp1252',
        'encodings.ascii',
        'pkg_resources.py2_warn',
        'math',  # For loading spinner animation
        'time',  # For timing and delays
        'localization',  # Internationalization module
        'tksvg',  # SVG support for tkinter
        'PIL',  # Image processing
        'PIL.Image',
        'PIL.ImageTk',
        'cairosvg',  # SVG to PNG conversion
        'matplotlib',  # Graph plotting
        'matplotlib.pyplot',
        'matplotlib.patches',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'networkx',  # Graph analysis
        'numpy',  # Numerical computing
        'pandas',  # Data processing
        # Playwright本地渲染支持
        'playwright',
        'playwright.sync_api',
        'playwright._impl',
        'playwright._impl._api_structures',
        'playwright._impl._browser',
        'playwright._impl._page'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'scipy',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
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
    name='MCUCodeAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩，避免DLL问题
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # 可以添加图标文件路径
)
'''

    with open('MCUCodeAnalyzer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ 创建PyInstaller配置文件: MCUCodeAnalyzer.spec")

def clean_old_builds():
    """清理旧的构建文件和之前的版本"""
    print("🧹 清理旧的构建文件和之前版本...")

    # 清理构建目录
    cleanup_dirs = ["build", "dist", "MCUCodeAnalyzer_Portable"]
    cleanup_files = ["MCUCodeAnalyzer.spec"]

    for dir_name in cleanup_dirs:
        if Path(dir_name).exists():
            print(f"  删除目录: {dir_name}")
            try:
                shutil.rmtree(dir_name)
            except PermissionError as e:
                print(f"  ⚠️ 无法删除 {dir_name}: {e}")
                print(f"  💡 请手动删除该目录或关闭占用文件的程序")
            except Exception as e:
                print(f"  ❌ 删除 {dir_name} 时出错: {e}")

    for file_name in cleanup_files:
        if Path(file_name).exists():
            print(f"  删除文件: {file_name}")
            try:
                Path(file_name).unlink()
            except Exception as e:
                print(f"  ❌ 删除 {file_name} 时出错: {e}")

    # 清理之前版本的exe文件 (保留最近2个版本)
    parent_dir = Path("..")
    if parent_dir.exists():
        print("  清理旧版本exe文件 (保留最近2个版本)...")
        exe_files = list(parent_dir.glob("MCU_Code_Analyzer_v*.exe"))

        if len(exe_files) > 2:
            # 按修改时间排序，最新的在前
            exe_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 保留最新的2个，删除其余的
            files_to_delete = exe_files[2:]
            for exe_file in files_to_delete:
                try:
                    print(f"    删除旧版本: {exe_file.name}")
                    exe_file.unlink()
                except Exception as e:
                    print(f"    ⚠️ 无法删除 {exe_file.name}: {e}")

            if files_to_delete:
                print(f"    保留最新2个版本: {[f.name for f in exe_files[:2]]}")
        else:
            print("    当前版本数量 ≤ 2，无需清理")

    print("✅ 清理完成")

def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")

    try:
        # 使用spec文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "MCUCodeAnalyzer.spec"]

        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 构建中，请稍候...")

        # 使用实时输出，避免看起来卡住
        result = subprocess.run(cmd, text=True)

        if result.returncode == 0:
            print("✅ exe文件构建成功！")

            # 检查输出文件 (onefile模式)
            exe_path = Path("dist/MCUCodeAnalyzer.exe")
            if exe_path.exists():
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                return True
            else:
                print("❌ 未找到生成的exe文件")
                return False
        else:
            print("❌ 构建失败，请检查上面的错误信息")
            return False

    except KeyboardInterrupt:
        print("\n❌ 构建被用户中断")
        return False
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def create_portable_package():
    """创建便携版包"""
    print("📦 创建便携版包...")
    version = get_version()

    source_exe = Path("dist/MCUCodeAnalyzer.exe")
    if not source_exe.exists():
        print("❌ 找不到构建输出文件")
        return False

    # 创建便携版目录
    portable_dir = Path("MCUCodeAnalyzer_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir()

    # 复制exe文件
    shutil.copy2(source_exe, portable_dir / "MCUCodeAnalyzer.exe")

    # 创建启动脚本
    start_script = portable_dir / "Start MCU Code Analyzer.bat"
    with open(start_script, 'w', encoding='utf-8') as f:
        f.write(f'''@echo off
chcp 65001 >nul
title MCU Code Analyzer v{version}

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    MCU Code Analyzer v{version}                    ║
echo ║                                                              ║
echo ║  Professional MCU project analysis tool                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Starting application...

MCUCodeAnalyzer.exe

if errorlevel 1 (
    echo.
    echo Application failed to start, please check system environment
    pause
)
''')

    # 创建说明文件
    readme = portable_dir / "README.txt"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write(f'''MCU Code Analyzer v{version} - Portable Version

Usage:
1. Double-click "Start MCU Code Analyzer.bat" to launch
2. Or run "MCUCodeAnalyzer.exe" directly

Features:
- Support for STM32/NXP/Microchip/TI and other multi-vendor chip analysis
- Intelligent code structure analysis and interface recognition
- Support for Keil/CMake/Makefile and other project formats
- Optional LLM intelligent analysis functionality

System Requirements:
- Windows 10/11
- No Python environment installation required

Features:
- Online Mermaid rendering using kroki.io (no local dependencies required)
- All features work out of the box without additional installations

Technical Support:
- GitHub: https://github.com/fafactx/mcu-code-analyzer
- Documentation: README.md

Copyright:
Copyright (c) 2024 MCU Code Analyzer Team
License: MIT
''')



    print(f"✅ 便携版包创建完成: {portable_dir.absolute()}")
    return True

def create_fixed_location_exe():
    """创建固定位置的exe文件"""
    print("📦 创建固定位置exe文件...")

    try:
        version = get_version()
        source_exe = Path("dist/MCUCodeAnalyzer.exe")
        target_exe = Path(f"../MCU_Code_Analyzer_v{version}.exe")

        if source_exe.exists():
            # 复制exe到固定位置
            shutil.copy2(source_exe, target_exe)
            print(f"✅ exe文件已复制到: {target_exe.absolute()}")

            # 检查文件大小
            size_mb = target_exe.stat().st_size / 1024 / 1024
            print(f"📊 文件大小: {size_mb:.1f} MB")

            return True
        else:
            print("❌ 源exe文件不存在")
            return False

    except Exception as e:
        print(f"❌ 创建固定位置exe失败: {e}")
        return False

def get_version():
    """从config.yaml读取版本号"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('app', {}).get('version', '1.0.0')
    except:
        return '1.0.0'

def increment_version():
    """自动递增版本号"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        current_version = config.get('app', {}).get('version', '1.0.0')
        print(f"📋 当前版本: {current_version}")

        # 解析版本号 (major.minor.patch)
        parts = current_version.split('.')
        if len(parts) == 3:
            major, minor, patch = map(int, parts)
            patch += 1  # 递增补丁版本号
            new_version = f"{major}.{minor}.{patch}"
        else:
            # 如果格式不正确，默认递增
            new_version = "1.1.1"

        # 更新配置
        config['app']['version'] = new_version

        # 写回文件
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ 版本号已更新: {current_version} -> {new_version}")
        return new_version

    except Exception as e:
        print(f"❌ 版本号更新失败: {e}")
        return get_version()

def main():
    """主函数"""
    print(f"🚀 MCU Code Analyzer - exe build tool")
    print("=" * 50)

    # 检查当前目录
    if not Path("main_gui.py").exists():
        print("❌ Please run this script in the mcu_code_analyzer directory")
        return False

    # 自动递增版本号
    version = increment_version()

    # 清理旧的构建文件
    clean_old_builds()

    # 检查PyInstaller
    if not check_pyinstaller():
        return False

    # 创建配置文件
    create_spec_file()

    # 构建exe
    if not build_exe():
        return False

    # 创建便携版
    if not create_portable_package():
        return False

    # 创建固定位置的exe
    create_fixed_location_exe()

    print(f"\n🎉 Build completed! Version: {version}")
    print("\n📁 Output files:")
    print("  - dist/MCUCodeAnalyzer.exe                 (Single file executable)")
    print("  - MCUCodeAnalyzer_Portable/                (Portable package)")
    print(f"  - ../MCU_Code_Analyzer_v{version}.exe      (Fixed location)")
    print("\n🚀 How to run:")
    print("  1. Enter MCUCodeAnalyzer_Portable directory")
    print("  2. Double-click 'Start MCU Code Analyzer.bat'")
    print(f"  3. Or run MCU_Code_Analyzer_v{version}.exe directly")
    print(f"\n📋 Version updated: {version}")
    print("🔄 Previous versions have been cleaned up")
    print("✅ Using onefile mode to avoid DLL issues")

    return True

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
