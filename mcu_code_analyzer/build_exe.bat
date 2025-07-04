@echo off
chcp 65001 >nul
title MCU代码分析器 - exe打包工具

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  MCU代码分析器 exe打包工具                   ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo 🔍 检查PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller安装失败
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller已准备就绪

echo.
echo 🔨 开始打包exe文件...
echo 这可能需要几分钟时间，请耐心等待...

pyinstaller --onefile --windowed --name="MCUCodeAnalyzer" --add-data="config.yaml;." --add-data="templates;templates" --hidden-import=tkinter --hidden-import=yaml --hidden-import=requests --hidden-import=chardet main.py

if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo.
echo ✅ 打包成功！
echo.
echo 📁 exe文件位置: dist\MCUCodeAnalyzer.exe
echo 📊 正在检查文件...

if exist "dist\MCUCodeAnalyzer.exe" (
    for %%I in ("dist\MCUCodeAnalyzer.exe") do echo 📊 文件大小: %%~zI 字节
    echo.
    echo 🚀 您可以直接运行: dist\MCUCodeAnalyzer.exe
    echo.
    echo 是否现在运行程序？ (y/n)
    set /p run_now=
    if /i "%run_now%"=="y" (
        echo 🚀 启动程序...
        start "" "dist\MCUCodeAnalyzer.exe"
    )
) else (
    echo ❌ 未找到生成的exe文件
)

echo.
pause
