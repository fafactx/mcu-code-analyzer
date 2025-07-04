@echo off
chcp 65001 >nul
title STM32工程分析器 v2.0 - 演示启动器

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    STM32工程分析器 v2.0                    ║
echo ║                                                              ║
echo ║  🚀 智能分析STM32项目，助力代码理解与平台迁移                      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 📋 启动选项:
echo 1. GUI模式 (图形界面)
echo 2. 演示模式 (功能演示)
echo 3. CLI帮助 (命令行帮助)
echo 4. 退出
echo.

set /p choice="请选择启动模式 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🖥️ 启动GUI模式...
    python main.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🎯 启动演示模式...
    python demo.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 📖 显示CLI帮助...
    python main.py --help
    echo.
    echo 示例命令:
    echo   python main.py --cli "C:\path\to\stm32\project"
    echo   python main.py --cli "C:\path\to\project" --output "C:\output"
    echo   python main.py --cli "C:\path\to\project" --no-llm
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 👋 感谢使用STM32工程分析器！
    goto end
)

echo.
echo ❌ 无效选择，请重新运行脚本
pause

:end
echo.
pause
