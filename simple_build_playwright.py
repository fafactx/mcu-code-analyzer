"""
简化的Playwright版本构建脚本
假设依赖已安装，直接构建
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def create_simple_spec():
    """创建简化的PyInstaller配置"""
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
        ('mcu_code_analyzer/assets', 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'yaml',
        'requests',
        'chardet',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'playwright',
        'playwright.sync_api',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MCU_Code_Analyzer_Local',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('MCU_Code_Analyzer_Local.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 配置文件创建完成")


def build_simple():
    """简化构建"""
    print("🔨 开始构建...")
    
    try:
        # 创建配置
        create_simple_spec()
        
        # 构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "MCU_Code_Analyzer_Local.spec"]
        print(f"执行: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 构建成功！")
            
            exe_path = Path("dist/MCU_Code_Analyzer_Local.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"📁 文件: {exe_path}")
                print(f"📊 大小: {size_mb:.1f} MB")
                return True
            else:
                print("❌ 未找到exe文件")
                return False
        else:
            print("❌ 构建失败")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建异常: {e}")
        return False


if __name__ == "__main__":
    print("🚀 简化构建 - MCU代码分析器本地渲染版")
    print("=" * 40)
    
    if build_simple():
        print("\n🎉 构建完成！")
        print("🚀 可以运行: dist/MCU_Code_Analyzer_Local.exe")
    else:
        print("\n❌ 构建失败")
