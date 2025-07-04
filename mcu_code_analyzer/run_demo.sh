#!/bin/bash

# STM32工程分析器 v2.0 - Linux/macOS启动脚本

clear

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    STM32工程分析器 v2.0                    ║"
echo "║                                                              ║"
echo "║  🚀 智能分析STM32项目，助力代码理解与平台迁移                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 启动选项:"
echo "1. GUI模式 (图形界面)"
echo "2. 演示模式 (功能演示)"
echo "3. CLI帮助 (命令行帮助)"
echo "4. 退出"
echo ""

read -p "请选择启动模式 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🖥️ 启动GUI模式..."
        python3 main.py
        ;;
    2)
        echo ""
        echo "🎯 启动演示模式..."
        python3 demo.py
        ;;
    3)
        echo ""
        echo "📖 显示CLI帮助..."
        python3 main.py --help
        echo ""
        echo "示例命令:"
        echo "  python3 main.py --cli \"/path/to/stm32/project\""
        echo "  python3 main.py --cli \"/path/to/project\" --output \"/output\""
        echo "  python3 main.py --cli \"/path/to/project\" --no-llm"
        ;;
    4)
        echo ""
        echo "👋 感谢使用STM32工程分析器！"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ 无效选择，请重新运行脚本"
        ;;
esac

echo ""
read -p "按回车键继续..."
