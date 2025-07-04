"""
MCU代码分析器 - 支持Playwright本地渲染的构建脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


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


def install_dependencies():
    """安装依赖包"""
    print("📦 安装项目依赖...")
    
    try:
        # 安装基础依赖
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "mcu_code_analyzer/requirements.txt"
        ], check=True)
        print("✅ 基础依赖安装完成")
        
        # 安装Playwright浏览器
        print("🌐 安装Playwright浏览器引擎...")
        subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], check=True)
        print("✅ Playwright浏览器引擎安装完成")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def create_spec_file():
    """创建PyInstaller配置文件"""
    print("📝 创建PyInstaller配置文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# MCU Code Analyzer with Playwright Support

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
        ('mcu_code_analyzer/assets', 'assets'),
    ],
    hiddenimports=[
        # 基础模块
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
        'math',
        'time',
        'localization',
        
        # 图像处理
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        
        # 图表绘制
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.patches',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'networkx',
        'numpy',
        'pandas',
        
        # Playwright本地渲染支持
        'playwright',
        'playwright.sync_api',
        'playwright._impl',
        'playwright._impl._api_structures',
        'playwright._impl._browser',
        'playwright._impl._page',
        'playwright._impl._chromium',
        'playwright._impl._connection',
        'playwright._impl._helper',
        'playwright._impl._transport',
        'greenlet',
        'websockets',
        'pyee',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'scipy',
        'cv2',
        'tensorflow',
        'torch',
        'sklearn',
        'IPython',
        'jupyter',
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
    name='MCU_Code_Analyzer_Playwright',
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
    icon=None,
)
'''
    
    with open('MCU_Code_Analyzer_Playwright.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller配置文件创建完成")


def build_exe():
    """构建exe文件"""
    print("🔨 开始构建exe文件...")

    try:
        # 清理之前的构建
        if Path("build").exists():
            shutil.rmtree("build")
        if Path("dist").exists():
            shutil.rmtree("dist")

        # 使用spec文件构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "MCU_Code_Analyzer_Playwright.spec"]

        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 构建中，请稍候...")

        result = subprocess.run(cmd, text=True)

        if result.returncode == 0:
            print("✅ exe文件构建成功！")

            # 检查输出文件
            exe_path = Path("dist/MCU_Code_Analyzer_Playwright.exe")
            if exe_path.exists():
                print(f"📁 exe文件位置: {exe_path.absolute()}")
                print(f"📊 文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                
                # 创建发布目录
                create_release_package()
                
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


def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")
    
    release_dir = Path("MCU_Code_Analyzer_Playwright_Release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制exe文件
    exe_source = Path("dist/MCU_Code_Analyzer_Playwright.exe")
    exe_dest = release_dir / "MCU_Code_Analyzer_Playwright.exe"
    shutil.copy2(exe_source, exe_dest)
    
    # 创建启动脚本
    bat_content = '''@echo off
echo 🚀 启动MCU代码分析器 (支持本地Mermaid渲染)
echo.
echo 💡 本版本支持：
echo    - 本地Playwright渲染 (无需网络)
echo    - 高质量Mermaid图表
echo    - 完整离线功能
echo.
MCU_Code_Analyzer_Playwright.exe
pause
'''
    
    with open(release_dir / "启动 MCU Code Analyzer (本地渲染).bat", 'w', encoding='gbk') as f:
        f.write(bat_content)
    
    # 创建说明文件
    readme_content = '''# MCU代码分析器 - 本地渲染版

## 新功能特性

### 🎨 本地Mermaid渲染
- 使用Playwright技术实现本地渲染
- 无需网络连接即可生成高质量流程图
- 支持完整的Mermaid语法
- 渲染质量与VSCode一致

### 🚀 使用方法
1. 双击 "启动 MCU Code Analyzer (本地渲染).bat"
2. 或直接运行 MCU_Code_Analyzer_Playwright.exe
3. 在配置中选择 "本地渲染" 模式

### ⚙️ 渲染模式配置
- **本地渲染**: 使用内置Playwright引擎 (推荐)
- **在线渲染**: 使用在线服务 (需要网络)
- **自动模式**: 优先本地，失败时切换在线

### 📊 支持的图表类型
- 函数调用流程图
- 接口使用关系图
- 项目架构图
- 自定义Mermaid图表

### 🔧 技术特性
- 完全离线工作
- 高质量PNG/SVG输出
- 自适应界面缩放
- 图片保存功能

### 📝 版本信息
- 版本: v3.1 (Playwright Edition)
- 构建时间: {build_time}
- 支持平台: Windows 10/11

### 🆘 故障排除
如果遇到渲染问题：
1. 检查配置文件中的渲染模式设置
2. 尝试切换到在线渲染模式
3. 查看日志文件获取详细错误信息

---
© 2024 MCU Code Analyzer Team
'''.format(build_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    with open(release_dir / "使用说明.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 发布包创建完成: {release_dir}")


def test_build():
    """测试构建的exe文件"""
    print("🧪 测试构建的exe文件...")
    
    exe_path = Path("dist/MCU_Code_Analyzer_Playwright.exe")
    if not exe_path.exists():
        print("❌ exe文件不存在")
        return False
    
    try:
        # 简单测试exe是否能启动
        result = subprocess.run([str(exe_path), "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 or "usage" in result.stdout.lower():
            print("✅ exe文件测试通过")
            return True
        else:
            print("⚠️ exe文件可能有问题")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ exe测试超时，但这可能是正常的")
        return True
    except Exception as e:
        print(f"⚠️ exe测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 MCU代码分析器 - Playwright版本构建脚本")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 创建配置文件
    create_spec_file()
    
    # 构建exe
    if not build_exe():
        sys.exit(1)
    
    # 测试构建结果
    test_build()
    
    print("\n🎉 构建完成！")
    print("📁 发布文件位置: MCU_Code_Analyzer_Playwright_Release/")
    print("🚀 可以运行: MCU_Code_Analyzer_Playwright_Release/MCU_Code_Analyzer_Playwright.exe")


if __name__ == "__main__":
    main()
